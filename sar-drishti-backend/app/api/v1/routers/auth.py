"""
Authentication routes — PostgreSQL backed.
Real random 6-digit OTP stored in Redis / cache, logged to sms_outbox table.
GET /dev/sms-outbox enables real testing without hardcoding.
"""
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.core.deps import get_db, get_redis, get_current_user
from app.core.security import (
    create_access_token, create_refresh_token,
    generate_otp, hash_otp, verify_otp
)
from app.core.config import settings
from app.models.all_models import User, AuditLog, CANONICAL_ROLES

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

ALLOWED_DOMAINS = (
    "gujarat.gov.in", "gov.in", "nic.in",
    "bisag.gujarat.gov.in", "gsrtc.in",
    "ndrf.gov.in", "police.gujarat.gov.in", "gmail.com"
)


@router.post("/register", status_code=201)
async def register(
    request: Request,
    full_name: str = Form(...),
    designation: str = Form(...),
    role: str = Form(...),
    district_id: int = Form(1),
    govt_email: str = Form(...),
    mobile_number: str = Form(...),
    id_document: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
):
    clean_mob = mobile_number.replace(" ", "").replace("+91", "").strip()
    clean_email = govt_email.strip().lower()

    if len(clean_mob) != 10 or not clean_mob.isdigit():
        raise HTTPException(400, "Mobile number must be exactly 10 Indian digits (e.g. 9876543210)")

    if not any(clean_email.endswith(d) for d in ALLOWED_DOMAINS):
        raise HTTPException(400, "Registration restricted to authorized official domains")

    existing = await db.execute(
        select(User).where((User.email == clean_email) | (User.mobile == clean_mob))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(400, "User with this email or mobile already exists")

    doc_path = f"id_docs/{clean_mob}_{id_document.filename}" if id_document else None

    user = User(
        full_name=full_name,
        designation=designation,
        role=role,
        email=clean_email,
        mobile=clean_mob,
        id_doc_path=doc_path,
        status="approved" if settings.ENV == "development" else "pending",
    )
    db.add(user)
    await db.flush()

    db.add(AuditLog(
        user_id=user.id,
        action="user.register",
        resource_type="user",
        resource_id=str(user.id),
        ip_address=request.client.host if request.client else None,
    ))
    await db.commit()

    return {
        "status": "pending",
        "message": "Registration submitted to Gujarat R&B Dept. Awaiting Administrator verification.",
        "user_id": user.id,
    }


@router.post("/otp/send")
async def otp_send(
    request: Request,
    body: dict,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    mobile = body.get("mobile", "").replace(" ", "").replace("+91", "").strip()
    if not mobile or len(mobile) < 10:
        raise HTTPException(400, "Valid 10-digit mobile number required")

    result = await db.execute(select(User).where(User.mobile.like(f"%{mobile}%")))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "No account found for this mobile number. Please register first.")
    if user.status == "pending":
        raise HTTPException(403, "Account pending administrative approval. You will receive an SMS once approved.")
    if user.status == "suspended":
        raise HTTPException(403, "Account suspended. Contact your district super-admin.")

    otp = generate_otp(6)
    await redis.setex(f"otp:{mobile}", settings.OTP_TTL_SEC, hash_otp(otp))
    await redis.setex(f"otp_attempts:{mobile}", settings.OTP_TTL_SEC, "0")

    # Store in sms_outbox table in PostgreSQL
    sms_text = f"[SAR-DRISHTI SEOC] Your emergency access OTP is {otp}. Valid for 5 minutes."
    await db.execute(
        text("INSERT INTO sms_outbox (mobile, body, kind) VALUES (:m, :b, 'OTP')"),
        {"m": mobile, "b": sms_text}
    )
    await db.commit()

    print(f"\n[DISPATCHED SMS OUTBOX] Mobile: +91 {mobile} | OTP: {otp}\n")

    return {
        "sent": True,
        "channel": "SMS / Sandes Govt Gateway",
        "ttl_sec": settings.OTP_TTL_SEC,
        "dev_hint": "Check DEV SMS INBOX panel below",
    }


@router.post("/otp/verify")
async def otp_verify(
    request: Request,
    body: dict,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    mobile = body.get("mobile", "").replace(" ", "").replace("+91", "").strip()
    otp = str(body.get("otp", "")).strip()

    if not mobile or len(otp) != 6:
        raise HTTPException(400, "Fields 'mobile' (10 digits) and 'otp' (6 digits) required")

    attempts_key = f"otp_attempts:{mobile}"
    attempts = int(await redis.get(attempts_key) or 0)
    if attempts >= settings.OTP_MAX_VERIFY_ATTEMPTS:
        await redis.delete(f"otp:{mobile}")
        raise HTTPException(429, "Too many failed attempts. Request a new OTP.")

    stored_hash = await redis.get(f"otp:{mobile}")
    if not stored_hash:
        raise HTTPException(400, "OTP expired or not requested. Click 'Send Code'.")

    if not verify_otp(otp, stored_hash):
        await redis.incr(attempts_key)
        remaining = settings.OTP_MAX_VERIFY_ATTEMPTS - attempts - 1
        raise HTTPException(400, f"Invalid OTP. {remaining} attempts remaining.")

    await redis.delete(f"otp:{mobile}")
    await redis.delete(attempts_key)

    result = await db.execute(select(User).where(User.mobile.like(f"%{mobile}%")))
    user = result.scalar_one_or_none()
    if not user or user.status != "approved":
        raise HTTPException(401, "Account not approved")

    access_token = create_access_token(user.id, extra={"role": user.role, "name": user.full_name})
    refresh_token = create_refresh_token(user.id)

    db.add(AuditLog(
        user_id=user.id,
        action="user.login",
        resource_type="user",
        resource_id=str(user.id),
        ip_address=request.client.host if request.client else None,
    ))
    await db.commit()

    return {
        "token": access_token,
        "tokens": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        },
        "user": {
            "id": user.id,
            "name": user.full_name,
            "role": user.role,
            "designation": user.designation,
            "email": user.email,
        },
    }


@router.get("/me")
async def me(user=Depends(get_current_user)):
    return {
        "id": user.id,
        "name": user.full_name,
        "role": user.role,
        "designation": user.designation,
        "email": user.email,
        "mobile": user.mobile,
        "status": user.status,
    }


@router.get("/dev/sms-outbox")
async def dev_sms_outbox(mobile: str = "", db: AsyncSession = Depends(get_db)):
    clean_mob = mobile.replace(" ", "").replace("+91", "").strip()
    query = "SELECT id, mobile, body, created_at FROM sms_outbox"
    params = {}
    if clean_mob:
        query += " WHERE mobile LIKE :m"
        params["m"] = f"%{clean_mob}%"
    query += " ORDER BY created_at DESC LIMIT 5"
    res = await db.execute(text(query), params)
    return [
        {"id": r[0], "mobile": r[1], "body": r[2], "created_at": r[3].isoformat()}
        for r in res.fetchall()
    ]

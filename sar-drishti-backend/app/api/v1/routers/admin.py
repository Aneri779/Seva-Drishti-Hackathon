"""
Admin routes: user approval, config, scene refresh trigger.
All protected by require_role("admin").
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.core.deps import get_db, require_role
from app.models.all_models import User, AppConfig, AuditLog

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users")
async def list_pending_users(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("admin")),
):
    res = await db.execute(select(User).order_by(User.created_at.desc()))
    return [
        {
            "id": u.id,
            "name": u.full_name,
            "email": u.email,
            "mobile": u.mobile[-4:].rjust(10, "*"),  # mask mobile
            "role": u.role,
            "designation": u.designation,
            "status": u.status,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in res.scalars().all()
    ]


@router.patch("/users/{id}/approve")
async def approve_user(
    request: Request,
    id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_role("admin")),
):
    user = await db.get(User, id)
    if not user:
        raise HTTPException(404, f"User {id} not found")
    if user.status == "approved":
        raise HTTPException(400, "User already approved")
    
    user.status = "approved"
    user.approved_at = datetime.now(timezone.utc)
    user.approved_by = admin.id
    
    db.add(AuditLog(
        user_id=admin.id,
        action="user.approve",
        resource_type="user",
        resource_id=str(id),
        ip_address=request.client.host if request.client else None,
    ))
    await db.commit()
    return {"status": "approved", "user_id": id}


@router.get("/config")
async def get_config(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("admin")),
):
    """Read config from app_config table. Mask sensitive keys."""
    res = await db.execute(select(AppConfig))
    config = {row.key: row.value for row in res.scalars().all()}
    
    return {
        "gee_project": "***",  # never return project ID in API response
        "gee_service_account": "***@***.iam.gserviceaccount.com",  # masked
        "otsu_slope_max_deg": float(config.get("otsu_slope_max_deg", 5.0)),
        "otsu_hand_max_m": float(config.get("otsu_hand_max_m", 15.0)),
        "min_flood_area_ha": float(config.get("min_flood_area_ha", 1.0)),
        "jrc_occurrence_threshold": int(config.get("jrc_occurrence_threshold", 75)),
        "scene_refresh_interval_h": int(config.get("scene_refresh_interval_h", 3)),
        "gujarat_aoi_bbox": config.get("gujarat_aoi_bbox"),
        "sms_gateway": "configured",
        "whatsapp_gateway": "configured",
    }


@router.put("/config")
async def update_config(
    request: Request,
    body: dict,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("admin")),
):
    """Update pipeline thresholds in app_config table."""
    allowed_keys = {
        "otsu_slope_max_deg", "otsu_hand_max_m", "min_flood_area_ha",
        "jrc_occurrence_threshold", "scene_refresh_interval_h",
    }
    updated = []
    for key, value in body.items():
        if key not in allowed_keys:
            continue
        config_row = await db.get(AppConfig, key)
        if config_row:
            config_row.value = str(value)
            config_row.updated_by = user.id
        else:
            db.add(AppConfig(key=key, value=str(value), updated_by=user.id))
        updated.append(key)
    
    if not updated:
        raise HTTPException(400, f"No valid config keys. Allowed: {allowed_keys}")
    
    db.add(AuditLog(
        user_id=user.id,
        action="admin.config.update",
        detail={"updated_keys": updated, "values": {k: body[k] for k in updated}},
        ip_address=request.client.host if request.client else None,
    ))
    await db.commit()
    return {"updated": updated}


@router.post("/scenes/refresh")
async def trigger_scene_refresh(
    user=Depends(require_role("admin")),
):
    """Manually trigger scene_watcher Celery task."""
    try:
        from app.sar.pipeline import scene_watcher
        result = scene_watcher.delay()
        return {"task_id": result.id, "status": "queued"}
    except Exception as e:
        raise HTTPException(503, f"Celery not available: {e}")


@router.get("/meta/roles")
async def get_roles(user=Depends(require_role("admin"))):
    """Canonical roles — single source of truth."""
    from app.models.all_models import CANONICAL_ROLES
    ROLE_LABELS = {
        "rb_ee": "Roads & Buildings (R&B) Executive Engineer",
        "seoc_officer": "State Emergency Operation Centre (SEOC) Duty Officer",
        "collector": "District Collector / Magistrate Disaster Cell",
        "ndrf": "National Disaster Response Force (NDRF) Commander",
        "gsrtc": "GSRTC Central Route Controller",
        "bisag_gis": "BISAG-N Remote Sensing Geospatial Analyst",
        "admin": "System Administrator",
    }
    return [{"value": r, "label": ROLE_LABELS.get(r, r)} for r in CANONICAL_ROLES]


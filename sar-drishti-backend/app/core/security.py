"""
Security utilities: JWT, OTP, bcrypt.
No fixed/hardcoded OTPs. No dev bypass in OTP verification.
"""
import random
import hashlib
import hmac
from datetime import datetime, timezone, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── JWT ─────────────────────────────────────────────────────────

def create_access_token(user_id: int, extra: dict = None) -> str:
    payload = {
        "sub": str(user_id),
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TTL_MIN),
        "type": "access",
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TTL_DAYS),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Raises JWTError if invalid/expired."""
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])


# ── OTP ─────────────────────────────────────────────────────────

def generate_otp(length: int = 6) -> str:
    """Cryptographically-random OTP. Never fixed to any value."""
    return str(random.SystemRandom().randint(10 ** (length - 1), 10 ** length - 1))


def hash_otp(otp: str) -> str:
    """SHA-256 HMAC of OTP with JWT_SECRET as key for Redis storage."""
    return hmac.new(settings.JWT_SECRET.encode(), otp.encode(), hashlib.sha256).hexdigest()


def verify_otp(otp: str, stored_hash: str) -> bool:
    """Constant-time comparison."""
    expected = hash_otp(otp)
    return hmac.compare_digest(expected, stored_hash)


# ── Password (for admin seed only; users use OTP) ───────────────

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

"""
FastAPI dependencies: DB session, Redis, current user, require_role.
Every non-public route MUST use get_current_user or require_role.
"""
from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status, WebSocket
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.core.security import decode_token
from app.core.config import settings

# ── DB Session ───────────────────────────────────────────────────

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── In-Memory / Redis Mock Cache Fallback for Local Windows ──────
class LocalCache:
    def __init__(self):
        self._store = {}

    async def setex(self, key: str, ttl: int, val: str):
        self._store[key] = val

    async def get(self, key: str) -> Optional[str]:
        return self._store.get(key)

    async def delete(self, key: str):
        self._store.pop(key, None)

    async def incr(self, key: str) -> int:
        val = int(self._store.get(key, 0)) + 1
        self._store[key] = str(val)
        return val

    def pipeline(self):
        return self

    async def execute(self):
        return True

    def expire(self, key: str, ttl: int):
        pass


_local_cache = LocalCache()

async def get_redis():
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True, socket_connect_timeout=1)
        await r.ping()
        return r
    except Exception:
        return _local_cache


# ── Auth Bearer ──────────────────────────────────────────────────

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    from app.models.all_models import User
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or user.status != "approved":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or not approved",
        )
    return user


async def get_current_user_ws(token: str, db: AsyncSession) -> Optional[object]:
    from app.models.all_models import User
    try:
        payload = decode_token(token)
        user_id = int(payload["sub"])
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        return user if (user and user.status == "approved") else None
    except Exception:
        return None


def require_role(*roles: str):
    async def checker(user=Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role}' is not authorized. Required: {list(roles)}",
            )
        return user
    return checker


CurrentUser = Depends(get_current_user)

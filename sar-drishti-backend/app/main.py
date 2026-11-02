"""
SAR-Drishti FastAPI application.
/health — liveness (always fast, no external calls)
/health/deep — readiness (DB, PostGIS, Redis, MinIO, GEE, Celery, scene age)
Request logging middleware: one line per request.
CORS limited to configured origins only.
DEMO_MODE banner: if enabled, every response includes 'X-Demo-Mode: true' header.
"""
import logging
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1.routers import auth, scenes, stats, chainage, routing, notifications, bulletins, admin, dispatch, ws, meta

logging.basicConfig(
    level=logging.DEBUG if settings.is_dev else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: verify DB connection. Shutdown: cleanup."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"DEMO_MODE={settings.DEMO_MODE}, ENV={settings.ENV}")
    
    if settings.DEMO_MODE:
        logger.warning(
            "=== DEMO_MODE IS ENABLED. ALL DATA IS SYNTHETIC. ==="
            " Set DEMO_MODE=false for operational use."
        )
    
    # Verify DB connectivity at startup — fail hard if unreachable
    try:
        from app.db.session import engine
        from sqlalchemy import text
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database: connected")
    except Exception as e:
        logger.critical(f"Database connection FAILED at startup: {e}")
        raise SystemExit(f"Cannot start: database unreachable: {e}") from e
    
    # Initialize GEE
    try:
        from app.sar.gee_client import _init_gee
        _init_gee()
    except Exception as e:
        logger.error(f"GEE init failed at startup: {e}. Pipeline will fail on first use.")
    
    yield
    logger.info("Shutdown complete.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="SAR-Drishti: Sentinel-1 SAR flood monitoring for Gujarat R&B Dept",
    lifespan=lifespan,
    docs_url="/docs" if settings.is_dev else None,
    redoc_url="/redoc" if settings.is_dev else None,
)

# ── CORS — strictly configured, never "*" ────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-Request-ID", "X-Demo-Mode"],
)


# ── Request logging middleware ────────────────────────────────────
@app.middleware("http")
async def request_logger(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start = time.perf_counter()
    
    response = await call_next(request)
    
    ms = round((time.perf_counter() - start) * 1000, 1)
    user_id = getattr(request.state, "user_id", "-")
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} "
        f"user={user_id} status={response.status_code} {ms}ms"
    )
    response.headers["X-Request-ID"] = request_id
    
    if settings.DEMO_MODE:
        response.headers["X-Demo-Mode"] = "true"
    
    return response


# ── Demo mode banner on every JSON response ───────────────────────
@app.middleware("http")
async def demo_banner(request: Request, call_next):
    response = await call_next(request)
    return response


# ── Routers ──────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/v1")
app.include_router(scenes.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")
app.include_router(chainage.router, prefix="/api/v1")
app.include_router(routing.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(bulletins.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(dispatch.router, prefix="/api/v1")
app.include_router(meta.router, prefix="/api/v1")
app.include_router(ws.router)


# ── Health endpoints ──────────────────────────────────────────────

@app.get("/health", tags=["health"])
async def health():
    """Liveness probe — always returns quickly."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "demo_mode": settings.DEMO_MODE,
        "env": settings.ENV,
    }


@app.get("/health/deep", tags=["health"])
async def health_deep():
    """
    Readiness probe — checks all dependencies.
    Returns 503 if any required dependency is down.
    Required: DB, PostGIS, Redis. Optional: MinIO, GEE, Celery.
    """
    results = {}
    all_ok = True
    
    # ── DB ───────────────────────────────────────────────────────
    try:
        from app.db.session import engine
        from sqlalchemy import text
        async with engine.begin() as conn:
            pg_ver = (await conn.execute(text("SELECT version()"))).scalar()
            try:
                postgis_ver = (await conn.execute(text("SELECT PostGIS_Version()"))).scalar()
            except Exception:
                postgis_ver = "PostGIS not loaded (using native geometry logic)"
            results["db"] = {
                "status": "ok",
                "version": pg_ver[:50] if pg_ver else None,
                "postgis": postgis_ver,
            }
    except Exception as e:
        results["db"] = {"status": "error", "detail": str(e)}
        all_ok = False

    # ── Redis / Local Cache ──────────────────────────────────────
    try:
        from app.core.deps import get_redis
        redis = await get_redis()
        pong = True
        if hasattr(redis, "ping"):
            pong = await redis.ping()
        results["redis"] = {"status": "ok" if pong else "error"}
    except Exception as e:
        results["redis"] = {"status": "error", "detail": str(e)}

    # ── GEE ─────────────────────────────────────────────────────
    try:
        from app.sar.gee_client import check_gee_live
        results["gee"] = check_gee_live()
    except Exception as e:
        results["gee"] = {"status": "error", "detail": str(e)}
    
    # ── Celery worker ────────────────────────────────────────────
    try:
        from app.tasks.celery_app import celery_app
        inspect = celery_app.control.inspect(timeout=3)
        active = inspect.active()
        results["celery"] = {
            "status": "ok" if active else "no_workers",
            "workers": list(active.keys()) if active else [],
        }
    except Exception as e:
        results["celery"] = {"status": "error", "detail": str(e)}
    
    # ── Latest scene age ─────────────────────────────────────────
    try:
        from app.db.session import AsyncSessionLocal
        from app.models.all_models import SARScene
        from sqlalchemy import select
        async with AsyncSessionLocal() as db:
            sc = (await db.execute(
                select(SARScene).where(SARScene.status == "done")
                .order_by(SARScene.acquired_at.desc()).limit(1)
            )).scalar_one_or_none()
        if sc:
            now = datetime.now(timezone.utc)
            acq = sc.acquired_at
            if acq.tzinfo is None:
                acq = acq.replace(tzinfo=timezone.utc)
            age_h = round((now - acq).total_seconds() / 3600, 1)
            results["latest_scene"] = {
                "s1_id": sc.s1_id,
                "age_h": age_h,
                "status": sc.status,
                "note": "Sentinel-1 revisit is 6-12 days, not seconds",
            }
        else:
            results["latest_scene"] = {"status": "none", "note": "No processed scenes yet"}
    except Exception as e:
        results["latest_scene"] = {"status": "error", "detail": str(e)}
    
    status_code = 200 if all_ok else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ok" if all_ok else "degraded",
            "demo_mode": settings.DEMO_MODE,
            "checks": results,
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }
    )

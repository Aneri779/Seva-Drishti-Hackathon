"""
Scenes & telemetry routes — all data from DB only.
No synthetic histogram fallback. 404 if scene not processed.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.deps import get_db, get_current_user, require_role
from app.models.all_models import SARScene

router = APIRouter(prefix="/scenes", tags=["scenes"])


def _scene_age(acquired_at: datetime) -> str:
    """Human-readable data age. Never claims sub-minute freshness."""
    if not acquired_at:
        return "unknown"
    now = datetime.now(timezone.utc)
    if acquired_at.tzinfo is None:
        acquired_at = acquired_at.replace(tzinfo=timezone.utc)
    delta = now - acquired_at
    h = int(delta.total_seconds() // 3600)
    d = h // 24
    if d >= 2:
        return f"observed {d}d ago"
    elif h >= 1:
        return f"observed {h}h ago"
    else:
        m = int(delta.total_seconds() // 60)
        return f"observed {m}m ago"


def _scene_label(s: SARScene) -> str:
    """Real label from DB. No hardcoded '(Current)' string."""
    replay = f" [REPLAY: {s.replay_event_name}]" if s.is_replay else ""
    acq_str = s.acquired_at.strftime("%d %b %Y %H:%M IST") if s.acquired_at else "unknown"
    return f"Pass {s.rel_orbit} {s.pass_dir} - {acq_str}{replay}"


@router.get("")
async def list_scenes(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    res = await db.execute(select(SARScene).order_by(SARScene.acquired_at.desc()).limit(50))
    scenes = res.scalars().all()
    return [
        {
            "id": s.id,
            "label": _scene_label(s),
            "status": s.status,
            "s1_id": s.s1_id,
            "age": _scene_age(s.acquired_at),
            "flood_km2": s.flood_km2,
            "is_replay": s.is_replay,
        }
        for s in scenes
    ]


@router.get("/latest/telemetry")
async def latest_scene_telemetry(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    res = await db.execute(
        select(SARScene)
        .where(SARScene.status == "done")
        .order_by(SARScene.acquired_at.desc())
        .limit(1)
    )
    s = res.scalar_one_or_none()
    if not s:
        raise HTTPException(503, "No processed scene available. Pipeline may be initialising.")
    return _telemetry_dict(s)


@router.get("/{scene_id}/telemetry")
async def scene_telemetry(
    scene_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    res = await db.execute(select(SARScene).where(SARScene.id == scene_id))
    s = res.scalar_one_or_none()
    if not s:
        raise HTTPException(404, f"Scene {scene_id} not found")
    return _telemetry_dict(s)


@router.get("/{scene_id}/histogram")
async def scene_histogram(
    scene_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    """Returns histogram only if scene is processed. 404 otherwise. No synthetic fallback."""
    res = await db.execute(select(SARScene).where(SARScene.id == scene_id))
    s = res.scalar_one_or_none()
    if not s:
        raise HTTPException(404, f"Scene {scene_id} not found")
    if s.status != "done" or not s.histogram:
        raise HTTPException(404, "Histogram not available: scene not yet processed")
    # Return real histogram with real Otsu threshold
    return {
        "vv": s.histogram.get("vv"),
        "vh": s.histogram.get("vh"),
        "delta_vv": s.histogram.get("delta_vv"),
        "otsu_vv": s.otsu_vv,
        "otsu_vh": s.otsu_vh,
        "otsu_delta_vv": s.otsu_delta_vv,
        "speckle_filter": s.speckle_filter,
        "scene_id": scene_id,
    }


def _telemetry_dict(s: SARScene) -> dict:
    return {
        "s1_id": s.s1_id,
        "rel_orbit": s.rel_orbit,
        "pass_dir": s.pass_dir,
        "acquired_at": s.acquired_at.isoformat() if s.acquired_at else None,
        "age": _scene_age(s.acquired_at),
        "mean_sigma0_vv": s.mean_sigma0_vv,
        "mean_sigma0_vh": s.mean_sigma0_vh,
        "valid_pct": s.valid_pct,
        "flood_km2": s.flood_km2,
        "otsu_vv": s.otsu_vv,
        "otsu_vh": s.otsu_vh,
        "otsu_delta_vv": s.otsu_delta_vv,
        "speckle_filter": s.speckle_filter,
        "baseline_scene_id": s.baseline_scene_id,
        "status": s.status,
        "error_text": s.error_text if s.status == "failed" else None,
        "is_replay": s.is_replay,
        "replay_event_name": s.replay_event_name,
        "depth_note": "estimated (30 m DEM)" if s.flood_km2 else None,
        "polygon_count": s.polygon_count,
    }


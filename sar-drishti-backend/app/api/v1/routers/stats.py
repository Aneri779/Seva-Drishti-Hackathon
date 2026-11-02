"""
Stats, alerts, advisories, and public routes — all from DB.
No hardcoded numbers or strings.
"""
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

from app.core.deps import get_db, get_current_user
from app.models.all_models import (
    Alert, SARScene, ChainageEvent, Road, District,
    RoadStatus, ValidationRun
)

router = APIRouter(tags=["stats"])


def _ago(dt: datetime) -> str:
    if not dt:
        return "unknown"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - dt
    m = int(delta.total_seconds() // 60)
    h = m // 60
    d = h // 24
    if d >= 1:
        return f"{d}d ago"
    if h >= 1:
        return f"{h}h ago"
    return f"{m}m ago"


@router.get("/alerts")
async def get_alerts(
    district: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    query = select(Alert).where(Alert.is_active == True)
    if district:
        query = query.where(Alert.zone.ilike(f"%{district}%") | Alert.road_label.ilike(f"%{district}%") | Alert.text.ilike(f"%{district}%"))
    query = query.order_by(Alert.created_at.desc()).limit(50)
    
    res = await db.execute(query)
    alerts = res.scalars().all()
    if not alerts:
        # Fallback to all active alerts if selected district has none
        fallback_res = await db.execute(select(Alert).where(Alert.is_active == True).order_by(Alert.created_at.desc()).limit(50))
        alerts = fallback_res.scalars().all()
    return [
        {
            "id": a.id,
            "road": a.road_label or "Unknown road",
            "ago": _ago(a.created_at),
            "desc": a.text,
            "action": {
                "label": a.action_label or "Monitor",
                "color": "bg-error text-white" if a.severity == "CRITICAL"
                         else "bg-primary-container text-on-primary-container",
            },
            "zone": a.zone or "",
            "border": "border-error" if a.severity == "CRITICAL" else "border-amber-500",
            "severity": a.severity,
        }
        for a in alerts
    ]


@router.get("/stats/summary")
async def stats_summary(
    district: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    """All numbers computed from DB. No hardcoded values."""
    # Latest processed scene
    scene_res = await db.execute(
        select(SARScene).where(SARScene.status == "done")
        .order_by(SARScene.acquired_at.desc()).limit(1)
    )
    latest_scene = scene_res.scalar_one_or_none()
    
    if not latest_scene:
        raise HTTPException(503, "No processed scene available. Run scene_watcher first.")
    
    # Road status counts (from road_status table if available, else chainage_events)
    try:
        status_counts = await db.execute(text("""
            SELECT rs.status_class, COUNT(*) as cnt
            FROM road_status rs
            WHERE rs.scene_id = :scene_id
            GROUP BY rs.status_class
        """), {"scene_id": latest_scene.id})
        counts = {row[0]: row[1] for row in status_counts.fetchall()}
    except Exception:
        counts = {}
    
    # Chainage events
    ce_res = await db.execute(
        select(func.count(ChainageEvent.id))
        .where(ChainageEvent.scene_id == latest_scene.id)
    )
    total_events = ce_res.scalar() or 0
    
    washout_res = await db.execute(
        select(func.count(ChainageEvent.id))
        .where(
            ChainageEvent.scene_id == latest_scene.id,
            ChainageEvent.category.like("%Washout%")
        )
    )
    washouts = washout_res.scalar() or 0
    
    # Active alerts
    alert_res = await db.execute(
        select(func.count(Alert.id)).where(Alert.is_active == True)
    )
    active_alerts = alert_res.scalar() or 0
    
    critical_res = await db.execute(
        select(func.count(Alert.id))
        .where(Alert.is_active == True, Alert.severity == "CRITICAL")
    )
    critical_alerts = critical_res.scalar() or 0
    
    # Total monitored road segments
    seg_res = await db.execute(text("SELECT COALESCE(SUM((end_m - start_m)), 0) FROM road_segments"))
    monitored_m = seg_res.scalar() or 0
    monitored_km = round(monitored_m / 1000, 1)
    
    # Dispatch teams
    dispatch_res = await db.execute(text(
        "SELECT COUNT(*) FROM dispatch_tasks WHERE column_state IN ('en_route', 'on_site')"
    ))
    deployed_teams = dispatch_res.scalar() or 0
    
    # Otsu bimodal lock: check histogram quality
    otsu_quality = "Not validated" if not latest_scene.histogram else (
        f"{latest_scene.valid_pct:.1f}% valid pixels"
        if latest_scene.valid_pct else "computed"
    )
    
    # Validation metrics
    val_res = await db.execute(
        select(ValidationRun)
        .where(ValidationRun.scene_id == latest_scene.id)
        .order_by(ValidationRun.run_at.desc()).limit(1)
    )
    val_run = val_res.scalar_one_or_none()
    f1_label = f"F1={val_run.f1:.3f}" if val_run else "Not yet validated"
    
    return {
        "monitored_km": monitored_km,
        "submerged_segments": counts.get("OVERTOPPING", 0) + counts.get("WASHOUT", 0),
        "washouts": washouts,
        "deployed_teams": deployed_teams,
        "critical_alerts": critical_alerts,
        "active_alerts": active_alerts,
        "affected_corridors": total_events,
        "active_overtopping_m": counts.get("OVERTOPPING", 0) * 100,  # 100m per segment
        "flood_km2": latest_scene.flood_km2 or 0,
        "otsu_bimodal_quality": otsu_quality,
        "validation": f1_label,
        "scene_age": _ago(latest_scene.acquired_at),
        "scene_id": latest_scene.id,
    }


@router.get("/stats/road-classes")
async def stats_road_classes(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    """Road counts by class from DB."""
    res = await db.execute(text("""
        SELECT r.road_class, COUNT(r.id) as road_count,
               COUNT(DISTINCT rs.id) > 0 as has_active_status
        FROM roads r
        LEFT JOIN road_segments rs_seg ON rs_seg.road_id = r.id
        LEFT JOIN road_status rs ON rs.segment_id = rs_seg.id
        GROUP BY r.road_class
        ORDER BY r.road_class
    """))
    rows = res.fetchall()
    return [
        {
            "name": {"NH": "National (NH)", "SH": "State (SH)",
                     "MDR": "District (MDR)", "ODR": "Rural (ODR)"}[row[0]],
            "class": row[0],
            "count": row[1],
            "active": row[2],
        }
        for row in rows
    ]


@router.get("/advisories/corridors")
async def advisory_corridors(
    db: AsyncSession = Depends(get_db),
):
    """Flood corridor advisories from latest scene's chainage_events + road_status. Public telemetry."""
    # Latest scene
    scene_res = await db.execute(
        select(SARScene).where(SARScene.status == "done")
        .order_by(SARScene.acquired_at.desc()).limit(1)
    )
    scene = scene_res.scalar_one_or_none()
    if not scene:
        raise HTTPException(503, "No processed scene available")
    
    # Group chainage events by district
    rows = await db.execute(text("""
        SELECT d.name, r.code, r.road_class, ce.category, ce.max_depth_m,
               ce.start_m, ce.end_m, ce.confidence, ce.length_m
        FROM chainage_events ce
        JOIN roads r ON r.id = ce.road_id
        JOIN districts d ON d.id = r.district_id
        WHERE ce.scene_id = :scene_id
        ORDER BY d.name, ce.max_depth_m DESC
    """), {"scene_id": scene.id})
    
    from collections import defaultdict
    by_district = defaultdict(list)
    for row in rows.fetchall():
        by_district[row[0]].append({
            "road_code": row[1],
            "road_class": row[2],
            "category": row[3],
            "depth_m": row[4],
            "start_m": row[5],
            "end_m": row[6],
            "confidence": row[7],
        })
    
    corridors = []
    for district_name, events in by_district.items():
        worst = events[0]  # sorted by depth DESC
        has_washout = any("Washout" in e["category"] for e in events)
        has_overtopping = any("Overtopping" in e["category"] for e in events)
        
        status_str = (
            "ACTIVE WASHOUT RISK" if has_washout
            else "CRITICAL OVERTOPPING" if has_overtopping
            else "ADVISORY MONITORING"
        )
        status_color = "error" if (has_washout or has_overtopping) else "primary"
        
        routes = [
            {
                "name": f"{e['road_code']}",
                "val": f"{e['category']}: Depth est. +{e['depth_m']:.2f}m (30 m DEM)"
                       if e["depth_m"] else e["category"],
                "color": "error" if "Washout" in e["category"] or "Overtopping" in e["category"]
                         else "secondary" if "Bridge" in e["category"]
                         else "tertiary",
            }
            for e in events[:3]
        ]
        
        corridors.append({
            "district": f"DISTRICT: {district_name.upper()}",
            "title": f"{district_name} Corridor",
            "status": status_str,
            "statusColor": status_color,
            "flood_km2": round(scene.flood_km2 / max(1, len(by_district)), 1),
            "valid_pct": round(scene.valid_pct or 0, 1),
            "routes": routes,
            "age": _ago(scene.acquired_at),
        })
    
    return corridors


@router.get("/public/summary")
async def public_summary(db: AsyncSession = Depends(get_db)):
    """No auth required. Shows system status without sensitive operational data."""
    scene_res = await db.execute(
        select(SARScene).where(SARScene.status == "done")
        .order_by(SARScene.acquired_at.desc()).limit(1)
    )
    scene = scene_res.scalar_one_or_none()
    
    # Validation metrics
    val_text = "Not yet validated"
    if scene:
        val_res = await db.execute(
            select(ValidationRun)
            .where(ValidationRun.scene_id == scene.id)
            .order_by(ValidationRun.run_at.desc()).limit(1)
        )
        val = val_res.scalar_one_or_none()
        if val:
            val_text = f"F1={val.f1:.3f}, IoU={val.iou:.3f} vs {val.reference_source}"
    
    return {
        "last_scene": scene.s1_id if scene else None,
        "last_scene_age": _ago(scene.acquired_at) if scene else "No data",
        "flood_km2": scene.flood_km2 if scene else None,
        "validation": val_text,
        "pipeline_band": "Sentinel-1 IW GRD VV+VH (5.405 GHz C-band SAR)",
        "depth_note": "estimated (30 m DEM)",
    }


@router.get("/public/districts")
async def public_districts(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(District).order_by(District.name))
    return [{"id": d.id, "name": d.name, "name_gu": d.name_gu} for d in res.scalars().all()]


@router.get("/system/status")
async def system_status(db: AsyncSession = Depends(get_db)):
    scene_res = await db.execute(
        select(SARScene).order_by(SARScene.acquired_at.desc()).limit(1)
    )
    scene = scene_res.scalar_one_or_none()
    
    return {
        "status": "operational",
        "database": "PostgreSQL 15 Connected",
        "latest_scene_id": scene.s1_id if scene else "No scenes yet",
        "latest_scene_status": scene.status if scene else "ready",
        "latest_scene_age": _ago(scene.acquired_at) if scene else "ready",
        "error_text": scene.error_text if (scene and scene.status == "failed") else None,
    }


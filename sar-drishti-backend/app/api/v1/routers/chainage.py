"""
Chainage Registry routes — server-side filters, real data, CSV export.
"""
import csv
import io
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.core.deps import get_db, get_current_user
from app.models.all_models import ChainageEvent, Road, District, SARScene

router = APIRouter(prefix="/chainage-events", tags=["chainage"])


@router.get("")
async def get_chainage_events(
    district: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    road_class: Optional[str] = Query(None),
    scene_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Server-side filtered chainage events. All data from DB."""
    # Use latest scene if none specified
    if not scene_id:
        sc = await db.execute(
            select(SARScene.id).where(SARScene.status == "done")
            .order_by(SARScene.acquired_at.desc()).limit(1)
        )
        scene_id = sc.scalar_one_or_none()
    
    where_clauses = []
    params = {"limit": page_size, "offset": (page - 1) * page_size}
    if scene_id:
        where_clauses.append("ce.scene_id = :scene_id")
        params["scene_id"] = scene_id
    if district:
        where_clauses.append("d.name ILIKE :district_like")
        params["district_like"] = f"%{district}%"
    if category:
        where_clauses.append("ce.category ILIKE :category_like")
        params["category_like"] = f"%{category}%"
    if road_class:
        where_clauses.append("r.road_class = :road_class::road_class")
        params["road_class"] = road_class

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    query = text(f"""
        SELECT ce.id, ce.start_m, ce.end_m, ce.length_m, ce.category,
               ce.flank, ce.flooded_pct, ce.max_depth_m, ce.delta_db,
               ce.confidence, ce.created_at,
               r.code, r.name, r.road_class,
               d.name as district_name
        FROM chainage_events ce
        JOIN roads r ON r.id = ce.road_id
        JOIN districts d ON d.id = r.district_id
        {where_sql}
        ORDER BY ce.max_depth_m DESC NULLS LAST
        LIMIT :limit OFFSET :offset
    """)
    
    res = await db.execute(query, params)
    rows = res.fetchall()
    
    items = []
    for row in rows:
        (id_, start_m, end_m, length_m, cat, flank, flooded_pct, depth_m,
         delta_db, conf, created_at, code, name, road_class_, district_name) = row
        
        is_breach = "Washout" in (cat or "")
        is_sub = "Overtopping" in (cat or "")
        cat_color = "error" if is_breach else ("secondary" if is_sub else "tertiary")
        
        items.append({
            "id": code,
            "type": {"NH": "NAT HIGHWAY", "SH": "STATE HWY",
                     "MDR": "DIST ROAD", "ODR": "RURAL ROAD"}.get(road_class_, road_class_),
            "name": name,
            "dist": district_name,
            "block": f"{district_name} Taluka",
            "chainage": (
                f"KM {start_m // 1000}+{start_m % 1000:03d} → "
                f"KM {end_m // 1000}+{end_m % 1000:03d}"
            ) if start_m is not None else "N/A",
            "flank": flank or "Both Lanes",
            "len": f"{length_m:,} m" if length_m else "N/A",
            "cwPct": f"{int(flooded_pct or 0)}%",
            "depth": f"+{depth_m:.2f} m (estimated, 30 m DEM)" if depth_m else "N/A",
            "cat": cat,
            "catColor": cat_color,
            "pulse": is_breach,
            "conf": f"{(conf or 0) * 100:.1f}%",
            "db": f"Δ {delta_db:.1f} dB" if delta_db else "N/A",
        })
    
    return items


@router.get("/export.csv")
async def export_chainage_csv(
    district: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    token: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Real CSV export from DB. Supports ?token= query param for browser downloads."""
    from app.core.security import decode_access_token
    from app.models.all_models import User
    
    if token:
        payload = decode_access_token(token)
        if not payload:
            raise HTTPException(401, "Invalid token")
        user = await db.get(User, payload["sub"])
    else:
        user = None

    data = await get_chainage_events(
        district=district, category=category,
        page=1, page_size=10000, db=db, user=user
    )
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "id", "type", "name", "dist", "chainage", "flank",
        "len", "depth", "cat", "conf", "db"
    ])
    writer.writeheader()
    writer.writerows(data)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=chainage_events.csv"}
    )


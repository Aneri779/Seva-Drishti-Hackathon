"""
Dispatch tasks — field kanban with real field report submission.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db, get_current_user, require_role
from app.models.all_models import DispatchTask, ChainageEvent, Road, AuditLog

router = APIRouter(prefix="/dispatch-tasks", tags=["dispatch"])


@router.get("")
async def get_dispatch_tasks(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    res = await db.execute(
        select(
            DispatchTask.id,
            DispatchTask.machinery,
            DispatchTask.assignee,
            DispatchTask.column_state,
            DispatchTask.progress_pct,
            DispatchTask.verdict,
            ChainageEvent.start_m,
            ChainageEvent.category,
            ChainageEvent.max_depth_m,
            Road.code,
        )
        .join(ChainageEvent, DispatchTask.event_id == ChainageEvent.id)
        .join(Road, ChainageEvent.road_id == Road.id)
        .order_by(ChainageEvent.max_depth_m.desc())
    )
    tasks = []
    for row in res.all():
        (dt_id, machinery, assignee, column_state, progress_pct,
         verdict, start_m, cat, max_depth_m, r_code) = row
        # Map database enum (queued, en_route, on_site, resolved) to UI columns
        ui_state = {
            "queued": "hotspot",
            "en_route": "dispatched",
            "on_site": "dispatched",
            "resolved": "cleared",
        }.get(column_state, column_state)

        tasks.append({
            "id": dt_id,
            "road": f"{r_code} | KM {start_m // 1000}+{start_m % 1000:03d}",
            "cat": cat,
            "depth": f"+{max_depth_m:.2f}m (estimated, 30 m DEM)" if max_depth_m else "N/A",
            "machinery": machinery or "TBD",
            "assignee": assignee or "TBD",
            "column_state": ui_state,
            "raw_state": column_state,
            "progress_pct": progress_pct,
            "verdict": verdict,
        })
    return tasks


@router.patch("/{id}")
async def update_dispatch_task(
    request: Request,
    id: int,
    body: dict,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("rb_ee", "seoc_officer", "ndrf", "admin")),
):
    task = await db.get(DispatchTask, id)
    if not task:
        raise HTTPException(404, f"Task {id} not found")
    
    STATE_MAP = {
        "queued": "hotspot",
        "hotspot": "hotspot",
        "en_route": "dispatched",
        "on_site": "dispatched",
        "dispatched": "dispatched",
        "resolved": "cleared",
        "cleared": "cleared",
    }

    updated_fields = {}
    if "column_state" in body:
        val = body["column_state"]
        db_state = {"hotspot": "queued", "dispatched": "en_route", "cleared": "resolved"}.get(val, val)
        task.column_state = db_state
        updated_fields["column_state"] = db_state
    if "progress_pct" in body:
        task.progress_pct = min(100, max(0, int(body["progress_pct"])))
        updated_fields["progress_pct"] = task.progress_pct
    if "field_report" in body:
        import json
        rep = body["field_report"]
        task.field_report = json.dumps(rep) if isinstance(rep, dict) else str(rep)
        updated_fields["field_report"] = "submitted"
    if "verdict" in body:
        if body["verdict"] not in ("CONFIRMED", "INCORRECT", "PARTIAL"):
            raise HTTPException(400, "verdict must be CONFIRMED, INCORRECT, or PARTIAL")
        task.verdict = body["verdict"]
        task.verdict_submitted_at = datetime.now(timezone.utc)
        updated_fields["verdict"] = body["verdict"]
    
    if updated_fields:
        db.add(AuditLog(
            user_id=user.id,
            action="dispatch.update",
            resource_type="dispatch_task",
            resource_id=str(id),
            detail=updated_fields,
            ip_address=request.client.host if request.client else None,
        ))
    
    await db.commit()
    return {"status": "updated", "id": id, "updated": updated_fields}


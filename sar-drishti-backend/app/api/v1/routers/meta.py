"""
Public metadata routes for dropdowns and onboarding (districts, canonical roles).
No authentication required.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db
from app.models.all_models import District, CANONICAL_ROLES

router = APIRouter(prefix="/meta", tags=["metadata"])

ROLE_METADATA = [
    {"value": "rb_ee", "label": "Roads & Buildings (R&B) Executive Engineer"},
    {"value": "seoc_officer", "label": "State Emergency Operation Centre (SEOC) Duty Officer"},
    {"value": "collector", "label": "District Collector / Magistrate Disaster Cell"},
    {"value": "ndrf", "label": "National Disaster Response Force (NDRF Commander)"},
    {"value": "gsrtc", "label": "GSRTC Central Route Controller"},
    {"value": "bisag_gis", "label": "BISAG-N Remote Sensing Geospatial Analyst"},
    {"value": "admin", "label": "System Administrator"}
]


@router.get("/districts")
async def get_districts(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(District.id, District.name, District.name_gu, District.lgd_code).order_by(District.name))
    return [
        {"id": r[0], "name": r[1], "name_gu": r[2], "lgd_code": r[3]}
        for r in res.all()
    ]


@router.get("/roles")
async def get_roles():
    return ROLE_METADATA

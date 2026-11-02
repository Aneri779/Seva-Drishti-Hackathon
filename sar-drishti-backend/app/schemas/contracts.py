"""
Pydantic schemas mirroring exact frontend mock keys.
Enables 1-to-1 drop-in replacement with zero layout breaks.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any

# Auth
class RegisterRequest(BaseModel):
    full_name: str
    designation: str
    role: str
    district: str
    govt_email: EmailStr
    mobile_number: str

class OTPSendRequest(BaseModel):
    mobile: str

class OTPVerifyRequest(BaseModel):
    mobile: str
    otp: str

class UserProfile(BaseModel):
    id: int
    full_name: str
    designation: str
    role: str
    email: str
    mobile: str

# ChainageRegistry (Rows contract)
class ChainageRow(BaseModel):
    id: str  # e.g. "GJ-SH-25"
    type: str  # "STATE HWY"
    name: str  # "Porbandar – Dwarka Coastal Corridor"
    dist: str  # "Porbandar"
    block: str  # "Ranavav Taluka"
    chainage: str  # "KM 42+100 → KM 44+800"
    flank: str
    len: str  # "2,700 m"
    cwPct: str  # "92%"
    depth: str  # "+0.42 m Depth (estimated, 30 m DEM)"
    cat: str  # "Embankment Washout/Breach"
    catColor: str  # "error"
    pulse: bool
    conf: str  # "99.1%"
    db: str  # "Δ -22.4 dB (Specular Refl)"

# Dashboard Alerts contract
class AlertItem(BaseModel):
    id: int
    road: str  # "SH-25: Km 42.100 to 44.800"
    ago: str  # "12m ago"
    desc: str
    action: Dict[str, str]  # {"label": "...", "color": "..."}
    zone: str
    border: str

# Telemetry
class SceneTelemetry(BaseModel):
    s1_id: str
    rel_orbit: int
    pass_dir: str
    acquired_at: str
    mean_sigma0_vv: float
    valid_pct: float
    flood_km2: float
    otsu_vv: float
    otsu_vh: float
    speckle_filter: str
    status: str

# Route Plan
class RouteRequest(BaseModel):
    origin: str
    destination: str
    vehicle_profile: Optional[str] = "NDRF Boats Truck"
    clearance_m: Optional[float] = 0.90

class RouteCard(BaseModel):
    title: str
    via: str
    distance_km: float
    detour_min: int
    submergence_m: str
    clearance_status: str
    passable_pct: str
    is_safe: bool
    geojson: Dict[str, Any]


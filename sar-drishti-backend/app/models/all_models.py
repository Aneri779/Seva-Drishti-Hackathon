"""
All SQLAlchemy ORM models for SAR-Drishti.
Uses PostGIS geometry types via GeoAlchemy2.
No mock/demo data: all values come from real DB rows.
"""
from datetime import datetime, timezone
from typing import Optional
import json

from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Float, ForeignKey,
    Integer, String, Text, UniqueConstraint, Index, Enum as SAEnum,
    JSON, CheckConstraint, SmallInteger
)
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from app.db.session import Base


def utcnow():
    return datetime.now(timezone.utc)


# ── Canonical role list ──────────────────────────────────────────
# Single source of truth: used by DB CHECK, API /meta/roles, JWT, frontend
CANONICAL_ROLES = (
    "rb_ee",           # R&B Executive Engineer
    "seoc_officer",    # State Emergency Operation Centre Duty Officer
    "collector",       # District Collector Disaster Cell
    "ndrf",            # NDRF Commander
    "gsrtc",           # GSRTC Route Controller
    "bisag_gis",       # BISAG-N Geospatial Analyst
    "admin",           # System Administrator
)

RoleEnum = SAEnum(*CANONICAL_ROLES, name="user_role")
StatusEnum = SAEnum("pending", "approved", "suspended", name="user_status")
SceneStatusEnum = SAEnum("queued", "processing", "done", "failed", name="scene_status")
NotifStatusEnum = SAEnum("pending", "sent", "failed", name="notif_status")
BulletinStatusEnum = SAEnum("draft", "signed", "published", name="bulletin_status")
DeliveryStatusEnum = SAEnum("pending", "delivered", "read", "failed", name="delivery_status")
DispatchStateEnum = SAEnum("queued", "en_route", "on_site", "resolved", name="dispatch_state")
RoadClassEnum = SAEnum("NH", "SH", "MDR", "ODR", name="road_class")


# ── 1. Geography ─────────────────────────────────────────────────

class District(Base):
    __tablename__ = "districts"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    name_gu = Column(String(100))
    lgd_code = Column(String(10), unique=True)
    geom = Column(Geometry("MULTIPOLYGON", srid=4326))

    talukas = relationship("Taluka", back_populates="district")
    roads = relationship("Road", back_populates="district")


class Taluka(Base):
    __tablename__ = "talukas"
    id = Column(Integer, primary_key=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    name = Column(String(100), nullable=False)
    name_gu = Column(String(100))
    geom = Column(Geometry("MULTIPOLYGON", srid=4326))
    district = relationship("District", back_populates="talukas")


# ── 2. Road network ───────────────────────────────────────────────

class Road(Base):
    __tablename__ = "roads"
    id = Column(Integer, primary_key=True)
    district_id = Column(Integer, ForeignKey("districts.id"))
    code = Column(String(30), unique=True, nullable=False)      # e.g. "GJ-SH-25"
    name = Column(String(200), nullable=False)
    road_class = Column(RoadClassEnum, nullable=False)
    total_length_m = Column(Integer)
    geom = Column(Geometry("MULTILINESTRING", srid=4326))

    district = relationship("District", back_populates="roads")
    segments = relationship("RoadSegment", back_populates="road")


class RoadSegment(Base):
    """100-m road segments, derived by splitting road geometry."""
    __tablename__ = "road_segments"
    id = Column(BigInteger, primary_key=True)
    road_id = Column(Integer, ForeignKey("roads.id"), nullable=False)
    start_m = Column(Integer, nullable=False)     # metres from road start
    end_m = Column(Integer, nullable=False)
    crest_elev = Column(Float)                    # DEM sample (m ASL)
    chainage_source = Column(String(20), default="derived")  # 'derived' or 'official'
    geom = Column(Geometry("LINESTRING", srid=4326), nullable=False)

    road = relationship("Road", back_populates="segments")
    __table_args__ = (
        Index("ix_road_segments_geom", "geom", postgresql_using="gist"),
        Index("ix_road_segments_road_id", "road_id"),
    )


class RoadEdge(Base):
    """pgRouting topology edge."""
    __tablename__ = "road_edges"
    id = Column(BigInteger, primary_key=True)
    source = Column(Integer, nullable=False)
    target = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)          # length in metres
    reverse_cost = Column(Float, nullable=False)
    passable = Column(Boolean, default=True)
    road_id = Column(Integer, ForeignKey("roads.id"))
    segment_id = Column(BigInteger, ForeignKey("road_segments.id"))
    geom = Column(Geometry("LINESTRING", srid=4326))
    __table_args__ = (
        Index("ix_road_edges_geom", "geom", postgresql_using="gist"),
    )


class RoadNode(Base):
    """pgRouting topology node."""
    __tablename__ = "road_nodes"
    id = Column(Integer, primary_key=True)
    geom = Column(Geometry("POINT", srid=4326))
    __table_args__ = (
        Index("ix_road_nodes_geom", "geom", postgresql_using="gist"),
    )


# ── 3. SAR Scenes ─────────────────────────────────────────────────

class SARScene(Base):
    __tablename__ = "sar_scenes"
    id = Column(Integer, primary_key=True)
    s1_id = Column(String(100), unique=True, nullable=False)    # GEE system:index
    rel_orbit = Column(Integer, nullable=False)
    pass_dir = Column(String(20), nullable=False)               # ASCENDING/DESCENDING
    acquired_at = Column(DateTime(timezone=True), nullable=False)
    observed_at = Column(DateTime(timezone=True))               # when processed & stored
    status = Column(SceneStatusEnum, default="queued")
    error_text = Column(Text)                                   # if failed, exact error

    # Radiometry — only populated when status=done
    mean_sigma0_vv = Column(Float)
    mean_sigma0_vh = Column(Float)
    valid_pct = Column(Float)       # % non-nodata pixels
    flood_km2 = Column(Float)       # area of detected flood
    
    # Real Otsu thresholds from GEE histogram
    otsu_vv = Column(Float)
    otsu_vh = Column(Float)
    otsu_delta_vv = Column(Float)   # change image threshold
    
    # Full histogram JSONB: {vv: {bins: [...], counts: [...]}, vh: {...}, delta_vv: {...}}
    histogram = Column(JSON)
    
    # Processing metadata
    speckle_filter = Column(String(50))     # e.g. "Refined Lee 7x7"
    baseline_scene_id = Column(String(100)) # same orbit/pass dry-season reference
    cog_path = Column(String(500))          # MinIO path for COG
    polygon_count = Column(Integer)
    
    # REPLAY flag: set when manually triggered for a past event
    is_replay = Column(Boolean, default=False)
    replay_event_name = Column(String(200))  # e.g. "Cyclone Biparjoy Jun 2023"

    road_statuses = relationship("RoadStatus", back_populates="scene")
    flood_polygons = relationship("FloodPolygon", back_populates="scene")
    chainage_events = relationship("ChainageEvent", back_populates="scene")
    alerts = relationship("Alert", back_populates="scene")
    __table_args__ = (
        Index("ix_sar_scenes_acquired", "acquired_at"),
        Index("ix_sar_scenes_orbit", "rel_orbit", "pass_dir"),
    )


class FloodPolygon(Base):
    """Flood extent polygons derived from SAR processing."""
    __tablename__ = "flood_polygons"
    id = Column(BigInteger, primary_key=True)
    scene_id = Column(Integer, ForeignKey("sar_scenes.id"), nullable=False)
    geom = Column(Geometry("POLYGON", srid=4326), nullable=False)
    status_class = Column(String(30))    # FLOODED, PERMANENT_WATER, NO_DATA
    depth_m = Column(Float)             # estimated from DEM (30 m GLO-30)
    confidence = Column(Float)          # 0-1

    scene = relationship("SARScene", back_populates="flood_polygons")
    __table_args__ = (
        Index("ix_flood_polygons_geom", "geom", postgresql_using="gist"),
        Index("ix_flood_polygons_scene_id", "scene_id"),
    )


# ── 4. Road Status ───────────────────────────────────────────────

class RoadStatus(Base):
    """Per-scene per-segment road status from SAR intersection."""
    __tablename__ = "road_status"
    id = Column(BigInteger, primary_key=True)
    scene_id = Column(Integer, ForeignKey("sar_scenes.id"), nullable=False)
    segment_id = Column(BigInteger, ForeignKey("road_segments.id"), nullable=False)
    status_class = Column(String(40))   # CLEAR, ROADSIDE_WATER, OVERTOPPING, WASHOUT, NO_DATA
    max_depth_m = Column(Float)         # estimated depth in metres
    flooded_pct = Column(Float)         # % of segment flooded
    delta_vv_db = Column(Float)         # change in sigma0 VV (dB)
    delta_vh_db = Column(Float)
    confidence = Column(Float)
    processed_at = Column(DateTime(timezone=True), default=utcnow)

    scene = relationship("SARScene", back_populates="road_statuses")
    __table_args__ = (
        UniqueConstraint("scene_id", "segment_id", name="uq_road_status_scene_seg"),
        Index("ix_road_status_scene_id", "scene_id"),
        Index("ix_road_status_segment_id", "segment_id"),
    )


# ── 5. Chainage Events ───────────────────────────────────────────

class ChainageEvent(Base):
    """Contiguous flood/damage events per road (gaps-and-islands from road_status)."""
    __tablename__ = "chainage_events"
    id = Column(Integer, primary_key=True)
    scene_id = Column(Integer, ForeignKey("sar_scenes.id"))
    road_id = Column(Integer, ForeignKey("roads.id"), nullable=False)
    start_m = Column(Integer, nullable=False)
    end_m = Column(Integer, nullable=False)
    length_m = Column(Integer)
    category = Column(String(50))   # Washout, Overtopping, Bridge Abutment High-Risk, Roadside Water Only
    flank = Column(String(30))      # Both Lanes / Left Flank / Right Flank
    flooded_pct = Column(Float)
    max_depth_m = Column(Float)
    delta_db = Column(Float)
    confidence = Column(Float)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    scene = relationship("SARScene", back_populates="chainage_events")
    road = relationship("Road")
    dispatch_tasks = relationship("DispatchTask", back_populates="event")
    __table_args__ = (
        Index("ix_chainage_events_road_id", "road_id"),
        Index("ix_chainage_events_scene_id", "scene_id"),
        CheckConstraint("end_m > start_m", name="ck_chainage_order"),
    )


# ── 6. Users & Auth ──────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String(200), nullable=False)
    designation = Column(String(200))
    role = Column(RoleEnum, nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    mobile = Column(String(15), unique=True, nullable=False)
    id_doc_path = Column(String(500))       # MinIO path for uploaded govt ID
    status = Column(StatusEnum, default="pending")  # pending until admin approves
    created_at = Column(DateTime(timezone=True), default=utcnow)
    approved_at = Column(DateTime(timezone=True))
    approved_by = Column(Integer, ForeignKey("users.id"))

    notifications = relationship("Notification", back_populates="created_by_user")
    bulletins = relationship("Bulletin", foreign_keys="[Bulletin.created_by]", back_populates="created_by_user")
    __table_args__ = (
        Index("ix_users_mobile", "mobile"),
        Index("ix_users_email", "email"),
    )


# ── 7. Alerts ────────────────────────────────────────────────────

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True)
    scene_id = Column(Integer, ForeignKey("sar_scenes.id"))
    event_id = Column(Integer, ForeignKey("chainage_events.id"))
    severity = Column(String(20))       # CRITICAL, HIGH, MODERATE, LOW
    text = Column(Text, nullable=False)
    road_label = Column(String(200))
    zone = Column(String(100))
    action_label = Column(String(100))
    created_at = Column(DateTime(timezone=True), default=utcnow)
    is_active = Column(Boolean, default=True)

    scene = relationship("SARScene", back_populates="alerts")
    __table_args__ = (Index("ix_alerts_created_at", "created_at"),)


# ── 8. Notifications ─────────────────────────────────────────────

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    audience_json = Column(JSON)        # list of role/district filters
    body = Column(Text, nullable=False)
    channel = Column(String(30))        # SMS, WhatsApp, Sandes
    status = Column(NotifStatusEnum, default="pending")
    confirmed_at = Column(DateTime(timezone=True))  # human confirmation timestamp
    sent_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=utcnow)

    created_by_user = relationship("User", back_populates="notifications")
    deliveries = relationship("NotificationDelivery", back_populates="notification")


class NotificationDelivery(Base):
    """One row per recipient per notification."""
    __tablename__ = "notification_deliveries"
    id = Column(BigInteger, primary_key=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(DeliveryStatusEnum, default="pending")
    sent_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    gateway_ref = Column(String(100))   # external message ID

    notification = relationship("Notification", back_populates="deliveries")
    __table_args__ = (
        UniqueConstraint("notification_id", "user_id", name="uq_delivery_notif_user"),
    )


# ── 9. Bulletins ─────────────────────────────────────────────────

class Bulletin(Base):
    __tablename__ = "bulletins"
    id = Column(Integer, primary_key=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    scene_id = Column(Integer, ForeignKey("sar_scenes.id"))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(BulletinStatusEnum, default="draft")
    pdf_path = Column(String(500))          # MinIO path
    sha256 = Column(String(64))             # real SHA-256 of PDF bytes
    signed_by = Column(Integer, ForeignKey("users.id"))
    signed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=utcnow)
    size_bytes = Column(BigInteger)
    
    district = relationship("District")
    scene = relationship("SARScene")
    created_by_user = relationship("User", foreign_keys=[created_by], back_populates="bulletins")
    signed_by_user = relationship("User", foreign_keys=[signed_by])


# ── 10. Field Dispatch ───────────────────────────────────────────

class DispatchTask(Base):
    __tablename__ = "dispatch_tasks"
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("chainage_events.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    machinery = Column(String(200))
    assignee = Column(String(200))
    column_state = Column(DispatchStateEnum, default="queued")
    progress_pct = Column(SmallInteger, default=0)
    field_report = Column(Text)
    verdict = Column(String(20))    # CONFIRMED / INCORRECT / PARTIAL
    verdict_submitted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=utcnow)

    event = relationship("ChainageEvent", back_populates="dispatch_tasks")


# ── 11. App Config ───────────────────────────────────────────────

class AppConfig(Base):
    """Admin-editable pipeline thresholds stored in DB, read by pipeline."""
    __tablename__ = "app_config"
    key = Column(String(100), primary_key=True)
    value = Column(Text, nullable=False)
    description = Column(Text)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    updated_by = Column(Integer, ForeignKey("users.id"))


# ── 12. Audit Log ────────────────────────────────────────────────

class AuditLog(Base):
    """Every sensitive action must write a row here."""
    __tablename__ = "audit_log"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)   # e.g. "bulletin.sign", "notification.send"
    resource_type = Column(String(50))
    resource_id = Column(String(50))
    detail = Column(JSON)
    ip_address = Column(String(45))
    created_at = Column(DateTime(timezone=True), default=utcnow)
    __table_args__ = (Index("ix_audit_log_created_at", "created_at"),)


# ── 13. Validation Runs ──────────────────────────────────────────

class ValidationRun(Base):
    """Stores F1/IoU results from scripts/validate_event.py only."""
    __tablename__ = "validation_runs"
    id = Column(Integer, primary_key=True)
    scene_id = Column(Integer, ForeignKey("sar_scenes.id"), nullable=False)
    reference_source = Column(String(100))   # e.g. "Sentinel-2 MNDWI"
    reference_date = Column(DateTime(timezone=True))
    iou = Column(Float)
    f1 = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    notes = Column(Text)
    run_at = Column(DateTime(timezone=True), default=utcnow)
    run_by = Column(String(100))             # script user/path

    scene = relationship("SARScene")

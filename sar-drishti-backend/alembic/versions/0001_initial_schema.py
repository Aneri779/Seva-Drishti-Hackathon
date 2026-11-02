"""Initial schema - PostGIS extensions + pgRouting + all tables

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-11-02
"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2
from sqlalchemy.dialects import postgresql

revision = '0001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable PostGIS + pgRouting extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgrouting")
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")

    # ── Enums ────────────────────────────────────────────────────
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE user_role AS ENUM (
                'rb_ee','seoc_officer','collector','ndrf',
                'gsrtc','bisag_gis','admin'
            );
        EXCEPTION WHEN duplicate_object THEN NULL; END $$
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE user_status AS ENUM ('pending','approved','suspended');
        EXCEPTION WHEN duplicate_object THEN NULL; END $$
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE scene_status AS ENUM ('queued','processing','done','failed');
        EXCEPTION WHEN duplicate_object THEN NULL; END $$
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE notif_status AS ENUM ('pending','sent','failed');
        EXCEPTION WHEN duplicate_object THEN NULL; END $$
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE bulletin_status AS ENUM ('draft','signed','published');
        EXCEPTION WHEN duplicate_object THEN NULL; END $$
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE delivery_status AS ENUM ('pending','delivered','read','failed');
        EXCEPTION WHEN duplicate_object THEN NULL; END $$
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE dispatch_state AS ENUM ('queued','en_route','on_site','resolved');
        EXCEPTION WHEN duplicate_object THEN NULL; END $$
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE road_class AS ENUM ('NH','SH','MDR','ODR');
        EXCEPTION WHEN duplicate_object THEN NULL; END $$
    """)

    # ── Districts ────────────────────────────────────────────────
    op.create_table("districts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
        sa.Column("name_gu", sa.String(100)),
        sa.Column("lgd_code", sa.String(10), unique=True),
        sa.Column("geom", geoalchemy2.types.Geometry("MULTIPOLYGON", srid=4326)),
    )
    op.create_index("ix_districts_geom", "districts", ["geom"], postgresql_using="gist")

    # ── Talukas ──────────────────────────────────────────────────
    op.create_table("talukas",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("district_id", sa.Integer, sa.ForeignKey("districts.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("name_gu", sa.String(100)),
        sa.Column("geom", geoalchemy2.types.Geometry("MULTIPOLYGON", srid=4326)),
    )

    # ── Users ────────────────────────────────────────────────────
    op.create_table("users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("designation", sa.String(200)),
        sa.Column("role", sa.Enum(
            "rb_ee","seoc_officer","collector","ndrf",
            "gsrtc","bisag_gis","admin", name="user_role"), nullable=False),
        sa.Column("email", sa.String(200), unique=True, nullable=False),
        sa.Column("mobile", sa.String(15), unique=True, nullable=False),
        sa.Column("id_doc_path", sa.String(500)),
        sa.Column("status", sa.Enum("pending","approved","suspended", name="user_status"),
                  default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now()),
        sa.Column("approved_at", sa.DateTime(timezone=True)),
        sa.Column("approved_by", sa.Integer, sa.ForeignKey("users.id")),
    )
    op.create_index("ix_users_mobile", "users", ["mobile"])
    op.create_index("ix_users_email", "users", ["email"])

    # ── Roads ────────────────────────────────────────────────────
    op.create_table("roads",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("district_id", sa.Integer, sa.ForeignKey("districts.id")),
        sa.Column("code", sa.String(30), unique=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("road_class", sa.Enum("NH","SH","MDR","ODR", name="road_class"), nullable=False),
        sa.Column("total_length_m", sa.Integer),
        sa.Column("geom", geoalchemy2.types.Geometry("MULTILINESTRING", srid=4326)),
    )
    op.create_index("ix_roads_geom", "roads", ["geom"], postgresql_using="gist")

    # ── Road Segments ────────────────────────────────────────────
    op.create_table("road_segments",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("road_id", sa.Integer, sa.ForeignKey("roads.id"), nullable=False),
        sa.Column("start_m", sa.Integer, nullable=False),
        sa.Column("end_m", sa.Integer, nullable=False),
        sa.Column("crest_elev", sa.Float),
        sa.Column("chainage_source", sa.String(20), default="derived"),
        sa.Column("geom", geoalchemy2.types.Geometry("LINESTRING", srid=4326), nullable=False),
    )
    op.create_index("ix_road_segments_geom", "road_segments", ["geom"], postgresql_using="gist")
    op.create_index("ix_road_segments_road_id", "road_segments", ["road_id"])

    # ── Road Nodes (pgRouting) ───────────────────────────────────
    op.create_table("road_nodes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("geom", geoalchemy2.types.Geometry("POINT", srid=4326)),
    )
    op.create_index("ix_road_nodes_geom", "road_nodes", ["geom"], postgresql_using="gist")

    # ── Road Edges (pgRouting) ───────────────────────────────────
    op.create_table("road_edges",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("source", sa.Integer, nullable=False),
        sa.Column("target", sa.Integer, nullable=False),
        sa.Column("cost", sa.Float, nullable=False),
        sa.Column("reverse_cost", sa.Float, nullable=False),
        sa.Column("passable", sa.Boolean, default=True),
        sa.Column("road_id", sa.Integer, sa.ForeignKey("roads.id")),
        sa.Column("segment_id", sa.BigInteger, sa.ForeignKey("road_segments.id")),
        sa.Column("geom", geoalchemy2.types.Geometry("LINESTRING", srid=4326)),
    )
    op.create_index("ix_road_edges_geom", "road_edges", ["geom"], postgresql_using="gist")

    # ── SAR Scenes ────────────────────────────────────────────────
    op.create_table("sar_scenes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("s1_id", sa.String(100), unique=True, nullable=False),
        sa.Column("rel_orbit", sa.Integer, nullable=False),
        sa.Column("pass_dir", sa.String(20), nullable=False),
        sa.Column("acquired_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True)),
        sa.Column("status", sa.Enum("queued","processing","done","failed", name="scene_status"),
                  default="queued"),
        sa.Column("error_text", sa.Text),
        sa.Column("mean_sigma0_vv", sa.Float),
        sa.Column("mean_sigma0_vh", sa.Float),
        sa.Column("valid_pct", sa.Float),
        sa.Column("flood_km2", sa.Float),
        sa.Column("otsu_vv", sa.Float),
        sa.Column("otsu_vh", sa.Float),
        sa.Column("otsu_delta_vv", sa.Float),
        sa.Column("histogram", postgresql.JSONB),
        sa.Column("speckle_filter", sa.String(50)),
        sa.Column("baseline_scene_id", sa.String(100)),
        sa.Column("cog_path", sa.String(500)),
        sa.Column("polygon_count", sa.Integer),
        sa.Column("is_replay", sa.Boolean, default=False),
        sa.Column("replay_event_name", sa.String(200)),
    )
    op.create_index("ix_sar_scenes_acquired", "sar_scenes", ["acquired_at"])
    op.create_index("ix_sar_scenes_orbit", "sar_scenes", ["rel_orbit", "pass_dir"])

    # ── Flood Polygons ───────────────────────────────────────────
    op.create_table("flood_polygons",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("scene_id", sa.Integer, sa.ForeignKey("sar_scenes.id"), nullable=False),
        sa.Column("geom", geoalchemy2.types.Geometry("POLYGON", srid=4326), nullable=False),
        sa.Column("status_class", sa.String(30)),
        sa.Column("depth_m", sa.Float),
        sa.Column("confidence", sa.Float),
    )
    op.create_index("ix_flood_polygons_geom", "flood_polygons", ["geom"], postgresql_using="gist")
    op.create_index("ix_flood_polygons_scene_id", "flood_polygons", ["scene_id"])

    # ── Road Status ───────────────────────────────────────────────
    op.create_table("road_status",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("scene_id", sa.Integer, sa.ForeignKey("sar_scenes.id"), nullable=False),
        sa.Column("segment_id", sa.BigInteger, sa.ForeignKey("road_segments.id"), nullable=False),
        sa.Column("status_class", sa.String(40)),
        sa.Column("max_depth_m", sa.Float),
        sa.Column("flooded_pct", sa.Float),
        sa.Column("delta_vv_db", sa.Float),
        sa.Column("delta_vh_db", sa.Float),
        sa.Column("confidence", sa.Float),
        sa.Column("processed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("scene_id", "segment_id", name="uq_road_status_scene_seg"),
    )
    op.create_index("ix_road_status_scene_id", "road_status", ["scene_id"])
    op.create_index("ix_road_status_segment_id", "road_status", ["segment_id"])

    # ── Road Status Latest View ──────────────────────────────────
    op.execute("""
        CREATE VIEW road_status_latest AS
        SELECT DISTINCT ON (rs.segment_id)
            rs.*,
            seg.geom,
            r.code AS road_code,
            r.road_class
        FROM road_status rs
        JOIN road_segments seg ON seg.id = rs.segment_id
        JOIN roads r ON r.id = seg.road_id
        JOIN sar_scenes sc ON sc.id = rs.scene_id
        WHERE sc.status = 'done'
        ORDER BY rs.segment_id, sc.acquired_at DESC
    """)

    # ── Chainage Events ──────────────────────────────────────────
    op.create_table("chainage_events",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("scene_id", sa.Integer, sa.ForeignKey("sar_scenes.id")),
        sa.Column("road_id", sa.Integer, sa.ForeignKey("roads.id"), nullable=False),
        sa.Column("start_m", sa.Integer, nullable=False),
        sa.Column("end_m", sa.Integer, nullable=False),
        sa.Column("length_m", sa.Integer),
        sa.Column("category", sa.String(50)),
        sa.Column("flank", sa.String(30)),
        sa.Column("flooded_pct", sa.Float),
        sa.Column("max_depth_m", sa.Float),
        sa.Column("delta_db", sa.Float),
        sa.Column("confidence", sa.Float),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("end_m > start_m", name="ck_chainage_order"),
    )
    op.create_index("ix_chainage_events_road_id", "chainage_events", ["road_id"])
    op.create_index("ix_chainage_events_scene_id", "chainage_events", ["scene_id"])

    # ── Alerts ───────────────────────────────────────────────────
    op.create_table("alerts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("scene_id", sa.Integer, sa.ForeignKey("sar_scenes.id")),
        sa.Column("event_id", sa.Integer, sa.ForeignKey("chainage_events.id")),
        sa.Column("severity", sa.String(20)),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("road_label", sa.String(200)),
        sa.Column("zone", sa.String(100)),
        sa.Column("action_label", sa.String(100)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("is_active", sa.Boolean, default=True),
    )
    op.create_index("ix_alerts_created_at", "alerts", ["created_at"])

    # ── Notifications ─────────────────────────────────────────────
    op.create_table("notifications",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("created_by", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("audience_json", postgresql.JSONB),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("channel", sa.String(30)),
        sa.Column("status", sa.Enum("pending","sent","failed", name="notif_status"),
                  default="pending"),
        sa.Column("confirmed_at", sa.DateTime(timezone=True)),
        sa.Column("sent_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── Notification Deliveries ───────────────────────────────────
    op.create_table("notification_deliveries",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("notification_id", sa.Integer, sa.ForeignKey("notifications.id"), nullable=False),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.Enum("pending","delivered","read","failed", name="delivery_status"),
                  default="pending"),
        sa.Column("sent_at", sa.DateTime(timezone=True)),
        sa.Column("delivered_at", sa.DateTime(timezone=True)),
        sa.Column("read_at", sa.DateTime(timezone=True)),
        sa.Column("gateway_ref", sa.String(100)),
        sa.UniqueConstraint("notification_id", "user_id", name="uq_delivery_notif_user"),
    )

    # ── Bulletins ─────────────────────────────────────────────────
    op.create_table("bulletins",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("district_id", sa.Integer, sa.ForeignKey("districts.id"), nullable=False),
        sa.Column("scene_id", sa.Integer, sa.ForeignKey("sar_scenes.id")),
        sa.Column("created_by", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.Enum("draft","signed","published", name="bulletin_status"),
                  default="draft"),
        sa.Column("pdf_path", sa.String(500)),
        sa.Column("sha256", sa.String(64)),
        sa.Column("signed_by", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("signed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("size_bytes", sa.BigInteger),
    )

    # ── Dispatch Tasks ────────────────────────────────────────────
    op.create_table("dispatch_tasks",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("event_id", sa.Integer, sa.ForeignKey("chainage_events.id"), nullable=False),
        sa.Column("assigned_to", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("machinery", sa.String(200)),
        sa.Column("assignee", sa.String(200)),
        sa.Column("column_state", sa.Enum("queued","en_route","on_site","resolved",
                  name="dispatch_state"), default="queued"),
        sa.Column("progress_pct", sa.SmallInteger, default=0),
        sa.Column("field_report", sa.Text),
        sa.Column("verdict", sa.String(20)),
        sa.Column("verdict_submitted_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # ── App Config ────────────────────────────────────────────────
    op.create_table("app_config",
        sa.Column("key", sa.String(100), primary_key=True),
        sa.Column("value", sa.Text, nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_by", sa.Integer, sa.ForeignKey("users.id")),
    )

    # Seed default config values
    op.execute("""
        INSERT INTO app_config (key, value, description) VALUES
        ('otsu_slope_max_deg', '5.0', 'Max slope (degrees) for flood classification'),
        ('otsu_hand_max_m', '15.0', 'Max HAND value (m) for flood classification'),
        ('min_flood_area_ha', '1.0', 'Minimum flood polygon area to store (hectares)'),
        ('jrc_occurrence_threshold', '75', 'JRC permanent water occurrence threshold (0-100)'),
        ('scene_refresh_interval_h', '3', 'Hours between scene_watcher runs'),
        ('gujarat_aoi_bbox', '[68.0, 20.0, 74.5, 24.5]', 'Gujarat AOI bounding box [W,S,E,N]')
    """)

    # ── Audit Log ─────────────────────────────────────────────────
    op.create_table("audit_log",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50)),
        sa.Column("resource_id", sa.String(50)),
        sa.Column("detail", postgresql.JSONB),
        sa.Column("ip_address", sa.String(45)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_audit_log_created_at", "audit_log", ["created_at"])

    # ── Validation Runs ───────────────────────────────────────────
    op.create_table("validation_runs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("scene_id", sa.Integer, sa.ForeignKey("sar_scenes.id"), nullable=False),
        sa.Column("reference_source", sa.String(100)),
        sa.Column("reference_date", sa.DateTime(timezone=True)),
        sa.Column("iou", sa.Float),
        sa.Column("f1", sa.Float),
        sa.Column("precision", sa.Float),
        sa.Column("recall", sa.Float),
        sa.Column("notes", sa.Text),
        sa.Column("run_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("run_by", sa.String(100)),
    )


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS road_status_latest")
    for t in [
        "validation_runs", "audit_log", "app_config", "dispatch_tasks",
        "bulletins", "notification_deliveries", "notifications", "alerts",
        "chainage_events", "road_status", "flood_polygons", "sar_scenes",
        "road_edges", "road_nodes", "road_segments", "roads",
        "users", "talukas", "districts"
    ]:
        op.drop_table(t, if_exists=True)
    for e in ["user_role","user_status","scene_status","notif_status",
              "bulletin_status","delivery_status","dispatch_state","road_class"]:
        op.execute(f"DROP TYPE IF EXISTS {e}")


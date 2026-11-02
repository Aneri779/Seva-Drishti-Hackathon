"""
SAR-Drishti Backend Configuration
PostgreSQL + PostGIS + Redis only. No SQLite fallback.
All settings from environment variables only (never hardcoded).
"""
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # ── Application ──────────────────────────────────────────────
    APP_NAME: str = "SAR-Drishti API"
    APP_VERSION: str = "1.0.0"
    ENV: str = "production"
    DEMO_MODE: bool = False  # Must be explicitly set True; never defaults True

    # ── PostgreSQL (required) ────────────────────────────────────
    DATABASE_URL: str                      # asyncpg driver
    DATABASE_SYNC_URL: Optional[str] = None  # psycopg2, for Alembic

    # ── Redis (required) ─────────────────────────────────────────
    REDIS_URL: str

    # ── MinIO (required for COG storage) ─────────────────────────
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str = "sardrishti"
    MINIO_SECURE: bool = False

    # ── Google Earth Engine ──────────────────────────────────────
    GEE_PROJECT: str
    GEE_KEY_FILE: str  # Path to service account JSON; never logged

    # ── Copernicus Data Space Ecosystem (optional) ───────────────
    CDSE_USERNAME: Optional[str] = None
    CDSE_PASSWORD: Optional[str] = None

    # ── JWT ──────────────────────────────────────────────────────
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TTL_MIN: int = 15
    JWT_REFRESH_TTL_DAYS: int = 7

    # ── OTP rate-limits ──────────────────────────────────────────
    OTP_TTL_SEC: int = 300
    OTP_RATE_LIMIT_COUNT: int = 3
    OTP_RATE_LIMIT_WINDOW_MIN: int = 10
    OTP_MAX_VERIFY_ATTEMPTS: int = 5

    # ── Notification gateways ────────────────────────────────────
    SMS_GATEWAY: str = "console"
    WHATSAPP_GATEWAY: str = "console"
    SANDES_GATEWAY: str = "console"

    # ── CORS ─────────────────────────────────────────────────────
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    # ── Celery ───────────────────────────────────────────────────
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    SCENE_REFRESH_INTERVAL_H: int = 3

    # ── SAR pipeline thresholds (defaults; admin can override via app_config) ─
    OTSU_SLOPE_MAX_DEG: float = 5.0
    OTSU_HAND_MAX_M: float = 15.0
    MIN_FLOOD_AREA_HA: float = 1.0
    JRC_OCCURRENCE_THRESHOLD: int = 75

    @property
    def is_dev(self) -> bool:
        return self.ENV == "development"


settings = Settings()

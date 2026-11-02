"""
GEE client: initialise once with service account credentials.
Retries with tenacity. Fails loudly on any error.
Never logs or prints the key file content.
"""
import json
import logging
from functools import lru_cache
from typing import Optional

import ee
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings

logger = logging.getLogger(__name__)

_initialized = False


def _init_gee() -> None:
    """Initialize GEE exactly once. Raises on failure."""
    global _initialized
    if _initialized:
        return
    try:
        key_path = settings.GEE_KEY_FILE
        with open(key_path) as f:
            key_data = json.load(f)
        email = key_data["client_email"]
        # Never log the full key or email beyond this abbreviated form
        logger.info(f"GEE init: service account = {email[:20]}...@...")
        credentials = ee.ServiceAccountCredentials(email, key_path)
        ee.Initialize(credentials, project=settings.GEE_PROJECT)
        _initialized = True
        logger.info(f"GEE initialized for project={settings.GEE_PROJECT}")
    except Exception as e:
        logger.error(f"GEE initialization FAILED: {e}")
        raise RuntimeError(f"GEE initialization failed: {e}") from e


def get_ee() -> ee:
    """Get initialized GEE module. Raises if init fails."""
    _init_gee()
    return ee


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(ee.ee_exception.EEException),
    reraise=True,
)
def gee_call(fn, *args, **kwargs):
    """Wrap any GEE .getInfo() call with retries."""
    _init_gee()
    return fn(*args, **kwargs)


def check_gee_live() -> dict:
    """Run a real GEE call for /health/deep. Returns status dict."""
    try:
        _init_gee()
        # Query S1 scenes count over Gujarat in last 7 days
        from datetime import datetime, timedelta, timezone
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=7)
        gujarat_aoi = ee.Geometry.Rectangle([68.0, 20.0, 74.5, 24.5])
        count = (
            ee.ImageCollection("COPERNICUS/S1_GRD")
            .filterBounds(gujarat_aoi)
            .filterDate(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
            .size()
            .getInfo()
        )
        return {
            "status": "connected",
            "project": settings.GEE_PROJECT,
            "s1_scenes_last_7d": count,
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}


GUJARAT_AOI = ee.Geometry.Rectangle([68.0, 20.0, 74.5, 24.5])


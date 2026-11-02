"""
MinIO object storage service.
upload_bytes / download_bytes for COGs, PDFs, ID docs.
Fails loudly on connection error.
"""
import io
import logging
from typing import Optional

from minio import Minio
from minio.error import S3Error

from app.core.config import settings

logger = logging.getLogger(__name__)

_client: Optional[Minio] = None


def _get_client() -> Minio:
    global _client
    if _client is None:
        _client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        # Ensure bucket exists
        if not _client.bucket_exists(settings.MINIO_BUCKET):
            _client.make_bucket(settings.MINIO_BUCKET)
            logger.info(f"Created MinIO bucket: {settings.MINIO_BUCKET}")
    return _client


async def upload_bytes(data: bytes, path: str, content_type: str = "application/octet-stream") -> str:
    """Upload bytes to MinIO. Returns path (object name)."""
    client = _get_client()
    try:
        client.put_object(
            settings.MINIO_BUCKET,
            path,
            io.BytesIO(data),
            length=len(data),
            content_type=content_type,
        )
        logger.debug(f"Uploaded to MinIO: {path} ({len(data)} bytes)")
        return path
    except S3Error as e:
        logger.error(f"MinIO upload failed: {e}")
        raise RuntimeError(f"Object storage unavailable: {e}") from e


async def download_bytes(path: str) -> bytes:
    """Download bytes from MinIO."""
    client = _get_client()
    try:
        response = client.get_object(settings.MINIO_BUCKET, path)
        data = response.read()
        response.close()
        return data
    except S3Error as e:
        raise RuntimeError(f"Object not found: {path}: {e}") from e


def check_minio_live() -> dict:
    """Health check for MinIO."""
    try:
        client = _get_client()
        exists = client.bucket_exists(settings.MINIO_BUCKET)
        return {"status": "connected", "bucket": settings.MINIO_BUCKET, "exists": exists}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


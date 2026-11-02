"""
Celery application configuration.
Broker: Redis. Result backend: Redis.
Beat schedule: scene_watcher every SCENE_REFRESH_INTERVAL_H hours.
"""
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "sardrishti",
    broker=settings.CELERY_BROKER_URL or settings.REDIS_URL.replace("/0", "/1"),
    backend=settings.CELERY_RESULT_BACKEND or settings.REDIS_URL.replace("/0", "/2"),
    include=["app.sar.pipeline"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_queues={
        "sar_processing": {"exchange": "sar_processing", "routing_key": "sar_processing"},
        "default": {"exchange": "default", "routing_key": "default"},
    },
    task_default_queue="default",
    task_routes={
        "sar.process_scene": {"queue": "sar_processing"},
        "sar.scene_watcher": {"queue": "default"},
    },
    beat_schedule={
        "scene-watcher": {
            "task": "sar.scene_watcher",
            "schedule": settings.SCENE_REFRESH_INTERVAL_H * 3600,  # seconds
        }
    },
    # redbeat for distributed beat
    redbeat_redis_url=settings.CELERY_BROKER_URL or settings.REDIS_URL.replace("/0", "/1"),
)


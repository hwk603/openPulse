"""
Celery application configuration
"""
from celery import Celery
from config import get_settings

settings = get_settings()

# Create Celery app
celery_app = Celery(
    "openpulse",
    broker=settings.celery_broker,
    backend=settings.celery_backend,
    include=[
        "src.tasks.data_collection",
        "src.tasks.analysis",
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3000,  # 50 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Optional: Configure periodic tasks
celery_app.conf.beat_schedule = {
    "refresh-active-repositories": {
        "task": "src.tasks.data_collection.refresh_all_repositories",
        "schedule": 3600.0,  # Every hour
    },
}

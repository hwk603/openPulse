"""
Celery tasks for background processing
"""
from .celery_app import celery_app
from .data_collection_tasks import (
    fetch_repository_metrics_task,
    update_all_repositories_task,
)
from .analysis_tasks import (
    calculate_health_score_task,
    predict_contributor_churn_task,
    analyze_collaboration_network_task,
)

__all__ = [
    "celery_app",
    "fetch_repository_metrics_task",
    "update_all_repositories_task",
    "calculate_health_score_task",
    "predict_contributor_churn_task",
    "analyze_collaboration_network_task",
]

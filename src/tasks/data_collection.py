"""
Celery tasks for data collection
"""
from datetime import datetime
from loguru import logger
from typing import Dict, Any

from src.tasks.celery_app import celery_app
from src.data_collection import OpenDiggerClient
from src.storage import IoTDBClient
from src.database import get_db_context
from src.models.database import RepositoryModel


@celery_app.task(name="src.tasks.data_collection.fetch_repository_metrics")
def fetch_repository_metrics(platform: str, owner: str, repo: str) -> Dict[str, Any]:
    """
    Fetch metrics for a repository from OpenDigger

    Args:
        platform: Platform name (github/gitee)
        owner: Repository owner
        repo: Repository name

    Returns:
        Dictionary with fetched metrics
    """
    import asyncio

    logger.info(f"Fetching metrics for {platform}/{owner}/{repo}")

    try:
        repo_full_name = f"{owner}/{repo}"

        # Fetch metrics from OpenDigger
        client = OpenDiggerClient()
        loop = asyncio.get_event_loop()
        metrics = loop.run_until_complete(client.get_all_metrics(platform, owner, repo))

        # Store in IoTDB
        with IoTDBClient() as iotdb_client:
            # Process OpenRank data
            if "openrank" in metrics and metrics["openrank"]:
                for timestamp_str, value in list(metrics["openrank"].items())[:100]:  # Limit to recent 100
                    try:
                        # Parse timestamp
                        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                        iotdb_client.insert_metrics(
                            repo_full_name,
                            timestamp,
                            {"openrank": float(value)}
                        )
                    except Exception as e:
                        logger.warning(f"Failed to insert OpenRank data point: {e}")
                        continue

            # Process activity data
            if "activity" in metrics and metrics["activity"]:
                for timestamp_str, value in list(metrics["activity"].items())[:100]:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                        iotdb_client.insert_metrics(
                            repo_full_name,
                            timestamp,
                            {"activity_score": float(value)}
                        )
                    except Exception as e:
                        logger.warning(f"Failed to insert activity data point: {e}")
                        continue

            # Process stars data
            if "stars" in metrics and metrics["stars"]:
                for timestamp_str, value in list(metrics["stars"].items())[:100]:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                        iotdb_client.insert_metrics(
                            repo_full_name,
                            timestamp,
                            {"stars": int(value)}
                        )
                    except Exception as e:
                        logger.warning(f"Failed to insert stars data point: {e}")
                        continue

        # Update repository last_analyzed timestamp
        with get_db_context() as db:
            repo_model = db.query(RepositoryModel).filter(
                RepositoryModel.full_name == repo_full_name
            ).first()
            if repo_model:
                repo_model.last_analyzed = datetime.utcnow()
                db.commit()

        logger.info(f"Successfully fetched and stored metrics for {repo_full_name}")
        return {"status": "success", "repo": repo_full_name, "metrics_count": len(metrics)}

    except Exception as e:
        logger.error(f"Failed to fetch metrics for {platform}/{owner}/{repo}: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="src.tasks.data_collection.refresh_all_repositories")
def refresh_all_repositories() -> Dict[str, Any]:
    """
    Refresh metrics for all active repositories

    Returns:
        Dictionary with refresh status
    """
    logger.info("Refreshing all active repositories")

    try:
        with get_db_context() as db:
            active_repos = db.query(RepositoryModel).filter(
                RepositoryModel.is_active == True
            ).all()

            count = 0
            for repo in active_repos:
                # Schedule individual fetch tasks
                fetch_repository_metrics.delay(repo.platform, repo.owner, repo.name)
                count += 1

        logger.info(f"Scheduled refresh for {count} repositories")
        return {"status": "success", "repositories_scheduled": count}

    except Exception as e:
        logger.error(f"Failed to refresh repositories: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="src.tasks.data_collection.collect_collaboration_data")
def collect_collaboration_data(platform: str, owner: str, repo: str) -> Dict[str, Any]:
    """
    Collect collaboration network data for a repository

    Args:
        platform: Platform name (github/gitee)
        owner: Repository owner
        repo: Repository name

    Returns:
        Dictionary with collaboration data
    """
    logger.info(f"Collecting collaboration data for {platform}/{owner}/{repo}")

    try:
        # This would typically fetch PR reviews, co-authored commits, etc.
        # For now, return placeholder
        repo_full_name = f"{owner}/{repo}"

        # In production, would fetch from GitHub API or other sources
        # and build collaboration edges

        logger.info(f"Collaboration data collection completed for {repo_full_name}")
        return {"status": "success", "repo": repo_full_name}

    except Exception as e:
        logger.error(f"Failed to collect collaboration data: {e}")
        return {"status": "error", "error": str(e)}

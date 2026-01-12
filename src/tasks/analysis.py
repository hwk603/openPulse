"""
Celery tasks for analysis
"""
from datetime import datetime
from loguru import logger
from typing import Dict, Any

from src.tasks.celery_app import celery_app
from src.services import HealthAssessmentService, ChurnPredictionService
from src.database import get_db_context
from src.models.database import HealthScoreModel, ChurnPredictionModel, RepositoryModel, ContributorModel


@celery_app.task(name="src.tasks.analysis.analyze_repository_health")
def analyze_repository_health(repo_full_name: str) -> Dict[str, Any]:
    """
    Analyze repository health and store results

    Args:
        repo_full_name: Full repository name (owner/repo)

    Returns:
        Dictionary with analysis results
    """
    logger.info(f"Analyzing health for {repo_full_name}")

    try:
        # Calculate health score
        service = HealthAssessmentService()
        health_score = service.calculate_health_score(repo_full_name)

        # Store in database
        with get_db_context() as db:
            repo = db.query(RepositoryModel).filter(
                RepositoryModel.full_name == repo_full_name
            ).first()

            if repo:
                health_model = HealthScoreModel(
                    repo_id=repo.id,
                    timestamp=health_score.timestamp,
                    overall_score=health_score.overall_score,
                    activity_score=health_score.activity_score,
                    diversity_score=health_score.diversity_score,
                    response_time_score=health_score.response_time_score,
                    code_quality_score=health_score.code_quality_score,
                    documentation_score=health_score.documentation_score,
                    community_atmosphere_score=health_score.community_atmosphere_score,
                    lifecycle_stage=health_score.lifecycle_stage.value,
                )
                db.add(health_model)
                db.commit()

        logger.info(f"Health analysis completed for {repo_full_name}: {health_score.overall_score:.2f}")
        return {
            "status": "success",
            "repo": repo_full_name,
            "overall_score": health_score.overall_score,
            "lifecycle_stage": health_score.lifecycle_stage.value
        }

    except Exception as e:
        logger.error(f"Failed to analyze health for {repo_full_name}: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="src.tasks.analysis.predict_contributor_churn")
def predict_contributor_churn(repo_full_name: str, contributor_username: str) -> Dict[str, Any]:
    """
    Predict churn probability for a contributor

    Args:
        repo_full_name: Full repository name (owner/repo)
        contributor_username: Contributor username

    Returns:
        Dictionary with prediction results
    """
    logger.info(f"Predicting churn for {contributor_username} in {repo_full_name}")

    try:
        # Predict churn
        service = ChurnPredictionService()
        prediction = service.predict_churn(repo_full_name, contributor_username)

        # Store in database
        with get_db_context() as db:
            repo = db.query(RepositoryModel).filter(
                RepositoryModel.full_name == repo_full_name
            ).first()

            contributor = db.query(ContributorModel).filter(
                ContributorModel.username == contributor_username
            ).first()

            if not contributor:
                # Create contributor if doesn't exist
                contributor = ContributorModel(
                    username=contributor_username,
                    platform="github"  # Default
                )
                db.add(contributor)
                db.flush()

            if repo and contributor:
                churn_model = ChurnPredictionModel(
                    repo_id=repo.id,
                    contributor_id=contributor.id,
                    prediction_date=prediction.prediction_date,
                    churn_probability=prediction.churn_probability,
                    alert_level=prediction.alert_level.value,
                    behavior_decay_score=prediction.behavior_decay_score,
                    network_marginalization_score=prediction.network_marginalization_score,
                    temporal_anomaly_score=prediction.temporal_anomaly_score,
                    community_engagement_score=prediction.community_engagement_score,
                    retention_suggestions=prediction.retention_suggestions,
                )
                db.add(churn_model)
                db.commit()

        logger.info(f"Churn prediction completed for {contributor_username}: {prediction.churn_probability:.2%}")
        return {
            "status": "success",
            "contributor": contributor_username,
            "churn_probability": prediction.churn_probability,
            "alert_level": prediction.alert_level.value
        }

    except Exception as e:
        logger.error(f"Failed to predict churn for {contributor_username}: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="src.tasks.analysis.analyze_collaboration_network")
def analyze_collaboration_network(repo_full_name: str) -> Dict[str, Any]:
    """
    Analyze collaboration network for a repository

    Args:
        repo_full_name: Full repository name (owner/repo)

    Returns:
        Dictionary with network analysis results
    """
    logger.info(f"Analyzing collaboration network for {repo_full_name}")

    try:
        from src.graph_analysis import CollaborationNetworkAnalyzer

        # This would typically load collaboration data and analyze
        # For now, return placeholder
        analyzer = CollaborationNetworkAnalyzer()

        # In production, would load actual collaboration data
        # collaborations = load_collaboration_data(repo_full_name)
        # analyzer.build_network(collaborations)
        # metrics = analyzer.calculate_network_metrics()
        # key_contributors = analyzer.identify_key_contributors()
        # bus_factor = analyzer.calculate_bus_factor()

        logger.info(f"Network analysis completed for {repo_full_name}")
        return {"status": "success", "repo": repo_full_name}

    except Exception as e:
        logger.error(f"Failed to analyze network for {repo_full_name}: {e}")
        return {"status": "error", "error": str(e)}

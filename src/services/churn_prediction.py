"""
Contributor churn prediction service
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger
import numpy as np

from src.models import ChurnPrediction, AlertLevel
from src.storage import IoTDBClient
from src.graph_analysis import CollaborationNetworkAnalyzer
from config import get_settings


class ChurnPredictionService:
    """Service for predicting contributor churn"""

    def __init__(self):
        self.settings = get_settings()
        self.iotdb_client = IoTDBClient()
        self.network_analyzer = CollaborationNetworkAnalyzer()

    def predict_churn(
        self,
        repo_full_name: str,
        contributor_username: str,
        collaboration_data: List[Dict[str, Any]] = None,
    ) -> ChurnPrediction:
        """
        Predict churn probability for a contributor

        Args:
            repo_full_name: Full repository name
            contributor_username: Username of contributor
            collaboration_data: Optional collaboration network data

        Returns:
            ChurnPrediction object
        """
        logger.info(f"Predicting churn for {contributor_username} in {repo_full_name}")

        prediction_date = datetime.utcnow()

        # Calculate behavior decay score
        behavior_decay_score = self._calculate_behavior_decay(
            repo_full_name, contributor_username
        )

        # Calculate network marginalization score
        network_marginalization_score = 0.0
        if collaboration_data:
            self.network_analyzer.build_network(collaboration_data)
            network_marginalization_score = self._calculate_network_marginalization(
                contributor_username
            )

        # Calculate temporal anomaly score
        temporal_anomaly_score = self._calculate_temporal_anomaly(
            repo_full_name, contributor_username
        )

        # Calculate community engagement score
        community_engagement_score = self._calculate_community_engagement(
            repo_full_name, contributor_username
        )

        # Calculate overall churn probability (weighted combination)
        churn_probability = (
            0.35 * behavior_decay_score
            + 0.30 * network_marginalization_score
            + 0.25 * temporal_anomaly_score
            + 0.10 * (1 - community_engagement_score)  # Lower engagement = higher churn
        )

        # Determine alert level
        alert_level = self._determine_alert_level(churn_probability)

        # Generate retention suggestions
        retention_suggestions = self._generate_retention_suggestions(
            behavior_decay_score,
            network_marginalization_score,
            temporal_anomaly_score,
            community_engagement_score,
        )

        prediction = ChurnPrediction(
            contributor_username=contributor_username,
            repo_full_name=repo_full_name,
            prediction_date=prediction_date,
            churn_probability=churn_probability,
            alert_level=alert_level,
            behavior_decay_score=behavior_decay_score,
            network_marginalization_score=network_marginalization_score,
            temporal_anomaly_score=temporal_anomaly_score,
            community_engagement_score=community_engagement_score,
            retention_suggestions=retention_suggestions,
        )

        logger.info(
            f"Churn prediction for {contributor_username}: "
            f"{churn_probability:.2%} ({alert_level})"
        )
        return prediction

    def _calculate_behavior_decay(
        self, repo_full_name: str, contributor_username: str
    ) -> float:
        """
        Calculate behavior decay score based on contribution frequency decline

        Returns:
            Score between 0 (no decay) and 1 (severe decay)
        """
        # Get contribution history from IoTDB
        # This is a simplified version - in production would track per-contributor metrics

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=self.settings.CHURN_PREDICTION_WINDOW_DAYS)

        try:
            metrics = self.iotdb_client.query_metrics(
                repo_full_name,
                ["commits", "pull_requests", "active_contributors"],
                start_time,
                end_time,
            )

            if not metrics or len(metrics) < 30:
                return 0.5  # Insufficient data

            # Split into recent and older periods
            mid_point = len(metrics) // 2
            recent_period = metrics[mid_point:]
            older_period = metrics[:mid_point]

            # Calculate average activity
            recent_activity = np.mean([m.get("commits", 0) for m in recent_period])
            older_activity = np.mean([m.get("commits", 0) for m in older_period])

            if older_activity == 0:
                return 0.5

            # Calculate decay rate
            decay_rate = (older_activity - recent_activity) / older_activity

            # Normalize to 0-1 (30% decline = 0.3 score)
            decay_score = max(0, min(decay_rate, 1.0))

            return decay_score

        except Exception as e:
            logger.error(f"Failed to calculate behavior decay: {e}")
            return 0.5

    def _calculate_network_marginalization(self, contributor_username: str) -> float:
        """
        Calculate network marginalization score based on centrality decline

        Returns:
            Score between 0 (central) and 1 (marginalized)
        """
        if not self.network_analyzer.graph:
            return 0.5

        try:
            # Get centrality metrics
            centrality_metrics = self.network_analyzer.calculate_centrality_metrics()

            if contributor_username not in centrality_metrics:
                return 0.8  # Not in network = highly marginalized

            metrics = centrality_metrics[contributor_username]

            # Calculate marginalization based on low centrality
            degree_cent = metrics.get("degree_centrality", 0.0)
            betweenness_cent = metrics.get("betweenness_centrality", 0.0)

            # Lower centrality = higher marginalization
            marginalization_score = 1 - (0.6 * degree_cent + 0.4 * betweenness_cent)

            return marginalization_score

        except Exception as e:
            logger.error(f"Failed to calculate network marginalization: {e}")
            return 0.5

    def _calculate_temporal_anomaly(
        self, repo_full_name: str, contributor_username: str
    ) -> float:
        """
        Calculate temporal anomaly score based on activity pattern changes

        Returns:
            Score between 0 (normal) and 1 (anomalous)
        """
        # Simplified version - in production would use time series anomaly detection
        # For now, use behavior decay as proxy
        return self._calculate_behavior_decay(repo_full_name, contributor_username) * 0.8

    def _calculate_community_engagement(
        self, repo_full_name: str, contributor_username: str
    ) -> float:
        """
        Calculate community engagement score

        Returns:
            Score between 0 (no engagement) and 1 (high engagement)
        """
        # Simplified version - in production would track:
        # - Issue/PR comments
        # - Code reviews
        # - Discussion participation
        # For now, return moderate engagement
        return 0.6

    def _determine_alert_level(self, churn_probability: float) -> AlertLevel:
        """Determine alert level based on churn probability"""
        if churn_probability >= 0.7:
            return AlertLevel.RED
        elif churn_probability >= 0.5:
            return AlertLevel.ORANGE
        elif churn_probability >= 0.3:
            return AlertLevel.YELLOW
        else:
            return AlertLevel.GREEN

    def _generate_retention_suggestions(
        self,
        behavior_decay: float,
        network_marginalization: float,
        temporal_anomaly: float,
        community_engagement: float,
    ) -> List[str]:
        """Generate personalized retention suggestions"""
        suggestions = []

        if behavior_decay > 0.5:
            suggestions.append(
                "Contributor activity has declined significantly. "
                "Consider reaching out to understand if they're facing blockers."
            )

        if network_marginalization > 0.6:
            suggestions.append(
                "Contributor is becoming isolated in the collaboration network. "
                "Encourage pairing with core team members on important features."
            )

        if temporal_anomaly > 0.6:
            suggestions.append(
                "Unusual activity pattern detected. "
                "Schedule a 1-on-1 to discuss their continued involvement."
            )

        if community_engagement < 0.4:
            suggestions.append(
                "Low community engagement. "
                "Invite them to participate in discussions, code reviews, or community events."
            )

        if not suggestions:
            suggestions.append(
                "Contributor appears healthy. Continue regular engagement and recognition."
            )

        return suggestions

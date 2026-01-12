"""
Health assessment service for open source communities
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger

from src.models import HealthScore, LifecycleStage
from src.storage import IoTDBClient
from config import get_settings


class HealthAssessmentService:
    """Service for assessing community health"""

    def __init__(self):
        self.settings = get_settings()
        self.iotdb_client = IoTDBClient()

    def calculate_health_score(
        self, repo_full_name: str, timestamp: datetime = None
    ) -> HealthScore:
        """
        Calculate comprehensive health score for a repository

        Args:
            repo_full_name: Full repository name
            timestamp: Timestamp for assessment (default: now)

        Returns:
            HealthScore object
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        logger.info(f"Calculating health score for {repo_full_name}")

        # Get recent metrics from IoTDB
        end_time = timestamp
        start_time = timestamp - timedelta(days=90)

        metrics = self.iotdb_client.query_metrics(
            repo_full_name,
            [
                "openrank",
                "active_contributors",
                "commits",
                "pull_requests",
                "issues_opened",
                "issues_closed",
                "issue_response_time",
                "stars",
            ],
            start_time,
            end_time,
        )

        if not metrics:
            logger.warning(f"No metrics found for {repo_full_name}")
            return self._create_default_health_score(repo_full_name, timestamp)

        # Calculate dimension scores
        activity_score = self._calculate_activity_score(metrics)
        diversity_score = self._calculate_diversity_score(metrics)
        response_time_score = self._calculate_response_time_score(metrics)
        code_quality_score = self._calculate_code_quality_score(metrics)
        documentation_score = self._calculate_documentation_score(metrics)
        community_atmosphere_score = self._calculate_community_atmosphere_score(metrics)

        # Calculate overall score using weights
        weights = self.settings.HEALTH_SCORE_WEIGHTS
        overall_score = (
            weights["activity"] * activity_score
            + weights["diversity"] * diversity_score
            + weights["response_time"] * response_time_score
            + weights["code_quality"] * code_quality_score
            + weights["documentation"] * documentation_score
            + weights["community_atmosphere"] * community_atmosphere_score
        )

        # Determine lifecycle stage
        lifecycle_stage = self._determine_lifecycle_stage(metrics, overall_score)

        health_score = HealthScore(
            timestamp=timestamp,
            repo_full_name=repo_full_name,
            overall_score=overall_score,
            activity_score=activity_score,
            diversity_score=diversity_score,
            response_time_score=response_time_score,
            code_quality_score=code_quality_score,
            documentation_score=documentation_score,
            community_atmosphere_score=community_atmosphere_score,
            lifecycle_stage=lifecycle_stage,
        )

        logger.info(
            f"Health score for {repo_full_name}: {overall_score:.2f} ({lifecycle_stage})"
        )
        return health_score

    def _calculate_activity_score(self, metrics: List[Dict[str, Any]]) -> float:
        """Calculate activity score based on commits, PRs, issues"""
        if not metrics:
            return 0.0

        # Calculate average activity
        total_commits = sum(m.get("commits", 0) for m in metrics)
        total_prs = sum(m.get("pull_requests", 0) for m in metrics)
        total_issues = sum(m.get("issues_opened", 0) for m in metrics)

        # Normalize (assuming healthy project has ~100 commits, 20 PRs, 30 issues per 90 days)
        commit_score = min(total_commits / 100, 1.0) * 40
        pr_score = min(total_prs / 20, 1.0) * 30
        issue_score = min(total_issues / 30, 1.0) * 30

        return (commit_score + pr_score + issue_score) * 100 / 100

    def _calculate_diversity_score(self, metrics: List[Dict[str, Any]]) -> float:
        """Calculate diversity score based on contributor count"""
        if not metrics:
            return 0.0

        # Average active contributors
        avg_contributors = sum(m.get("active_contributors", 0) for m in metrics) / len(
            metrics
        )

        # Normalize (assuming healthy project has 10+ active contributors)
        score = min(avg_contributors / 10, 1.0) * 100
        return score

    def _calculate_response_time_score(self, metrics: List[Dict[str, Any]]) -> float:
        """Calculate response time score"""
        if not metrics:
            return 0.0

        # Average response time (in hours)
        response_times = [
            m.get("issue_response_time", 0) for m in metrics if m.get("issue_response_time")
        ]

        if not response_times:
            return 50.0  # Neutral score if no data

        avg_response_time = sum(response_times) / len(response_times)

        # Normalize (lower is better, 24 hours = 100, 168 hours = 0)
        if avg_response_time <= 24:
            score = 100.0
        elif avg_response_time >= 168:
            score = 0.0
        else:
            score = 100 - ((avg_response_time - 24) / (168 - 24)) * 100

        return score

    def _calculate_code_quality_score(self, metrics: List[Dict[str, Any]]) -> float:
        """Calculate code quality score (placeholder - would need code analysis)"""
        # This is a simplified version
        # In production, would analyze: test coverage, code review rate, etc.

        if not metrics:
            return 50.0

        # Use PR to commit ratio as proxy
        total_commits = sum(m.get("commits", 0) for m in metrics)
        total_prs = sum(m.get("pull_requests", 0) for m in metrics)

        if total_commits == 0:
            return 50.0

        pr_ratio = total_prs / total_commits
        # Healthy ratio: 0.2-0.5 (20-50% of commits via PR)
        if 0.2 <= pr_ratio <= 0.5:
            score = 100.0
        elif pr_ratio < 0.2:
            score = pr_ratio / 0.2 * 100
        else:
            score = max(100 - (pr_ratio - 0.5) * 100, 0)

        return score

    def _calculate_documentation_score(self, metrics: List[Dict[str, Any]]) -> float:
        """Calculate documentation score (placeholder)"""
        # This is a simplified version
        # In production, would analyze: README quality, wiki pages, comments, etc.
        return 70.0  # Default neutral-positive score

    def _calculate_community_atmosphere_score(
        self, metrics: List[Dict[str, Any]]
    ) -> float:
        """Calculate community atmosphere score"""
        if not metrics:
            return 50.0

        # Use issue closure rate as proxy
        total_opened = sum(m.get("issues_opened", 0) for m in metrics)
        total_closed = sum(m.get("issues_closed", 0) for m in metrics)

        if total_opened == 0:
            return 70.0  # Neutral-positive if no issues

        closure_rate = total_closed / total_opened
        # Healthy closure rate: 0.7-1.0
        score = min(closure_rate / 0.7, 1.0) * 100

        return score

    def _determine_lifecycle_stage(
        self, metrics: List[Dict[str, Any]], overall_score: float
    ) -> LifecycleStage:
        """Determine lifecycle stage based on metrics and trends"""
        if not metrics or len(metrics) < 2:
            return LifecycleStage.EMBRYONIC

        # Calculate trends
        recent_metrics = metrics[-30:]  # Last 30 days
        older_metrics = metrics[:30] if len(metrics) > 30 else metrics[:len(metrics)//2]

        recent_activity = sum(m.get("commits", 0) for m in recent_metrics) / len(recent_metrics)
        older_activity = sum(m.get("commits", 0) for m in older_metrics) / len(older_metrics)

        recent_contributors = sum(m.get("active_contributors", 0) for m in recent_metrics) / len(recent_metrics)
        older_contributors = sum(m.get("active_contributors", 0) for m in older_metrics) / len(older_metrics)

        # Determine stage
        if recent_contributors < 3:
            return LifecycleStage.EMBRYONIC
        elif recent_activity > older_activity * 1.2 and recent_contributors > older_contributors * 1.1:
            return LifecycleStage.GROWTH
        elif overall_score >= 70 and abs(recent_activity - older_activity) / max(older_activity, 1) < 0.2:
            return LifecycleStage.MATURE
        elif recent_activity < older_activity * 0.7:
            return LifecycleStage.DECLINE
        else:
            return LifecycleStage.MATURE

    def _create_default_health_score(
        self, repo_full_name: str, timestamp: datetime
    ) -> HealthScore:
        """Create default health score when no data available"""
        return HealthScore(
            timestamp=timestamp,
            repo_full_name=repo_full_name,
            overall_score=0.0,
            activity_score=0.0,
            diversity_score=0.0,
            response_time_score=0.0,
            code_quality_score=0.0,
            documentation_score=0.0,
            community_atmosphere_score=0.0,
            lifecycle_stage=LifecycleStage.EMBRYONIC,
        )

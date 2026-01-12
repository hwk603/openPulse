"""
Test business services (health assessment and churn prediction)
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from src.services.health_assessment import HealthAssessmentService
from src.services.churn_prediction import ChurnPredictionService
from src.models import HealthScore, ChurnPrediction, AlertLevel, LifecycleStage


class TestHealthAssessmentService:
    """Test suite for health assessment service"""

    @pytest.fixture
    def service(self, mock_iotdb_client):
        """Create health assessment service with mocked dependencies"""
        with patch('src.services.health_assessment.IoTDBClient', return_value=mock_iotdb_client):
            return HealthAssessmentService()

    def test_calculate_health_score(self, service, mock_iotdb_client):
        """Test health score calculation"""
        mock_iotdb_client.query_metrics.return_value = {
            "openrank": [100.5, 105.2, 110.8],
            "active_contributors": [45, 48, 52],
            "commits": [120, 130, 150],
            "pull_requests": [40, 42, 45],
            "issues_opened": [25, 28, 30],
            "issues_closed": [23, 26, 28],
            "stars": [4500, 4800, 5000],
            "forks": [1000, 1100, 1200]
        }

        health_score = service.calculate_health_score("apache/iotdb")

        assert health_score is not None
        assert isinstance(health_score, HealthScore)
        assert 0 <= health_score.overall_score <= 100
        assert health_score.repo_full_name == "apache/iotdb"

    def test_calculate_activity_score(self, service):
        """Test activity score calculation"""
        metrics = {
            "commits": [120, 130, 150],
            "pull_requests": [40, 42, 45],
            "issues_opened": [25, 28, 30]
        }

        score = service._calculate_activity_score(metrics)

        assert 0 <= score <= 100
        assert isinstance(score, float)

    def test_calculate_diversity_score(self, service):
        """Test diversity score calculation"""
        metrics = {
            "active_contributors": [45, 48, 52],
            "new_contributors": [5, 6, 8]
        }

        score = service._calculate_diversity_score(metrics)

        assert 0 <= score <= 100
        assert isinstance(score, float)

    def test_calculate_response_time_score(self, service):
        """Test response time score calculation"""
        metrics = {
            "issue_response_time": [24, 20, 18],  # hours
            "pr_response_time": [48, 36, 30]  # hours
        }

        score = service._calculate_response_time_score(metrics)

        assert 0 <= score <= 100
        assert isinstance(score, float)

    def test_calculate_code_quality_score(self, service):
        """Test code quality score calculation"""
        metrics = {
            "pr_review_rate": [0.85, 0.88, 0.90],
            "test_coverage": [0.75, 0.78, 0.80]
        }

        score = service._calculate_code_quality_score(metrics)

        assert 0 <= score <= 100
        assert isinstance(score, float)

    def test_identify_lifecycle_stage_embryonic(self, service):
        """Test lifecycle stage identification - embryonic"""
        metrics = {
            "active_contributors": [2, 2, 3],
            "commits": [10, 15, 20]
        }

        stage = service._identify_lifecycle_stage(metrics)

        assert stage == LifecycleStage.EMBRYONIC

    def test_identify_lifecycle_stage_growth(self, service):
        """Test lifecycle stage identification - growth"""
        metrics = {
            "active_contributors": [10, 15, 25],
            "commits": [100, 150, 250],
            "activity_trend": 0.5  # 50% growth
        }

        stage = service._identify_lifecycle_stage(metrics)

        assert stage == LifecycleStage.GROWTH

    def test_identify_lifecycle_stage_mature(self, service):
        """Test lifecycle stage identification - mature"""
        metrics = {
            "active_contributors": [50, 52, 51],
            "commits": [200, 210, 205],
            "activity_trend": 0.02  # 2% growth
        }

        stage = service._identify_lifecycle_stage(metrics)

        assert stage == LifecycleStage.MATURE

    def test_identify_lifecycle_stage_decline(self, service):
        """Test lifecycle stage identification - decline"""
        metrics = {
            "active_contributors": [50, 40, 30],
            "commits": [200, 150, 100],
            "activity_trend": -0.35  # 35% decline
        }

        stage = service._identify_lifecycle_stage(metrics)

        assert stage == LifecycleStage.DECLINE

    def test_health_score_with_missing_data(self, service, mock_iotdb_client):
        """Test health score calculation with missing data"""
        mock_iotdb_client.query_metrics.return_value = {
            "openrank": [100.5],
            "active_contributors": []
        }

        health_score = service.calculate_health_score("apache/iotdb")

        # Should handle missing data gracefully
        assert health_score is not None
        assert 0 <= health_score.overall_score <= 100


class TestChurnPredictionService:
    """Test suite for churn prediction service"""

    @pytest.fixture
    def service(self, mock_iotdb_client, mock_network_analyzer):
        """Create churn prediction service with mocked dependencies"""
        with patch('src.services.churn_prediction.IoTDBClient', return_value=mock_iotdb_client), \
             patch('src.services.churn_prediction.CollaborationNetworkAnalyzer', return_value=mock_network_analyzer):
            return ChurnPredictionService()

    def test_predict_churn(self, service, mock_iotdb_client, mock_network_analyzer):
        """Test churn prediction"""
        mock_iotdb_client.query_contributor_metrics.return_value = {
            "commits": [20, 18, 15, 10, 5],
            "pull_requests": [8, 7, 5, 3, 1],
            "issues": [5, 4, 3, 2, 1]
        }

        prediction = service.predict_churn("apache/iotdb", "testuser")

        assert prediction is not None
        assert isinstance(prediction, ChurnPrediction)
        assert 0 <= prediction.churn_probability <= 1
        assert prediction.contributor_username == "testuser"
        assert prediction.repo_full_name == "apache/iotdb"

    def test_calculate_behavior_decay_score(self, service):
        """Test behavior decay score calculation"""
        activity_history = {
            "commits": [20, 18, 15, 10, 5],
            "pull_requests": [8, 7, 5, 3, 1]
        }

        score = service._calculate_behavior_decay_score(activity_history)

        assert 0 <= score <= 1
        assert isinstance(score, float)

    def test_calculate_network_marginalization_score(self, service, mock_network_analyzer):
        """Test network marginalization score calculation"""
        centrality_history = [
            {"degree": 10, "betweenness": 0.5},
            {"degree": 8, "betweenness": 0.4},
            {"degree": 5, "betweenness": 0.2}
        ]

        score = service._calculate_network_marginalization_score(centrality_history)

        assert 0 <= score <= 1
        assert isinstance(score, float)

    def test_calculate_temporal_anomaly_score(self, service):
        """Test temporal anomaly score calculation"""
        activity_pattern = [10, 12, 11, 13, 2, 1, 0]  # Sudden drop

        score = service._calculate_temporal_anomaly_score(activity_pattern)

        assert 0 <= score <= 1
        assert isinstance(score, float)
        assert score > 0.5  # Should detect anomaly

    def test_calculate_community_engagement_score(self, service):
        """Test community engagement score calculation"""
        engagement_metrics = {
            "code_reviews": [5, 4, 3, 2, 1],
            "issue_comments": [10, 8, 6, 4, 2],
            "pr_comments": [8, 6, 4, 2, 1]
        }

        score = service._calculate_community_engagement_score(engagement_metrics)

        assert 0 <= score <= 1
        assert isinstance(score, float)

    def test_determine_alert_level_green(self, service):
        """Test alert level determination - green"""
        churn_probability = 0.15

        alert_level = service._determine_alert_level(churn_probability)

        assert alert_level == AlertLevel.GREEN

    def test_determine_alert_level_yellow(self, service):
        """Test alert level determination - yellow"""
        churn_probability = 0.45

        alert_level = service._determine_alert_level(churn_probability)

        assert alert_level == AlertLevel.YELLOW

    def test_determine_alert_level_orange(self, service):
        """Test alert level determination - orange"""
        churn_probability = 0.65

        alert_level = service._determine_alert_level(churn_probability)

        assert alert_level == AlertLevel.ORANGE

    def test_determine_alert_level_red(self, service):
        """Test alert level determination - red"""
        churn_probability = 0.85

        alert_level = service._determine_alert_level(churn_probability)

        assert alert_level == AlertLevel.RED

    def test_generate_retention_suggestions_green(self, service):
        """Test retention suggestions for green alert"""
        prediction_data = {
            "alert_level": AlertLevel.GREEN,
            "churn_probability": 0.15
        }

        suggestions = service._generate_retention_suggestions(prediction_data)

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    def test_generate_retention_suggestions_red(self, service):
        """Test retention suggestions for red alert"""
        prediction_data = {
            "alert_level": AlertLevel.RED,
            "churn_probability": 0.85,
            "behavior_decay_score": 0.9,
            "network_marginalization_score": 0.8
        }

        suggestions = service._generate_retention_suggestions(prediction_data)

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        # Should have more urgent suggestions
        assert any("urgent" in s.lower() or "immediate" in s.lower() for s in suggestions)

    def test_predict_churn_with_insufficient_data(self, service, mock_iotdb_client):
        """Test churn prediction with insufficient historical data"""
        mock_iotdb_client.query_contributor_metrics.return_value = {
            "commits": [5],  # Only one data point
            "pull_requests": [2]
        }

        prediction = service.predict_churn("apache/iotdb", "newuser")

        # Should handle gracefully
        assert prediction is not None
        assert prediction.churn_probability >= 0

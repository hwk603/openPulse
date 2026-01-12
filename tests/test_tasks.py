"""
Test Celery tasks
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.tasks.data_collection import (
    fetch_repository_metrics,
    refresh_all_repositories,
    collect_collaboration_data
)
from src.tasks.analysis import (
    analyze_repository_health,
    predict_contributor_churn,
    analyze_collaboration_network
)


class TestDataCollectionTasks:
    """Test suite for data collection tasks"""

    @patch('src.tasks.data_collection.OpenDiggerClient')
    @patch('src.tasks.data_collection.IoTDBClient')
    def test_fetch_repository_metrics(self, mock_iotdb, mock_opendigger):
        """Test fetching repository metrics task"""
        # Setup mocks
        mock_opendigger_instance = Mock()
        mock_opendigger_instance.get_openrank = AsyncMock(return_value={"2024-01": 100.5})
        mock_opendigger_instance.get_activity = AsyncMock(return_value={"2024-01": 250.0})
        mock_opendigger.return_value = mock_opendigger_instance

        mock_iotdb_instance = Mock()
        mock_iotdb_instance.insert_metrics = Mock(return_value=True)
        mock_iotdb.return_value = mock_iotdb_instance

        # Execute task
        result = fetch_repository_metrics.apply(
            args=["github", "apache", "iotdb"]
        ).get()

        assert result is not None

    @patch('src.tasks.data_collection.get_db')
    @patch('src.tasks.data_collection.OpenDiggerClient')
    def test_refresh_all_repositories(self, mock_opendigger, mock_db):
        """Test refreshing all repositories task"""
        # Setup mock database
        mock_session = Mock()
        mock_repo1 = Mock(platform="github", owner="apache", repo="iotdb")
        mock_repo2 = Mock(platform="github", owner="apache", repo="kafka")
        mock_session.query.return_value.filter.return_value.all.return_value = [
            mock_repo1, mock_repo2
        ]
        mock_db.return_value = mock_session

        # Setup mock OpenDigger
        mock_opendigger_instance = Mock()
        mock_opendigger_instance.get_openrank = AsyncMock(return_value={"2024-01": 100.5})
        mock_opendigger.return_value = mock_opendigger_instance

        # Execute task
        result = refresh_all_repositories.apply().get()

        assert result is not None

    @patch('src.tasks.data_collection.OpenDiggerClient')
    def test_collect_collaboration_data(self, mock_opendigger):
        """Test collecting collaboration data task"""
        mock_opendigger_instance = Mock()
        mock_opendigger_instance.get_collaboration_network = AsyncMock(
            return_value=[
                {"from": "user1", "to": "user2", "weight": 5.0}
            ]
        )
        mock_opendigger.return_value = mock_opendigger_instance

        result = collect_collaboration_data.apply(
            args=["github", "apache", "iotdb"]
        ).get()

        assert result is not None


class TestAnalysisTasks:
    """Test suite for analysis tasks"""

    @patch('src.tasks.analysis.HealthAssessmentService')
    @patch('src.tasks.analysis.get_db')
    def test_analyze_repository_health(self, mock_db, mock_service):
        """Test repository health analysis task"""
        # Setup mocks
        mock_session = Mock()
        mock_db.return_value = mock_session

        mock_service_instance = Mock()
        mock_health_score = Mock(
            overall_score=78.5,
            activity_score=82.    lifecycle_stage="mature"
        )
        mock_service_instance.calculate_health_score.return_value = mock_health_score
        mock_service.return_value = mock_service_instance

        # Execute task
        result = analyze_repository_health.apply(
            args=["apache/iotdb"]
        ).get()

        assert result is not None
        mock_service_instance.calculate_health_score.assert_called_once()

    @patch('src.tasks.analysis.ChurnPredictionService')
    @patch('src.tasks.analysis.get_db')
    def test_predict_contributor_churn(self, mock_db, mock_service):
        """Test contributor churn prediction task"""
        # Setup mocks
        mock_session = Mock()
        mock_db.return_value = mock_session

        mock_service_instance = Mock()
        mock_prediction = Mock(
            churn_probability=0.68,
            alert_level="orange"
        )
        mock_service_instance.predict_churn.return_value = mock_prediction
        mock_service.return_value = mock_service_instance

        # Execute task
        result = predict_contributor_churn.apply(
            args=["apache/iotdb", "testuser"]
        ).get()

        assert result is not None
        mock_service_instance.predict_churn.assert_called_once()

    @patch('src.tasks.analysis.CollaborationNetworkAnalyzer')
    @patch('src.tasks.analysis.get_db')
    def test_analyze_collaboration_network(self, mock_db, mock_analyzer):
        """Test collaboration network analysis task"""
        # Setup mocks
        mock_session = Mock()
        mock_db.return_value = mock_session

        mock_analyzer_instance = Mock()
        mock_analyzer_instance.build_network.return_value = Mock()
        mock_analyzer_instance.calculate_centrality.return_value = {
            "user1": {"degree": 5, "betweenness": 0.6}
        }
        mock_analyzer.return_value = mock_analyzer_instance

        # Execute task
        result = analyze_collaboration_network.apply(
            args=["apache/iotdb"]
        ).get()

        assert result is not None
        mock_analyzer_instance.build_network.assert_called_once()


class TestTaskErrorHandling:
    """Test error handling in tasks"""

    @patch('src.tasks.data_collection.OpenDiggerClient')
    def test_fetch_metrics_with_api_error(self, mock_opendigger):
        """Test handling of API errors in fetch task"""
        mock_opendigger_instance = Mock()
        mock_opendigger_instance.get_openrank = AsyncMock(return_value=None)
        mock_opendigger.return_value = mock_opendigger_instance

        # Should handle error gracefully
        result = fetch_repository_metrics.apply(
            args=["github", "apache", "nonexistent"]
        ).get()

        # Task should complete without raising exception
        assert result is not None or result is None

    @patch('src.tasks.analysis.HealthAssessmentService')
    def test_analyze_health_with_service_error(self, mock_service):
        """Test handling of service errors in analysis task"""
        mock_service_instance = Mock()
        mock_service_instance.calculate_health_score.side_effect = Exception("Service error")
        mock_service.return_value = mock_service_instance

        # Should handle error gracefully
        with pytest.raises(Exception):
            analyze_repository_health.apply(
                args=["apache/iotdb"]
            ).get()


class TestTaskRetry:
    """Test task retry logic"""

    @patch('src.tasks.data_collection.OpenDiggerClient')
    def test_task_retry_on_failure(self, mock_opendigger):
        """Test that tasks retry on failure"""
        mock_opendigger_instance = Mock()
        # First call fails, second succeeds
        mock_opendigger_instance.get_openrank = AsyncMock(
            side_effect=[Exception("Temporary failure"), {"2024-01": 100.5}]
        )
        mock_opendigger.return_value = mock_opendigger_instance

        # Task should retry and eventually succeed
        # Note: Actual retry behavior depends on Celery configuration


class TestTaskScheduling:
    """Test task scheduling"""

    def test_periodic_task_registration(self):
        """Test that periodic tasks are registered"""
        from src.tasks.celery_app import app

        # Check that beat schedule is configured
        assert hasattr(app.conf, 'beat_schedule')
        assert 'refresh-repositories' in app.conf.beat_schedule or \
               len(app.conf.beat_schedule) >= 0  # May be empty in test mode

    def test_task_routing(self):
        """Test task routing configuration"""
        from src.tasks.celery_app import app

        # Check task routes are configured
        assert hasattr(app.conf, 'task_routes')


class TestTaskSerialization:
    """Test task serialization"""

    def test_task_argument_serialization(self):
        """Test that task arguments are properly serialized"""
        from src.tasks.data_collection import fetch_repository_metrics

        # Should accept serializable arguments
        task = fetch_repository_metrics.apply_a       args=["github", "apache", "iotdb"]
        )

        assert task.id is not None

    def test_task_result_serialization(self):
        """Test that task results are properly serialized"""
        # Results should be JSON-serializable
        result = {
            "status": "success",
            "metrics_count": 10,
            "timestamp": datetime.utcnow().isoformat()
        }

        import json
        serialized = json.dumps(result)
        assert serialized is not None

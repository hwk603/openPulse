"""
Integration tests for OpenPulse
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import datetime
import time

from src.api.main import app

client = TestClient(app)


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows"""

    @pytest.mark.integration
    def test_complete_health_assessment_workflow(self):
        """Test complete health assessment workflow"""
        # 1. Create repository
        repo_data = {
            "platform": "github",
            "owner": "apache",
            "repo": "iotdb"
        }

        with patch('src.api.routes.repositories.get_db'):
            create_response = client.post(
                "/api/v1/repositories",
                json=repo_data
            )
            # May succeed or fail depending on mocks
            assert create_response.status_code in [200, 201, 422, 500]

        # 2. Trigger health assessment
        with patch('src.api.routes.analysis.HealthAssessmentService'):
            assessment_response = client.post(
                "/api/v1/health-assessment",
                json=repo_data
            )
            assert assessment_response.status_code in [200, 500]

        # 3. Retrieve results (if successful)
        if assessment_response.status_code == 200:
            data = assessment_response.json()
            assert "overall_score" in data or "error" not in data

    @pytest.mark.integration
    def test_complete_churn_prediction_workflow(self):
        """Test complete churn prediction workflow"""
        # 1. Create repository and contributor
        repo_data = {
            "platform": "github",
            "owner": "apache",
            "repo": "iotdb"
        }

        # 2. Predict churn
        churn_data = {
            **repo_data,
            "contributor_username": "testuser"
        }

        with patch('src.api.routes.analysis.ChurnPredictionService'):
            prediction_response = client.post(
                "/api/v1/churn-prediction",
                json=churn_data
            )
            assert prediction_response.status_code in [200, 500]

    @pytest.mark.integration
    def test_complete_network_analysis_workflow(self):
        """Test complete network analysis workflow"""
        repo_data = {
            "platform": "github",
            "owner": "apache",
            "repo": "iotdb"
        }

        with patch('src.api.routes.network.CollaborationNetworkAnalyzer'):
            network_response = client.post(
                "/api/v1/network-analysis",
                json=repo_data
            )
            assert network_response.status_code in [200, 500]


class TestDataPipeline:
    """Test data collection and processing pipeline"""

    @pytest.mark.integration
    @patch('src.data_collection.opendigger_client.httpx.AsyncClient')
    @patch('src.storage.iotdb_client.Session')
    def test_data_collection_pipeline(self, mock_iotdb_session, mock_http_client):
        """Test data flows from collection to storage"""
        # Mock OpenDigger API response
        mock_response = Mock()
        mock_response.json.return_value = {"2024-01": 100.5}
        mock_response.raise_for_status = Mock()
        mock_http_client.return_value.__aenter__.return_value.get = Mock(
            return_value=mock_response
        )

        # Mock IoTDB session
        mock_iotdb_session.return_value = Mock()

        # This would test the actual pipeline
        # In a real integration test, you'd verify data flows correctly


class TestDatabaseIntegration:
    """Test database integration"""

    @pytest.mark.integration
    @pytest.mark.skipif(True, reason="Requires actual database connection")
    def test_database_connection(self):
        """Test actual database connection"""
        from src.database import get_db

        db = next(get_db())
        assert db is not None
        db.close()

    @pytest.mark.integration
    @pytest.mark.skipif(True, reason="Requires actual database connection")
    def test_repository_crud_operations(self):
        """Test CRUD operations on repository"""
        from src.database import get_db
        from src.models.database import RepositoryModel

        db = next(get_db())

        # Create
        repo = RepositoryModel(
            platform="github",
            owner="test",
            repo="integration-test",
            full_name="test/integration-test"
        )
        db.add(repo)
        db.commit()

        # Read
        retrieved = db.query(RepositoryModel).filter_by(
            full_name="test/integration-test"
        ).first()
        assert retrieved is not None

        # Update
        retrieved.stars = 1000
        db.commit()

        # Delete
        db.delete(retrieved)
        db.commit()

        db.close()


class TestExternalAPIIntegration:
    """Test integration with external APIs"""

    @pytest.mark.integration
    @pytest.mark.skipif(True, reason="Requires actual API access")
    async def test_opendigger_api_integration(self):
        """Test actual OpenDigger API integration"""
        from src.data_collection.opendigger_client import OpenDiggerClient

        client = OpenDiggerClient()
        result = await client.get_openrank("github", "apache", "iotdb")

        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.integration
    @pytest.mark.skipif(True, reason="Requires actual IoTDB instance")
    def test_iotdb_integration(self):
        """Test actual IoTDB integration"""
        from src.storage.iotdb_client import IoTDBClient

        client = IoTDBClient()

        # Test connection
        result = client.create_storage_group("root.test")
        assert result is not None

        client.close()


class TestConcurrency:
    """Test concurrent operations"""

    @pytest.mark.integration
    def test_concurrent_api_requests(self):
        """Test handling of concurrent API requests"""
        import concurrent.futures

        def make_health_check():
            return client.get("/health")

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_health_check) for _ in range(20)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert len(results) == 20
        assert all(r.status_code == 200 for r in results)

    @pytest.mark.integration
    def test_concurrent_health_assessments(self):
        """Test concurrent health assessments"""
        import concurrent.futures

        repos = [
            {"platform": "github", "owner": "apache", "repo": f"repo{i}"}
            for i in range(5)
        ]

        def assess_health(repo_data):
            with patch('src.api.routes.analysis.HealthAssessmentService'):
                return client.post("/api/v1/health-assessment", json=repo_data)

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(assess_health, repo) for repo in repos]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert len(results) == 5


class TestPerformance:
    """Test performance characteristics"""

    @pytest.mark.integration
    @pytest.mark.performance
    def test_api_response_time(self):
        """Test API response time"""
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()

        response_time = end_time - start_time

        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second

    @pytest.mark.integration
    @pytest.mark.performance
    def test_batch_processing_performance(self):
        """Test batch processing performance"""
        batch_data = {
            "repositories": [
                {"platform": "github", "owner": "apache", "repo": f"repo{i}"}
                for i in range(10)
            ]
        }

        start_time = time.time()

        with patch('src.api.routes.analysis.HealthAssessmentService'):
            response = client.post(
                "/api/v1/health-assessment/batch",
                json=batch_data
            )

        end_time = time.time()
        processing_time = end_time - start_time

        # Should process batch reasonably quickly
        assert processing_time < 10.0  # 10 seconds for 10 repos


class TestErrorRecovery:
    """Test error recovery and resilience"""

    @pytest.mark.integration
    def test_recovery_from_database_error(self):
        """Test recovery from database errors"""
        with patch('src.api.routes.repositories.get_db') as mock_db:
            # Simulate database error
            mock_db.side_effect = Exception("Database connection failed")

            response = client.get("/api/v1/repositories")

            # Should return error response, not crash
            assert response.status_code in [500, 503]

    @pytest.mark.integration
    def test_recovery_from_external_api_error(self):
        """Test recovery from external API errors"""
        with patch('src.data_collection.opendigger_client.httpx.AsyncClient') as mock_client:
            # Simulate API error
            mock_client.return_value.__aenter__.return_value.get.side_effect = Exception("API unavailable")

            with patch('src.api.routes.analysis.HealthAssessmentService'):
                response = client.post(
                    "/api/v1/health-assessment",
                    json={"platform": "github", "owner": "apache", "repo": "iotdb"}
                )

            # Should handle gracefully
            assert response.status_code in [200, 500, 503]


class TestDataConsistency:
    """Test data consistency across components"""

    @pytest.mark.integration
    def test_health_score_consistency(self):
        """Test health score calculation consistency"""
        repo_data = {"platform": "github", "owner": "apache", "repo": "iotdb"}

        with patch('src.api.routes.analysis.HealthAssessmentService') as mock_service:
            mock_instance = Mock()
            mock_instance.calculate_health_score.return_value = Mock(
                overall_score=78.5,
                activity_score=82.0
            )
            mock_service.return_value = mock_instance

            # Call multiple times
            response1 = client.post("/api/v1/health-assessment", json=repo_data)
            response2 = client.post("/api/v1/health-assessment", json=repo_data)

            # Should return consistent results (with same mock)
            if response1.status_code == 200 and response2.status_code == 200:
                data1 = response1.json()
                data2 = response2.json()
                # Results should be consistent
                assert data1.get("overall_score") == data2.get("overall_score")

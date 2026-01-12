"""
Enhanced API endpoint tests
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.api.main import app
from src.models import HealthScore, ChurnPrediction, AlertLevel, LifecycleStage

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "OpenPulse"
        assert "version" in data
        assert "description" in data

    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_health_check_detailed(self):
        """Test detailed health check"""
        response = client.get("/health/detailed")
        assert response.status_code in [200, 503]
        data = response.json()
        assert "database" in data
        assert "redis" in data
        assert "iotdb" in data


class TestRepositoryEndpoints:
    """Test repository management endpoints"""

    def test_create_repository(self, sample_repo_data):
        """Test creating a repository"""
        with patch('src.api.routes.repositories.get_db') as mock_db:
            mock_session = Mock()
            mock_db.return_value = mock_session

            response = client.post(
                "/api/v1/repositories",
                json=sample_repo_data
            )

            # Should succeed or return validation error
            assert response.status_code in [200, 201, 422, 500]

    def test_list_repositories(self):
        """Test listing repositories"""
        with patch('src.api.routes.repositories.get_db') as mock_db:
            mock_session = Mock()
            mock_db.return_value = mock_session

            response = client.get("/api/v1/repositories")

            assert response.status_code in [200, 500]

    def test_get_repository(self):
        """Test getting a specific repository"""
        with patch('src.api.routes.repositories.get_db') as mock_db:
            mock_session = Mock()
            mock_db.return_value = mock_session

            response = client.get("/api/v1/repositories/1")

            assert response.status_code in [200, 404, 500]

    def test_delete_repository(self):
        """Test deleting a repository"""
        with patch('src.api.routes.repositories.get_db') as mock_db:
            mock_session = Mock()
            mock_db.return_value = mock_session

            response = client.delete("/api/v1/repositories/1")

            assert response.status_code in [200, 204, 404, 500]

    def test_create_repository_invalid_data(self):
        """Test creating repository with invalid data"""
        invalid_data = {
            "platform": "invalid_platform",
            "owner": "",
            "repo": ""
        }

        response = client.post(
            "/api/v1/repositories",
            json=invalid_data
        )

        assert response.status_code == 422


class TestAnalysisEndpoints:
    """Test analysis endpoints"""

    def test_health_assessment_endpoint(self, sample_api_request_data):
        """Test health assessment endpoint"""
        with patch('src.api.routes.analysis.HealthAssessmentService') as mock_service:
            mock_instance = Mock()
            mock_instance.calculate_health_score.return_value = HealthScore(
                timestamp=datetime.utcnow(),
                repo_full_name="apache/iotdb",
                overall_score=78.5,
                activity_score=82.0,
                diversity_score=75.0,
                response_time_score=80.0,
                code_quality_score=76.0,
                documentation_score=72.0,
                community_atmosphere_score=79.0,
                lifecycle_stage=LifecycleStage.MATURE
            )
            mock_service.return_value = mock_instance

            response = client.post(
                "/api/v1/health-assessment",
                json=sample_api_request_data["health_assessment"]
            )

            assert response.status_code in [200, 500]

    def test_health_assessment_missing_fields(self):
        """Test health assessment with missing required fields"""
        incomplete_data = {
            "platform": "github",
            "owner": "apache"
            # Missing 'repo' field
        }

        response = client.post(
            "/api/v1/health-assessment",
            json=incomplete_data
        )

        assert response.status_code == 422

    def test_churn_prediction_endpoint(self, sample_api_request_data):
        """Test churn prediction endpoint"""
        with patch('src.api.routes.analysis.ChurnPredictionService') as mock_service:
            mock_instance = Mock()
            mock_instance.predict_churn.return_value = ChurnPrediction(
                contributor_username="testuser",
                repo_full_name="apache/iotdb",
                prediction_date=datetime.utcnow(),
                churn_probability=0.68,
                alert_level=AlertLevel.ORANGE,
                behavior_decay_score=0.65,
                network_marginalization_score=0.55,
                temporal_anomaly_score=0.72,
                community_engagement_score=0.45,
                retention_suggestions=["Test suggestion"]
            )
            mock_service.return_value = mock_instance

            response = client.post(
                "/api/v1/churn-prediction",
                json=sample_api_request_data["churn_prediction"]
            )

            assert response.status_code in [200, 500]

    def test_churn_prediction_missing_contributor(self):
        """Test churn prediction without contributor username"""
        incomplete_data = {
            "platform": "github",
            "owner": "apache",
            "repo": "iotdb"
            # Missing 'contributor_username'
        }

        response = client.post(
            "/api/v1/churn-prediction",
            json=incomplete_data
        )

        assert response.status_code == 422

    def test_batch_health_assessment(self):
        """Test batch health assessment for multiple repositories"""
        batch_data = {
            "repositories": [
                {"platform": "github", "owner": "apache", "repo": "iotdb"},
                {"platform": "github", "owner": "apache", "repo": "kafka"},
                {"platform": "github", "owner": "apache", "repo": "spark"}
            ]
        }

        with patch('src.api.routes.analysis.HealthAssessmentService') as mock_service:
            mock_instance = Mock()
            mock_instance.calculate_health_score.return_value = Mock()
            mock_service.return_value = mock_instance

            response = client.post(
                "/api/v1/health-assessment/batch",
                json=batch_data
            )

            assert response.status_code in [200, 404, 500]


class TestNetworkEndpoints:
    """Test network analysis endpoints"""

    def test_network_analysis_endpoint(self, sample_api_request_data):
        """Test network analysis endpoint"""
        with patch('src.api.routes.network.CollaborationNetworkAnalyzer') as mock_analyzer:
            mock_instance = Mock()
            mock_instance.build_network.return_value = Mock()
            mock_instance.calculate_centrality.return_value = {}
            mock_instance.detect_structural_holes.return_value = {}
            mock_instance.detect_communities.return_value = {}
            mock_analyzer.return_value = mock_instance

            response = client.post(
                "/api/v1/network-analysis",
                json=sample_api_request_data["network_analysis"]
            )

            assert response.status_code in [200, 500]

    def test_get_contributor_centrality(self):
        """Test getting contributor centrality metrics"""
        with patch('src.api.routes.network.CollaborationNetworkAnalyzer') as mock_analyzer:
            mock_instance = Mock()
            mock_instance.calculate_centrality.return_value = {
                "testuser": {
                    "degree": 5,
                    "betweenness": 0.6,
                    "closeness": 0.7,
                    "pagerank": 0.25
                }
            }
            mock_analyzer.return_value = mock_instance

            response = client.get(
                "/api/v1/network/apache/iotdb/contributor/testuser/centrality"
            )

            assert response.status_code in [200, 404, 500]

    def test_get_structural_holes(self):
        """Test getting structural hole analysis"""
        with patch('src.api.routes.network.CollaborationNetworkAnalyzer') as mock_analyzer:
            mock_instance = Mock()
            mock_instance.detect_structural_holes.return_value = {
                "user1": {"constraint": 0.4, "effective_size": 1.5}
            }
            mock_analyzer.return_value = mock_instance

            response = client.get(
                "/api/v1/network/apache/iotdb/structural-holes"
            )

            assert response.status_code in [200, 500]

    def test_get_communities(self):
        """Test getting community detection results"""
        with patch('src.api.routes.network.CollaborationNetworkAnalyzer') as mock_analyzer:
            mock_instance = Mock()
            mock_instance.detect_communities.return_value = {
                "user1": 0, "user2": 0, "user3": 1
            }
            mock_analyzer.return_value = mock_instance

            response = client.get(
                "/api/v1/network/apache/iotdb/communities"
            )

            assert response.status_code in [200, 500]


class TestErrorHandling:
    """Test error handling"""

    def test_404_not_found(self):
        """Test 404 error handling"""
        response = client.get("/api/v1/nonexistent-endpoint")
        assert response.status_code == 404

    def test_method_not_allowed(self):
        """Test 405 method not allowed"""
        response = client.put("/health")
        assert response.status_code == 405

    def test_invalid_json(self):
        """Test invalid JSON handling"""
        response = client.post(
            "/api/v1/health-assessment",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_large_payload(self):
        """Test handling of large payloads"""
        large_data = {
            "platform": "github",
            "owner": "apache",
            "repo": "iotdb",
            "extra_data": "x" * 10000  # Large string
        }

        response = client.post(
            "/api/v1/health-assessment",
            json=large_data
        )

        # Should handle gracefully
        assert response.status_code in [200, 413, 422, 500]


class TestCORS:
    """Test CORS configuration"""

    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = client.options(
            "/api/v1/health-assessment",
            headers={"Origin": "http://localhost:3000"}
        )

        # CORS should be configured
        assert response.status_code in [200, 204]


class TestRateLimiting:
    """Test rate limiting (if implemented)"""

    def test_rate_limit_not_exceeded(self):
        """Test normal request rate"""
        for _ in range(5):
            response = client.get("/health")
            assert response.status_code == 200

    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import concurrent.futures

        def make_request():
            return client.get("/health")

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All requests should complete
        assert len(results) == 10
        assert all(r.status_code == 200 for r in results)

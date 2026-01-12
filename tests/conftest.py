"""
Test configuration and fixtures
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_repo_data() -> Dict[str, Any]:
    """Sample repository data for testing"""
    return {
        "platform": "github",
        "owner": "apache",
        "repo": "iotdb",
        "full_name": "apache/iotdb"
    }


@pytest.fixture
def sample_openrank_data() -> Dict[str, float]:
    """Sample OpenRank data"""
    return {
        "2024-01": 100.5,
        "2024-02": 105.2,
        "2024-03": 110.8,
        "2024-04": 108.3,
        "2024-05": 112.6
    }


@pytest.fixture
def sample_activity_data() -> Dict[str, float]:
    """Sample activity data"""
    return {
        "2024-01": 250.0,
        "2024-02": 280.0,
        "2024-03": 300.0,
        "2024-04": 290.0,
        "2024-05": 310.0
    }


@pytest.fixture
def sample_contributors_data() -> Dict[str, int]:
    """Sample contributors data"""
    return {
        "2024-01": 45,
        "2024-02": 48,
        "2024-03": 52,
        "2024-04": 50,
        "2024-05": 55
    }


@pytest.fixture
def sample_collaboration_data() -> list:
    """Sample collaboration network data"""
    return [
        {"from": "user1", "to": "user2", "weight": 5.0, "timestamp": "2024-01-15"},
        {"from": "user1", "to": "user3", "weight": 3.0, "timestamp": "2024-01-16"},
        {"from": "user2", "to": "user3", "weight": 4.0, "timestamp": "2024-01-17"},
        {"from": "user2", "to": "user4", "weight": 2.0, "timestamp": "2024-01-18"},
        {"from": "user3", "to": "user4", "weight": 6.0, "timestamp": "2024-01-19"},
        {"from": "user4", "to": "user5", "weight": 3.0, "timestamp": "2024-01-20"},
    ]


@pytest.fixture
def sample_health_score_data() -> Dict[str, Any]:
    """Sample health score data"""
    return {
        "timestamp": datetime.utcnow(),
        "repo_full_name": "apache/iotdb",
        "overall_score": 78.5,
        "activity_score": 82.0,
        "diversity_score": 75.0,
        "response_time_score": 80.0,
        "code_quality_score": 76.0,
        "documentation_score": 72.0,
        "community_atmosphere_score": 79.0,
        "lifecycle_stage": "mature"
    }


@pytest.fixture
def sample_churn_prediction_data() -> Dict[str, Any]:
    """Sample churn prediction data"""
    return {
        "contributor_username": "testuser",
        "repo_full_name": "apache/iotdb",
        "prediction_date": datetime.utcnow(),
        "churn_probability": 0.68,
        "alert_level": "orange",
        "behavior_decay_score": 0.65,
        "network_marginalization_score": 0.55,
        "temporal_anomaly_score": 0.72,
        "community_engagement_score": 0.45,
        "retention_suggestions": [
            "Assign mentorship role",
            "Invite to core team meetings",
            "Recognize recent contributions"
        ]
    }


@pytest.fixture
def mock_opendigger_client():
    """Mock OpenDigger client"""
    mock = Mock()
    mock.get_openrank = AsyncMock(return_value={
        "2024-01": 100.5,
        "2024-02": 105.2,
        "2024-03": 110.8
    })
    mock.get_activity = AsyncMock(return_value={
        "2024-01": 250.0,
        "2024-02": 280.0,
        "2024-03": 300.0
    })
    mock.get_contributors = AsyncMock(return_value={
        "2024-01": 45,
        "2024-02": 48,
        "2024-03": 52
    })
    return mock


@pytest.fixture
def mock_iotdb_client():
    """Mock IoTDB client"""
    mock = Mock()
    mock.insert_metrics = Mock(return_value=True)
    mock.query_metrics = Mock(return_value={
        "openrank": [100.5, 105.2, 110.8],
        "activity": [250.0, 280.0, 300.0],
        "contributors": [45, 48, 52]
    })
    mock.create_storage_group = Mock(return_value=True)
    mock.create_timeseries = Mock(return_value=True)
    return mock


@pytest.fixture
def mock_network_analyzer():
    """Mock network analyzer"""
    mock = Mock()
    mock.build_network = Mock()
    mock.calculate_centrality = Mock(return_value={
        "user1": {"degree": 2, "betweenness": 0.5, "closeness": 0.6, "pagerank": 0.25},
        "user2": {"degree": 3, "betweenness": 0.7, "closeness": 0.7, "pagerank": 0.30},
        "user3": {"degree": 3, "betweenness": 0.6, "closeness": 0.65, "pagerank": 0.28}
    })
    mock.detect_structural_holes = Mock(return_value={
        "user1": {"constraint": 0.4, "effective_size": 1.5},
        "user2": {"constraint": 0.3, "effective_size": 2.0}
    })
    mock.detect_communities = Mock(return_value={
        "user1": 0, "user2": 0, "user3": 1, "user4": 1
    })
    return mock


@pytest.fixture
def mock_database_session():
    """Mock database session"""
    mock = Mock()
    mock.add = Mock()
    mock.commit = Mock()
    mock.refresh = Mock()
    mock.query = Mock()
    mock.close = Mock()
    return mock


@pytest.fixture
def sample_metrics_data() -> Dict[str, Any]:
    """Sample metrics data for IoTDB"""
    return {
        "repo_full_name": "apache/iotdb",
        "timestamp": datetime.utcnow(),
        "metrics": {
            "openrank": 110.5,
            "activity": 300.0,
            "active_contributors": 52,
            "commits": 150,
            "pull_requests": 45,
            "issues_opened": 30,
            "issues_closed": 28,
            "stars": 5000,
            "forks": 1200
        }
    }


@pytest.fixture
def sample_api_request_data() -> Dict[str, Any]:
    """Sample API request data"""
    return {
        "health_assessment": {
            "platform": "github",
            "owner": "apache",
            "repo": "iotdb"
        },
        "churn_prediction": {
            "platform": "github",
            "owner": "apache",
            "repo": "iotdb",
            "contributor_username": "testuser"
        },
        "network_analysis": {
            "platform": "github",
            "owner": "apache",
            "repo": "iotdb"
        },
        "repository": {
            "platform": "github",
            "owner": "apache",
            "repo": "iotdb"
        }
    }

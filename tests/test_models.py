"""
Test database models and schemas
"""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import (
    HealthScore, ChurnPrediction, AlertLevel, LifecycleStage,
    CollaborationNetwork, StructuralHoleRisk, RiskAssessmentReport
)
from src.models.database import (
    Base, RepositoryModel, ContributorModel, HealthScoreModel,
    ChurnPredictionModel, AnalysisTaskModel
)


class TestPydanticModels:
    """Test Pydantic schema models"""

    def test_health_score_model(self):
        """Test HealthScore model"""
        health_score = HealthScore(
            timestamp=datetime.utcnow(),
            repo_full_name="test/repo",
            overall_score=75.5,
            activity_score=80.0,
            diversity_score=70.0,
            response_time_score=75.0,
            code_quality_score=80.0,
            documentation_score=70.0,
            community_atmosphere_score=75.0,
            lifecycle_stage=LifecycleStage.MATURE
        )

        assert health_score.overall_score == 75.5
        assert health_score.lifecycle_stage == LifecycleStage.MATURE
        assert health_score.repo_full_name == "test/repo"

    def test_health_score_validation(self):
        """Test HealthScore validation"""
        with pytest.raises(ValueError):
            HealthScore(
                timestamp=datetime.utcnow(),
                repo_full_name="test/repo",
                overall_score=150.0,  # Invalid: > 100
                activity_score=80.0,
                diversity_score=70.0,
                response_time_score=75.0,
                code_quality_score=80.0,
                documentation_score=70.0,
                community_atmosphere_score=75.0,
                lifecycle_stage=LifecycleStage.MATURE
            )

    def test_churn_prediction_model(self):
        """Test ChurnPrediction model"""
        prediction = ChurnPrediction(
            contributor_username="testuser",
            repo_full_name="test/repo",
            prediction_date=datetime.utcnow(),
            churn_probability=0.65,
            alert_level=AlertLevel.ORANGE,
            behavior_decay_score=0.6,
            network_marginalization_score=0.5,
            temporal_anomaly_score=0.7,
            community_engagement_score=0.4,
            retention_suggestions=["Test suggestion"]
        )

        assert prediction.churn_probability == 0.65
        assert prediction.alert_level == AlertLevel.ORANGE
        assert len(prediction.retention_suggestions) == 1

    def test_churn_prediction_validation(self):
        """Test ChurnPrediction validation"""
        with pytest.raises(ValueError):
            ChurnPrediction(
                contributor_username="testuser",
                repo_full_name="test/repo",
                prediction_date=datetime.utcnow(),
                churn_probability=1.5,  # Invalid: > 1.0
                alert_level=AlertLevel.ORANGE,
                behavior_decay_score=0.6,
                network_marginalization_score=0.5,
                temporal_anomaly_score=0.7,
                community_engagement_score=0.4,
                retention_suggestions=[]
            )

    def test_alert_levels(self):
        """Test AlertLevel enum"""
        assert AlertLevel.GREEN.value == "green"
        assert AlertLevel.YELLOW.value == "yellow"
        assert AlertLevel.ORANGE.value == "orange"
        assert AlertLevel.RED.value == "red"

        # Test enum comparison
        assert AlertLevel.RED > AlertLevel.ORANGE
        assert AlertLevel.YELLOW < AlertLevel.ORANGE

    def test_lifecycle_stages(self):
        """Test LifecycleStage enum"""
        assert LifecycleStage.EMBRYONIC.value == "embryonic"
        assert LifecycleStage.GROWTH.value == "growth"
        assert LifecycleStage.MATURE.value == "mature"
        assert LifecycleStage.DECLINE.value == "decline"

    def test_collaboration_network_model(self):
        """Test CollaborationNetwork model"""
        network = CollaborationNetwork(
            repo_full_name="test/repo",
            timestamp=datetime.utcnow(),
            nodes=["user1", "user2", "user3"],
            edges=[
                {"from": "user1", "to": "user2", "weight": 5.0},
                {"from": "user2", "to": "user3", "weight": 3.0}
            ],
            centrality_metrics={
                "user1": {"degree": 2, "betweenness": 0.5}
            }
        )

        assert len(network.nodes) == 3
        assert len(network.edges) == 2
        assert "user1" in network.centrality_metrics

    def test_structural_hole_risk_model(self):
        """Test StructuralHoleRisk model"""
        risk = StructuralHoleRisk(
            repo_full_name="test/repo",
            contributor_username="testuser",
            timestamp=datetime.utcnow(),
            constraint_score=0.4,
            effective_size=1.5,
            risk_level="high",
            connected_communities=2
        )

        assert risk.constraint_score == 0.4
        assert risk.risk_level == "high"
        assert risk.connected_communities == 2

    def test_risk_assessment_report_model(self):
        """Test RiskAssessmentReport model"""
        report = RiskAssessmentReport(
            repo_full_name="test/repo",
            timestamp=datetime.utcnow(),
            overall_risk_score=0.65,
            bus_factor=3,
            key_contributors=["user1", "user2", "user3"],
            structural_hole_risks=[],
            churn_predictions=[],
            recommendations=["Increase contributor diversity"]
        )

        assert report.overall_risk_score == 0.65
        assert report.bus_factor == 3
        assert len(report.key_contributors) == 3

    def test_model_json_serialization(self):
        """Test model JSON serialization"""
        health_score = HealthScore(
            timestamp=datetime.utcnow(),
            repo_full_name="test/repo",
            overall_score=75.5,
            activity_score=80.0,
            diversity_score=70.0,
            response_time_score=75.0,
            code_quality_score=80.0,
            documentation_score=70.0,
            community_atmosphere_score=75.0,
            lifecycle_stage=LifecycleStage.MATURE
        )

        json_data = health_score.model_dump_json()
        assert json_data is not None
        assert "overall_score" in json_data


class TestDatabaseModels:
    """Test SQLAlchemy database models"""

    @pytest.fixture
    def db_session(self):
        """Create in-memory database session for testing"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    def test_repository_model(self, db_session):
        """Test RepositoryModel"""
        repo = RepositoryModel(
            platform="github",
            owner="apache",
            repo="iotdb",
            full_name="apache/iotdb",
            description="Apache IoTDB",
            stars=5000,
            forks=1200,
            is_active=True
        )

        db_session.add(repo)
        db_session.commit()

        assert repo.id is not None
        assert repo.full_name == "apache/iotdb"
        assert repo.is_active is True

    def test_contributor_model(self, db_session):
        """Test ContributorModel"""
        contributor = ContributorModel(
            username="testuser",
            platform="github",
            email="test@example.com",
            name="Test User",
            total_commits=150,
            total_prs=45,
            total_issues=30
        )

        db_session.add(contributor)
        db_session.commit()

        assert contributor.id is not None
        assert contributor.username == "testuser"
        assert contributor.total_commits == 150

    def test_health_score_model_db(self, db_session):
        """Test HealthScoreModel database operations"""
        # First create a repository
        repo = RepositoryModel(
            platform="github",
            owner="apache",
            repo="iotdb",
            full_name="apache/iotdb"
        )
        db_session.add(repo)
        db_session.commit()

        # Create health score
        health_score = HealthScoreModel(
            repository_id=repo.id,
            timestamp=datetime.utcnow(),
            overall_score=75.5,
            activity_score=80.0,
            diversity_score=70.0,
            response_time_score=75.0,
            code_quality_score=80.0,
            documentation_score=70.0,
            community_atmosphere_score=75.0,
            lifecycle_stage="mature"
        )

        db_session.add(health_score)
        db_session.commit()

        assert health_score.id is not None
        assert health_score.repository_id == repo.id

    def test_churn_prediction_model_db(self, db_session):
        """Test ChurnPredictionModel database operations"""
        # Create repository and contributor
        repo = RepositoryModel(
            platform="github",
            owner="apache",
            repo="iotdb",
            full_name="apache/iotdb"
        )
        contributor = ContributorModel(
            username="testuser",
            platform="github"
        )

        db_session.add(repo)
        db_session.add(contributor)
        db_session.commit()

        # Create churn prediction
        prediction = ChurnPredictionModel(
            repository_id=repo.id,
            contributor_id=contributor.id,
            prediction_date=datetime.utcnow(),
            churn_probability=0.65,
            alert_level="orange",
            behavior_decay_score=0.6,
            network_marginalization_score=0.5,
            temporal_anomaly_score=0.7,
            community_engagement_score=0.4
        )

        db_session.add(prediction)
        db_session.commit()

        assert prediction.id is not None
        assert prediction.churn_probability == 0.65

    def test_analysis_task_model(self, db_session):
        """Test AnalysisTaskModel"""
        repo = RepositoryModel(
            platform="github",
            owner="apache",
            repo="iotdb",
            full_name="apache/iotdb"
        )
        db_session.add(repo)
        db_session.commit()

        task = AnalysisTaskModel(
            repository_id=repo.id,
            task_type="health_assessment",
            status="pending",
            created_at=datetime.utcnow()
        )

        db_session.add(task)
        db_session.commit()

        assert task.id is not None
        assert task.status == "pending"

        # Update task status
        task.status = "completed"
        task.completed_at = datetime.utcnow()
        db_session.commit()

        assert task.status == "completed"
        assert task.completed_at is not None

    def test_repository_relationships(self, db_session):
        """Test repository model relationships"""
        repo = RepositoryModel(
            platform="github",
            owner="apache",
            repo="iotdb",
            full_name="apache/iotdb"
        )
        db_session.add(repo)
        db_session.commit()

        # Add health scores
        for i in range(3):
            health_score = HealthScoreModel(
                repository_id=repo.id,
                timestamp=datetime.utcnow(),
                overall_score=75.0 + i,
                activity_score=80.0,
                diversity_score=70.0,
                response_time_score=75.0,
                code_quality_score=80.0,
                documentation_score=70.0,
                community_atmosphere_score=75.0,
                lifecycle_stage="mature"
            )
            db_session.add(health_score)

        db_session.commit()

        # Query repository with health scores
        repo_with_scores = db_session.query(RepositoryModel).filter_by(
            id=repo.id
        ).first()

        assert repo_with_scores is not None
        # Relationship should be accessible
        assert hasattr(repo_with_scores, 'health_scores')

    def test_model_timestamps(self, db_session):
        """Test automatic timestamp creation"""
        repo = RepositoryModel(
            platform="github",
            owner="apache",
            repo="iotdb",
            full_name="apache/iotdb"
        )

        db_session.add(repo)
        db_session.commit()

        assert repo.created_at is not None
        assert repo.updated_at is not None
        assert repo.created_at <= repo.updated_at

    def test_unique_constraints(self, db_session):
        """Test unique constraints"""
        repo1 = RepositoryModel(
            platform="github",
            owner="apache",
            repo="iotdb",
            full_name="apache/iotdb"
        )

        repo2 = RepositoryModel(
            platform="github",
            owner="apache",
            repo="iotdb",
            full_name="apache/iotdb"
        )

        db_session.add(repo1)
        db_session.commit()

        db_session.add(repo2)

        # Should raise integrity error due to unique constraint
        with pytest.raises(Exception):
            db_session.commit()

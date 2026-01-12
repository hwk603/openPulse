"""
SQLAlchemy database models for PostgreSQL
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class RepositoryModel(Base):
    """Repository database model"""
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False)
    owner = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    full_name = Column(String(512), unique=True, nullable=False, index=True)
    url = Column(String(512))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_analyzed = Column(DateTime)
    is_active = Column(Boolean, default=True)

    # Relationships
    health_scores = relationship("HealthScoreModel", back_populates="repository")
    churn_predictions = relationship("ChurnPredictionModel", back_populates="repository")


class ContributorModel(Base):
    """Contributor database model"""
    __tablename__ = "contributors"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False, index=True)
    platform = Column(String(50), nullable=False)
    contributions = Column(Integer, default=0)
    openrank = Column(Float, default=0.0)
    first_contribution = Column(DateTime)
    last_contribution = Column(DateTime)
    is_core = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    churn_predictions = relationship("ChurnPredictionModel", back_populates="contributor")


class HealthScoreModel(Base):
    """Health score database model"""
    __tablename__ = "health_scores"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)

    # Scores
    overall_score = Column(Float, nullable=False)
    activity_score = Column(Float, nullable=False)
    diversity_score = Column(Float, nullable=False)
    response_time_score = Column(Float, nullable=False)
    code_quality_score = Column(Float, nullable=False)
    documentation_score = Column(Float, nullable=False)
    community_atmosphere_score = Column(Float, nullable=False)

    # Lifecycle
    lifecycle_stage = Column(String(50), nullable=False)

    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    repository = relationship("RepositoryModel", back_populates="health_scores")


class ChurnPredictionModel(Base):
    """Churn prediction database model"""
    __tablename__ = "churn_predictions"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    contributor_id = Column(Integer, ForeignKey("contributors.id"), nullable=False)
    prediction_date = Column(DateTime, nullable=False, index=True)

    # Prediction
    churn_probability = Column(Float, nullable=False)
    alert_level = Column(String(20), nullable=False)

    # Contributing factors
    behavior_decay_score = Column(Float, default=0.0)
    network_marginalization_score = Column(Float, default=0.0)
    temporal_anomaly_score = Column(Float, default=0.0)
    community_engagement_score = Column(Float, default=0.0)

    # Recommendations
    retention_suggestions = Column(JSON)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    repository = relationship("RepositoryModel", back_populates="churn_predictions")
    contributor = relationship("ContributorModel", back_populates="churn_predictions")


class AnalysisTaskModel(Base):
    """Analysis task database model"""
    __tablename__ = "analysis_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(255), unique=True, nullable=False, index=True)
    task_type = Column(String(100), nullable=False)
    repo_full_name = Column(String(512), nullable=False)
    status = Column(String(50), default="pending")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    # Results
    error_message = Column(Text)
    result = Column(JSON)

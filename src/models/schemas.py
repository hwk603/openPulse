"""
Data models for OpenPulse platform
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class LifecycleStage(str, Enum):
    """Community lifecycle stages"""
    EMBRYONIC = "embryonic"
    GROWTH = "growth"
    MATURE = "mature"
    DECLINE = "decline"
    REVIVAL = "revival"


class AlertLevel(str, Enum):
    """Alert severity levels"""
    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"
    RED = "red"


class Repository(BaseModel):
    """Repository information"""
    platform: str = Field(..., description="Platform (github/gitee)")
    owner: str = Field(..., description="Repository owner")
    name: str = Field(..., description="Repository name")
    full_name: str = Field(..., description="Full repository name")
    url: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Contributor(BaseModel):
    """Contributor information"""
    username: str
    platform: str
    contributions: int = 0
    openrank: float = 0.0
    first_contribution: Optional[datetime] = None
    last_contribution: Optional[datetime] = None
    is_core: bool = False


class ActivityMetrics(BaseModel):
    """Activity metrics for a repository"""
    timestamp: datetime
    repo_full_name: str

    # Basic metrics
    stars: int = 0
    forks: int = 0
    watchers: int = 0
    open_issues: int = 0

    # Activity metrics
    commits: int = 0
    pull_requests: int = 0
    issues_opened: int = 0
    issues_closed: int = 0

    # Contributor metrics
    active_contributors: int = 0
    new_contributors: int = 0

    # OpenRank
    openrank: float = 0.0


class HealthScore(BaseModel):
    """Community health score"""
    timestamp: datetime
    repo_full_name: str

    # Overall score
    overall_score: float = Field(..., ge=0, le=100, description="Overall health score (0-100)")

    # Dimension scores
    activity_score: float = Field(..., ge=0, le=100)
    diversity_score: float = Field(..., ge=0, le=100)
    response_time_score: float = Field(..., ge=0, le=100)
    code_quality_score: float = Field(..., ge=0, le=100)
    documentation_score: float = Field(..., ge=0, le=100)
    community_atmosphere_score: float = Field(..., ge=0, le=100)

    # Lifecycle
    lifecycle_stage: LifecycleStage

    # Metadata
    calculated_at: datetime = Field(default_factory=datetime.utcnow)


class ChurnPrediction(BaseModel):
    """Contributor churn prediction"""
    contributor_username: str
    repo_full_name: str
    prediction_date: datetime

    # Prediction
    churn_probability: float = Field(..., ge=0, le=1, description="Probability of churning (0-1)")
    alert_level: AlertLevel

    # Contributing factors
    behavior_decay_score: float = 0.0
    network_marginalization_score: float = 0.0
    temporal_anomaly_score: float = 0.0
    community_engagement_score: float = 0.0

    # Recommendations
    retention_suggestions: List[str] = []


class StructuralHoleRisk(BaseModel):
    """Structural hole risk assessment"""
    repo_full_name: str
    analysis_date: datetime

    # Key bridge nodes
    bridge_contributors: List[Dict[str, Any]] = []

    # Risk metrics
    bus_factor: int = Field(..., description="Number of people whose absence would cripple the project")
    structural_vulnerability_score: float = Field(..., ge=0, le=1)

    # Network metrics
    network_density: float = 0.0
    clustering_coefficient: float = 0.0
    average_path_length: float = 0.0


class CollaborationNetwork(BaseModel):
    """Collaboration network snapshot"""
    repo_full_name: str
    snapshot_date: datetime

    # Network structure
    nodes: List[Dict[str, Any]] = []  # Contributors
    edges: List[Dict[str, Any]] = []  # Collaboration relationships

    # Network metrics
    node_count: int = 0
    edge_count: int = 0
    density: float = 0.0

    # Community structure
    communities: List[List[str]] = []
    modularity: float = 0.0


class RiskAssessmentReport(BaseModel):
    """OSPO risk assessment report"""
    repo_full_name: str
    report_date: datetime

    # Overall assessment
    health_score: float = Field(..., ge=0, le=100)
    risk_level: AlertLevel
    lifecycle_stage: LifecycleStage

    # Risk factors
    churn_risk: str = "low"  # low/medium/high
    bus_factor: int = 0
    structural_hole_risk: str = "low"

    # Trends
    openrank_trend: str = "stable"  # rising/stable/declining
    activity_trend: str = "stable"
    contributor_trend: str = "stable"

    # Recommendations
    recommendations: List[str] = []
    key_concerns: List[str] = []

    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class AnalysisTask(BaseModel):
    """Analysis task"""
    task_id: str
    task_type: str  # health_assessment, churn_prediction, network_analysis, etc.
    repo_full_name: str
    status: str = "pending"  # pending, running, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

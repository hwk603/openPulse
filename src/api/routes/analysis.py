"""
Analysis routes for health assessment and churn prediction
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from src.services import HealthAssessmentService, ChurnPredictionService
from src.models import HealthScore, ChurnPrediction, AlertLevel

router = APIRouter()


class HealthAssessmentRequest(BaseModel):
    """Request model for health assessment"""
    platform: str
    owner: str
    repo: str


class ChurnPredictionRequest(BaseModel):
    """Request model for churn prediction"""
    platform: str
    owner: str
    repo: str
    contributor_username: str


class HealthAssessmentResponse(BaseModel):
    """Response model for health assessment"""
    repo_full_name: str
    timestamp: datetime
    overall_score: float
    activity_score: float
    diversity_score: float
    response_time_score: float
    code_quality_score: float
    documentation_score: float
    community_atmosphere_score: float
    lifecycle_stage: str


class ChurnPredictionResponse(BaseModel):
    """Response model for churn prediction"""
    contributor_username: str
    repo_full_name: str
    churn_probability: float
    alert_level: str
    retention_suggestions: List[str]


@router.post("/health-assessment", response_model=HealthAssessmentResponse)
async def assess_health(request: HealthAssessmentRequest):
    """
    Assess community health for a repository

    Args:
        request: Health assessment request with platform, owner, repo

    Returns:
        Health assessment results
    """
    try:
        repo_full_name = f"{request.owner}/{request.repo}"

        service = HealthAssessmentService()
        health_score = service.calculate_health_score(repo_full_name)

        return HealthAssessmentResponse(
            repo_full_name=health_score.repo_full_name,
            timestamp=health_score.timestamp,
            overall_score=health_score.overall_score,
            activity_score=health_score.activity_score,
            diversity_score=health_score.diversity_score,
            response_time_score=health_score.response_time_score,
            code_quality_score=health_score.code_quality_score,
            documentation_score=health_score.documentation_score,
            community_atmosphere_score=health_score.community_atmosphere_score,
            lifecycle_stage=health_score.lifecycle_stage.value,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health assessment failed: {str(e)}")


@router.post("/churn-prediction", response_model=ChurnPredictionResponse)
async def predict_churn(request: ChurnPredictionRequest):
    """
    Predict contributor churn probability

    Args:
        request: Churn prediction request with platform, owner, repo, contributor

    Returns:
        Churn prediction results
    """
    try:
        repo_full_name = f"{request.owner}/{request.repo}"

        service = ChurnPredictionService()
        prediction = service.predict_churn(repo_full_name, request.contributor_username)

        return ChurnPredictionResponse(
            contributor_username=prediction.contributor_username,
            repo_full_name=prediction.repo_full_name,
            churn_probability=prediction.churn_probability,
            alert_level=prediction.alert_level.value,
            retention_suggestions=prediction.retention_suggestions,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Churn prediction failed: {str(e)}")


@router.get("/health-history/{platform}/{owner}/{repo}")
async def get_health_history(
    platform: str,
    owner: str,
    repo: str,
    days: int = 90
):
    """
    Get health score history for a repository

    Args:
        platform: Platform name (github/gitee)
        owner: Repository owner
        repo: Repository name
        days: Number of days of history to retrieve

    Returns:
        List of historical health scores
    """
    try:
        repo_full_name = f"{owner}/{repo}"

        # TODO: Implement historical query from IoTDB
        # For now, return placeholder
        return {
            "repo_full_name": repo_full_name,
            "history": [],
            "message": "Historical data retrieval not yet implemented"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")

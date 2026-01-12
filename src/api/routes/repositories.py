"""
Repository management routes
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from src.data_collection import OpenDiggerClient
from src.storage import IoTDBClient

router = APIRouter()


class RepositoryRequest(BaseModel):
    """Request model for adding a repository"""
    platform: str
    owner: str
    repo: str


class RepositoryResponse(BaseModel):
    """Response model for repository info"""
    platform: str
    owner: str
    repo: str
    full_name: str
    status: str
    message: str


class MetricsResponse(BaseModel):
    """Response model for repository metrics"""
    repo_full_name: str
    metrics: dict
    timestamp: datetime


@router.post("/repositories", response_model=RepositoryResponse)
async def add_repository(request: RepositoryRequest, background_tasks: BackgroundTasks):
    """
    Add a repository for monitoring

    Args:
        request: Repository information
        background_tasks: FastAPI background tasks

    Returns:
        Repository addition status
    """
    try:
        repo_full_name = f"{request.owner}/{request.repo}"

        # Initialize IoTDB schema for this repository
        iotdb_client = IoTDBClient()
        iotdb_client.connect()
        iotdb_client.create_timeseries_schema(repo_full_name)
        iotdb_client.close()

        # Schedule background task to fetch initial metrics
        background_tasks.add_task(
            fetch_and_store_metrics,
            request.platform,
            request.owner,
            request.repo
        )

        return RepositoryResponse(
            platform=request.platform,
            owner=request.owner,
            repo=request.repo,
            full_name=repo_full_name,
            status="success",
            message=f"Repository {repo_full_name} added successfully. Fetching initial metrics in background."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add repository: {str(e)}")


@router.get("/repositories/{platform}/{owner}/{repo}/metrics", response_model=MetricsResponse)
async def get_repository_metrics(platform: str, owner: str, repo: str):
    """
    Get current metrics for a repository

    Args:
        platform: Platform name (github/gitee)
        owner: Repository owner
        repo: Repository name

    Returns:
        Current repository metrics
    """
    try:
        repo_full_name = f"{owner}/{repo}"

        # Fetch metrics from OpenDigger
        client = OpenDiggerClient()
        metrics = await client.get_all_metrics(platform, owner, repo)

        return MetricsResponse(
            repo_full_name=repo_full_name,
            metrics=metrics,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch metrics: {str(e)}")


@router.post("/repositories/{platform}/{owner}/{repo}/refresh")
async def refresh_repository_metrics(
    platform: str,
    owner: str,
    repo: str,
    background_tasks: BackgroundTasks
):
    """
    Refresh metrics for a repository

    Args:
        platform: Platform name (github/gitee)
        owner: Repository owner
        repo: Repository name
        background_tasks: FastAPI background tasks

    Returns:
        Refresh status
    """
    try:
        repo_full_name = f"{owner}/{repo}"

        # Schedule background task to fetch and store metrics
        background_tasks.add_task(
            fetch_and_store_metrics,
            platform,
            owner,
            repo
        )

        return {
            "repo_full_name": repo_full_name,
            "status": "success",
            "message": "Metrics refresh scheduled"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh metrics: {str(e)}")


async def fetch_and_store_metrics(platform: str, owner: str, repo: str):
    """
    Background task to fetch and store metrics

    Args:
        platform: Platform name
        owner: Repository owner
        repo: Repository name
    """
    try:
        repo_full_name = f"{owner}/{repo}"

        # Fetch metrics from OpenDigger
        client = OpenDiggerClient()
        metrics = await client.get_all_metrics(platform, owner, repo)

        # Store in IoTDB
        iotdb_client = IoTDBClient()
        iotdb_client.connect()

        # Process and store time-series data
        # This is simplified - in production would process each metric type properly
        if "openrank" in metrics and metrics["openrank"]:
            for timestamp_str, value in metrics["openrank"].items():
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                    iotdb_client.insert_metrics(
                        repo_full_name,
                        timestamp,
                        {"openrank": float(value)}
                    )
                except Exception as e:
                    continue

        iotdb_client.close()

    except Exception as e:
        # Log error but don't raise (background task)
        from loguru import logger
        logger.error(f"Failed to fetch and store metrics for {platform}/{owner}/{repo}: {e}")

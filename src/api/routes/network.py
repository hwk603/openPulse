"""
Network analysis routes
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from src.graph_analysis import CollaborationNetworkAnalyzer
from src.models import CollaborationNetwork, StructuralHoleRisk

router = APIRouter()


class NetworkAnalysisRequest(BaseModel):
    """Request model for network analysis"""
    platform: str
    owner: str
    repo: str


class NetworkMetricsResponse(BaseModel):
    """Response model for network metrics"""
    repo_full_name: str
    timestamp: datetime
    node_count: int
    edge_count: int
    density: float
    average_clustering: float
    num_communities: int
    modularity: float
    bus_factor: int


class KeyContributorsResponse(BaseModel):
    """Response model for key contributors"""
    repo_full_name: str
    timestamp: datetime
    contributors: List[dict]


class StructuralHoleResponse(BaseModel):
    """Response model for structural hole analysis"""
    repo_full_name: str
    timestamp: datetime
    bridge_contributors: List[dict]
    bus_factor: int
    structural_vulnerability_score: float


@router.post("/network-analysis", response_model=NetworkMetricsResponse)
async def analyze_network(request: NetworkAnalysisRequest):
    """
    Analyze collaboration network for a repository

    Args:
        request: Network analysis request

    Returns:
        Network metrics
    """
    try:
        repo_full_name = f"{request.owner}/{request.repo}"

        # In production, would load actual collaboration data
        # For now, create sample network
        analyzer = CollaborationNetworkAnalyzer()

        # Sample collaboration data
        sample_collaborations = [
            {"from": "user1", "to": "user2", "weight": 5.0, "timestamp": datetime.utcnow()},
            {"from": "user1", "to": "user3", "weight": 3.0, "timestamp": datetime.utcnow()},
            {"from": "user2", "to": "user3", "weight": 2.0, "timestamp": datetime.utcnow()},
        ]

        analyzer.build_network(sample_collaborations)
        network_metrics = analyzer.calculate_network_metrics()
        communities = analyzer.detect_communities()
        bus_factor = analyzer.calculate_bus_factor()

        return NetworkMetricsResponse(
            repo_full_name=repo_full_name,
            timestamp=datetime.utcnow(),
            node_count=network_metrics.get("num_nodes", 0),
            edge_count=network_metrics.get("num_edges", 0),
            density=network_metrics.get("density", 0.0),
            average_clustering=network_metrics.get("average_clustering", 0.0),
            num_communities=communities.get("num_communities", 0),
            modularity=communities.get("modularity", 0.0),
            bus_factor=bus_factor,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Network analysis failed: {str(e)}")


@router.get("/key-contributors/{platform}/{owner}/{repo}", response_model=KeyContributorsResponse)
async def get_key_contributors(platform: str, owner: str, repo: str, top_n: int = 10):
    """
    Get key contributors for a repository

    Args:
        platform: Platform name (github/gitee)
        owner: Repository owner
        repo: Repository name
        top_n: Number of top contributors to return

    Returns:
        List of key contributors
    """
    try:
        repo_full_name = f"{owner}/{repo}"

        # In production, would load actual collaboration data
        analyzer = CollaborationNetworkAnalyzer()

        # Sample data
        sample_collaborations = [
            {"from": "user1", "to": "user2", "weight": 5.0, "timestamp": datetime.utcnow()},
            {"from": "user1", "to": "user3", "weight": 3.0, "timestamp": datetime.utcnow()},
        ]

        analyzer.build_network(sample_collaborations)
        key_contributors = analyzer.identify_key_contributors(top_n=top_n)

        return KeyContributorsResponse(
            repo_full_name=repo_full_name,
            timestamp=datetime.utcnow(),
            contributors=key_contributors,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get key contributors: {str(e)}")


@router.get("/structural-holes/{platform}/{owner}/{repo}", response_model=StructuralHoleResponse)
async def analyze_structural_holes(platform: str, owner: str, repo: str):
    """
    Analyze structural holes in collaboration network

    Args:
        platform: Platform name (github/gitee)
        owner: Repository owner
        repo: Repository name

    Returns:
        Structural hole analysis results
    """
    try:
        repo_full_name = f"{owner}/{repo}"

        # In production, would load actual collaboration data
        analyzer = CollaborationNetworkAnalyzer()

        # Sample data
        sample_collaborations = [
            {"from": "user1", "to": "user2", "weight": 5.0, "timestamp": datetime.utcnow()},
            {"from": "user1", "to": "user3", "weight": 3.0, "timestamp": datetime.utcnow()},
        ]

        analyzer.build_network(sample_collaborations)
        structural_holes = analyzer.detect_structural_holes()
        bus_factor = analyzer.calculate_bus_factor()

        # Identify bridge contributors
        bridge_contributors = [
            {
                "username": username,
                "constraint": data["constraint"],
                "effective_size": data["effective_size"],
                "is_bridge": data["is_bridge"],
            }
            for username, data in structural_holes.items()
            if data["is_bridge"]
        ]

        # Calculate vulnerability score (lower bus factor = higher vulnerability)
        vulnerability_score = max(0.0, 1.0 - (bus_factor / 10.0))

        return StructuralHoleResponse(
            repo_full_name=repo_full_name,
            timestamp=datetime.utcnow(),
            bridge_contributors=bridge_contributors,
            bus_factor=bus_factor,
            structural_vulnerability_score=vulnerability_score,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Structural hole analysis failed: {str(e)}")


@router.get("/network-export/{platform}/{owner}/{repo}")
async def export_network_data(platform: str, owner: str, repo: str):
    """
    Export network data for visualization

    Args:
        platform: Platform name (github/gitee)
        owner: Repository owner
        repo: Repository name

    Returns:
        Network data in format suitable for visualization
    """
    try:
        repo_full_name = f"{owner}/{repo}"

        # In production, would load actual collaboration data
        analyzer = CollaborationNetworkAnalyzer()

        # Sample data
        sample_collaborations = [
            {"from": "user1", "to": "user2", "weight": 5.0, "timestamp": datetime.utcnow()},
            {"from": "user1", "to": "user3", "weight": 3.0, "timestamp": datetime.utcnow()},
            {"from": "user2", "to": "user3", "weight": 2.0, "timestamp": datetime.utcnow()},
        ]

        analyzer.build_network(sample_collaborations)
        network_data = analyzer.export_network_data()

        return {
            "repo_full_name": repo_full_name,
            "timestamp": datetime.utcnow().isoformat(),
            "network": network_data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export network data: {str(e)}")

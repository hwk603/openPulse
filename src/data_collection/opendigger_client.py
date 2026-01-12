"""
OpenDigger data collection client
"""
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger

from config import get_settings


class OpenDiggerClient:
    """Client for OpenDigger API"""

    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.OPENDIGGER_API_URL
        self.timeout = self.settings.OPENDIGGER_TIMEOUT

    async def get_openrank(
        self, platform: str, owner: str, repo: str
    ) -> Optional[Dict[str, float]]:
        """
        Get OpenRank metrics for a repository

        Args:
            platform: Platform name (github/gitee)
            owner: Repository owner
            repo: Repository name

        Returns:
            Dictionary with timestamp -> openrank value mapping
        """
        url = f"{self.base_url}/{platform}/{owner}/{repo}/openrank.json"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch OpenRank for {platform}/{owner}/{repo}: {e}")
            return None

    async def get_activity(
        self, platform: str, owner: str, repo: str
    ) -> Optional[Dict[str, float]]:
        """
        Get activity metrics for a repository

        Args:
            platform: Platform name (github/gitee)
            owner: Repository owner
            repo: Repository name

        Returns:
            Dictionary with timestamp -> activity value mapping
        """
        url = f"{self.base_url}/{platform}/{owner}/{repo}/activity.json"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch activity for {platform}/{owner}/{repo}: {e}")
            return None

    async def get_contributors(
        self, platform: str, owner: str, repo: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get contributor information for a repository

        Args:
            platform: Platform name (github/gitee)
            owner: Repository owner
            repo: Repository name

        Returns:
            Dictionary with contributor data
        """
        url = f"{self.base_url}/{platform}/{owner}/{repo}/participants.json"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(
                f"Failed to fetch contributors for {platform}/{owner}/{repo}: {e}"
            )
            return None

    async def get_issue_response_time(
        self, platform: str, owner: str, repo: str
    ) -> Optional[Dict[str, float]]:
        """
        Get issue response time metrics

        Args:
            platform: Platform name (github/gitee)
            owner: Repository owner
            repo: Repository name

        Returns:
            Dictionary with timestamp -> response time mapping
        """
        url = f"{self.base_url}/{platform}/{owner}/{repo}/issue_response_time.json"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(
                f"Failed to fetch issue response time for {platform}/{owner}/{repo}: {e}"
            )
            return None

    async def get_issue_resolution_duration(
        self, platform: str, owner: str, repo: str
    ) -> Optional[Dict[str, float]]:
        """
        Get issue resolution duration metrics

        Args:
            platform: Platform name (github/gitee)
            owner: Repository owner
            repo: Repository name

        Returns:
            Dictionary with timestamp -> duration mapping
        """
        url = (
            f"{self.base_url}/{platform}/{owner}/{repo}/issue_resolution_duration.json"
        )
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(
                f"Failed to fetch issue resolution duration for {platform}/{owner}/{repo}: {e}"
            )
            return None

    async def get_change_requests(
        self, platform: str, owner: str, repo: str
    ) -> Optional[Dict[str, int]]:
        """
        Get change requests (PR) metrics

        Args:
            platform: Platform name (github/gitee)
            owner: Repository owner
            repo: Repository name

        Returns:
            Dictionary with timestamp -> PR count mapping
        """
        url = f"{self.base_url}/{platform}/{owner}/{repo}/change_requests.json"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(
                f"Failed to fetch change requests for {platform}/{owner}/{repo}: {e}"
            )
            return None

    async def get_stars(
        self, platform: str, owner: str, repo: str
    ) -> Optional[Dict[str, int]]:
        """
        Get stars metrics

        Args:
            platform: Platform name (github/gitee)
            owner: Repository owner
            repo: Repository name

        Returns:
            Dictionary with timestamp -> stars count mapping
        """
        url = f"{self.base_url}/{platform}/{owner}/{repo}/stars.json"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch stars for {platform}/{owner}/{repo}: {e}")
            return None

    async def get_technical_fork(
        self, platform: str, owner: str, repo: str
    ) -> Optional[Dict[str, int]]:
        """
        Get technical fork metrics

        Args:
            platform: Platform name (github/gitee)
            owner: Repository owner
            repo: Repository name

        Returns:
            Dictionary with timestamp -> fork count mapping
        """
        url = f"{self.base_url}/{platform}/{owner}/{repo}/technical_fork.json"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(
                f"Failed to fetch technical fork for {platform}/{owner}/{repo}: {e}"
            )
            return None

    async def get_all_metrics(
        self, platform: str, owner: str, repo: str
    ) -> Dict[str, Any]:
        """
        Get all available metrics for a repository

        Args:
            platform: Platform name (github/gitee)
            owner: Repository owner
            repo: Repository name

        Returns:
            Dictionary containing all metrics
        """
        logger.info(f"Fetching all metrics for {platform}/{owner}/{repo}")

        metrics = {
            "openrank": await self.get_openrank(platform, owner, repo),
            "activity": await self.get_activity(platform, owner, repo),
            "contributors": await self.get_contributors(platform, owner, repo),
            "issue_response_time": await self.get_issue_response_time(
                platform, owner, repo
            ),
            "issue_resolution_duration": await self.get_issue_resolution_duration(
                platform, owner, repo
            ),
            "change_requests": await self.get_change_requests(platform, owner, repo),
            "stars": await self.get_stars(platform, owner, repo),
            "technical_fork": await self.get_technical_fork(platform, owner, repo),
        }

        # Filter out None values
        metrics = {k: v for k, v in metrics.items() if v is not None}

        logger.info(
            f"Successfully fetched {len(metrics)} metric types for {platform}/{owner}/{repo}"
        )
        return metrics

"""
Test OpenDigger data collection client
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
import httpx
from datetime import datetime

from src.data_collection.opendigger_client import OpenDiggerClient


class TestOpenDiggerClient:
    """Test suite for OpenDigger client"""

    @pytest.fixture
    def client(self):
        """Create OpenDigger client instance"""
        return OpenDiggerClient()

    @pytest.mark.asyncio
    async def test_get_openrank_success(self, client, sample_openrank_data):
        """Test successful OpenRank data retrieval"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = sample_openrank_data
            mock_response.raise_for_status = Mock()

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await client.get_openrank("github", "apache", "iotdb")

            assert result is not None
            assert "2024-01" in result
            assert result["2024-01"] == 100.5

    @pytest.mark.asyncio
    async def test_get_openrank_http_error(self, client):
        """Test OpenRank retrieval with HTTP error"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.HTTPError("Connection failed")
            )

            result = await client.get_openrank("github", "apache", "iotdb")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_activity_success(self, client, sample_activity_data):
        """Test successful activity data retrieval"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = sample_activity_data
            mock_response.raise_for_status = Mock()

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await client.get_activity("github", "apache", "iotdb")

            assert result is not None
            assert "2024-01" in result
            assert result["2024-01"] == 250.0

    @pytest.mark.asyncio
    async def test_get_contributors_success(self, client, sample_contributors_data):
        """Test successful contributors data retrieval"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = sample_contributors_data
            mock_response.raise_for_status = Mock()

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await client.get_contributors("github", "apache", "iotdb")

            assert result is not None
            assert "2024-01" in result
            assert result["2024-01"] == 45

    @pytest.mark.asyncio
    async def test_get_stars_success(self, client):
        """Test successful stars data retrieval"""
        sample_stars = {"2024-01": 4500, "2024-02": 4800, "2024-03": 5000}

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = sample_stars
            mock_response.raise_for_status = Mock()

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await client.get_stars("github", "apache", "iotdb")

            assert result is not None
            assert result["2024-03"] == 5000

    @pytest.mark.asyncio
    async def test_get_forks_success(self, client):
        """Test successful forks data retrieval"""
        sample_forks = {"2024-01": 1000, "2024-02": 1100, "2024-03": 1200}

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = sample_forks
            mock_response.raise_for_status = Mock()

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await client.get_forks("github", "apache", "iotdb")

            assert result is not None
            assert result["2024-03"] == 1200

    @pytest.mark.asyncio
    async def test_timeout_handling(self, client):
        """Test timeout handling"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.TimeoutException("Request timeout")
            )

            result = await client.get_openrank("github", "apache", "iotdb")

            assert result is None

    @pytest.mark.asyncio
    async def test_invalid_json_response(self, client):
        """Test handling of invalid JSON response"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_response.raise_for_status = Mock()

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            with pytest.raises(ValueError):
                await client.get_openrank("github", "apache", "iotdb")

    def test_client_initialization(self, client):
        """Test client initialization"""
        assert client.base_url is not None
        assert client.timeout > 0
        assert hasattr(client, 'settings')

    @pytest.mark.asyncio
    async def test_multiple_platforms(self, client, sample_openrank_data):
        """Test data retrieval for different platforms"""
        platforms = ["github", "gitee"]

        for platform in platforms:
            with patch('httpx.AsyncClient') as mock_client:
                mock_response = Mock()
                mock_response.json.return_value = sample_openrank_data
                mock_response.raise_for_status = Mock()

                mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                    return_value=mock_response
                )

                result = await client.get_openrank(platform, "test", "repo")
                assert result is not None

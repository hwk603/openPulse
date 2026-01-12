"""
Test IoTDB storage client
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from src.storage.iotdb_client import IoTDBClient


class TestIoTDBClient:
    """Test suite for IoTDB client"""

    @pytest.fixture
    def client(self):
        """Create IoTDB client instance"""
        with patch('src.storage.iotdb_client.Session') as mock_session:
            mock_session.return_value = Mock()
            return IoTDBClient()

    def test_client_initialization(self, client):
        """Test client initialization"""
        assert client is not None
        assert hasattr(client, 'session')

    def test_create_storage_group(self, client):
        """Test creating storage group"""
        with patch.object(client.session, 'set_storage_group') as mock_set:
            mock_set.return_value = None

            result = client.create_storage_group("root.openpulse.github")

            assert result is True
            mock_set.assert_called_once()

    def test_create_storage_group_error(self, client):
        """Test storage group creation error handling"""
        with patch.object(client.session, 'set_storage_group') as mock_set:
            mock_set.side_effect = Exception("Storage group already exists")

            result = client.create_storage_group("root.openpulse.github")

            # Should handle error gracefully
            assert result is False

    def test_create_timeseries(self, client):
        """Test creating timeseries"""
        with patch.object(client.session, 'create_time_series') as mock_create:
            mock_create.return_value = None

            result = client.create_timeseries(
                "root.openpulse.github.apache.iotdb.openrank",
                data_type="FLOAT",
                encoding="PLAIN",
                compressor="SNAPPY"
            )

            assert result is True
            mock_create.assert_called_once()

    def test_insert_metrics(self, client, sample_metrics_data):
        """Test inserting metrics"""
        with patch.object(client.session, 'insert_record') as mock_insert:
            mock_insert.return_value = None

            result = client.insert_metrics(
                sample_metrics_data["repo_full_name"],
                sample_metrics_data["timestamp"],
                sample_metrics_data["metrics"]
            )

            assert result is True

    def test_insert_metrics_batch(self, client):
        """Test batch inserting metrics"""
        metrics_batch = [
            {
                "repo_full_name": "apache/iotdb",
                "timestamp": datetime.utcnow() - timedelta(days=i),
                "metrics": {
                    "openrank": 100.0 + i,
                    "activity": 200.0 + i
                }
            }
            for i in range(10)
        ]

        with patch.object(client.session, 'insert_records') as mock_insert:
            mock_insert.return_value = None

            result = client.insert_metrics_batch(metrics_batch)

            assert result is True

    def test_query_metrics(self, client):
        """Test querying metrics"""
        with patch.object(client.session, 'execute_query_statement') as mock_query:
            mock_dataset = Mock()
            mock_dataset.has_next.side_effect = [True, True, False]
            mock_dataset.next.side_effect = [
                Mock(get_fields=lambda: [100.5, 250.0]),
                Mock(get_fields=lambda: [105.2, 280.0])
            ]
            mock_query.return_value = mock_dataset

            result = client.query_metrics(
                "apache/iotdb",
                ["openrank", "activity"],
                start_time=datetime.utcnow() - timedelta(days=30),
                end_time=datetime.utcnow()
            )

            assert result is not None
            assert "openrank" in result
            assert "activity" in result

    def test_query_metrics_with_aggregation(self, client):
        """Test querying metrics with aggregation"""
        with patch.object(client.session, 'execute_query_statement') as mocquery:
            mock_dataset = Mock()
            mock_dataset.has_next.side_effect = [True, False]
            mock_dataset.next.return_value = Mock(get_fields=lambda: [105.0])
            mock_query.return_value = mock_dataset

            result = client.query_metrics_aggregated(
                "apache/iotdb",
                "openrank",
                aggregation="AVG",
                start_time=datetime.utcnow() - timedelta(days=30),
                end_time=datetime.utcnow()
            )

            assert result is not None

    def test_query_latest_metrics(self, client):
        """Test querying latest metrics"""
        with patch.object(client.session, 'execute_query_statement') as mock_query:
            mock_dataset = Mock()
            mock_dataset.has_next.side_effect = [True, False]
            mock_dataset.next.return_value = Mock(get_fields=lambda: [110.8, 300.0])
            mock_query.return_value = mock_dataset

            result = client.query_latest_metrics(
                "apache/iotdb",
                ["openrank", "activity"]
            )

            assert result is not None

    def test_delete_metrics(self, client):
        """Test deleting metrics"""
        with patch.object(client.session, 'delete_data') as mock_delete:
            mock_delete.return_value = None

            result = client.delete_metrics(
                "apache/iotdb",
                start_time=datetime.utcnow() - timedelta(days=30),
                end_time=datetime.utcnow()
            )

            assert result is True

    def test_connection_error_handling(self, client):
        """Test connection error handling"""
        with patch.objession, 'execute_query_statement') as mock_query:
            mock_query.side_effect = Exception("Connection failed")

            result = client.query_metrics(
                "apache/iotdb",
                ["openrank"],
                start_time=datetime.utcnow() - timedelta(days=30),
                end_time=datetime.utcnow()
            )

            # Should handle error gracefully
            assert result is None or result == {}

    def test_close_connection(self, client):
        """Test closing connection"""
        with patch.object(client.session, 'close') as mock_close:
        mock_close.return_value = None

            client.close()

            mock_close.assert_called_once()

    def test_context_manager(self):
        """Test using client as context manager"""
        with patch('src.storage.iotdb_client.Session') as mock_session:
            mock_instance = Mock()
            mock_session.return_value = mock_instance

            with IoTDBClient() as client:
                assert client is not None

            # Should close connection
            mock_instance.close.assert_called_once()

    def test_query_with_downsampling(self, client):
        """Test querying with downsampling"""
        with patch.object(client.session, 'execute_query_statement') as mock_query:
            mock_dataset = Mock()
            mock_dataset.has_next.side_effect = [True, True, False]
            mock_dataset.next.side_effect = [
                Mock(get_fields=lambda: [100.0]),
                Mock(get_fields=lambda: [105.0])
            ]
            mock_query.return_value = mock_dataset

            result = client.query_metrics_downsampled(
                "apache/iotdb",
                "openrank",
                interval="1d",
                aggregation="AVG",
                start_time=datetime.utcnow() - timedelta(days=30),
                end_time=datetime.utcnow()
            )

            assert result is not None

    def test_bulk_insert_performance(self, client):
        """Test bulk insert performance"""
        large_batch = [
            {
                "repo_full_name": f"org/repo{i}",
                "timestamp": datetime.utcnow(),
                "metrics": {"openrank": float(i)}
            }
            for i in range(1000)
            with patch.object(client.session, 'insert_records') as mocn            mock_insert.return_value = None

            result = client.insert_metrics_batch(large_batch)

            assert result is True

    def test_query_time_range_validation(self, client):
        """Test time range validation in queries"""
        end_time = datetime.utcnow()
        start_time = end_time + timedelta(days=1)  # Invalid: start > end

        with pytest.raises(ValueError):
            client.query_metrics(
                "apache/iotdb",
                ["openrank"],
                start_time=start_time,
                end_time=end_time
            )

    def test_metric_name_sanitization(self, client):
        """Test metric name sanitization"""
        invalid_metric_name = "metric-with-invalid/chars!"

        sanitized = client._sanitize_metric_name(invalid_metric_name)

        assert "/" not in sanitized
        assert "!" not in sanitized

"""
Apache IoTDB storage client for time-series data
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from iotdb.Session import Session
from iotdb.utils.IoTDBConstants import TSDataType, TSEncoding, Compressor
from loguru import logger

from config import get_settings


class IoTDBClient:
    """Client for Apache IoTDB time-series database"""

    def __init__(self):
        self.settings = get_settings()
        self.session: Optional[Session] = None

    def connect(self):
        """Establish connection to IoTDB"""
        try:
            self.session = Session(
                host=self.settings.IOTDB_HOST,
                port=self.settings.IOTDB_PORT,
                user=self.settings.IOTDB_USER,
                password=self.settings.IOTDB_PASSWORD,
            )
            self.session.open(False)
            logger.info(f"Connected to IoTDB at {self.settings.IOTDB_HOST}:{self.settings.IOTDB_PORT}")
        except Exception as e:
            logger.error(f"Failed to connect to IoTDB: {e}")
            raise

    def close(self):
        """Close IoTDB connection"""
        if self.session:
            self.session.close()
            logger.info("IoTDB connection closed")

    def create_timeseries_schema(self, repo_full_name: str):
        """
        Create time-series schema for a repository

        Args:
            repo_full_name: Full repository name (e.g., 'owner/repo')
        """
        if not self.session:
            self.connect()

        # Sanitize repo name for IoTDB path
        device_path = self._get_device_path(repo_full_name)

        # Define measurements and their types
        measurements = [
            # Basic metrics
            ("stars", TSDataType.INT32, TSEncoding.RLE, Compressor.SNAPPY),
            ("forks", TSDataType.INT32, TSEncoding.RLE, Compressor.SNAPPY),
            ("watchers", TSDataType.INT32, TSEncoding.RLE, Compressor.SNAPPY),
            ("open_issues", TSDataType.INT32, TSEncoding.RLE, Compressor.SNAPPY),
            # Activity metrics
            ("commits", TSDataType.INT32, TSEncoding.RLE, Compressor.SNAPPY),
            ("pull_requests", TSDataType.INT32, TSEncoding.RLE, Compressor.SNAPPY),
            ("issues_opened", TSDataType.INT32, TSEncoding.RLE, Compressor.SNAPPY),
            ("issues_closed", TSDataType.INT32, TSEncoding.RLE, Compressor.SNAPPY),
            # Contributor metrics
            ("active_contributors", TSDataType.INT32, TSEncoding.RLE, Compressor.SNAPPY),
            ("new_contributors", TSDataType.INT32, TSEncoding.RLE, Compressor.SNAPPY),
            # OpenRank
            ("openrank", TSDataType.DOUBLE, TSEncoding.GORILLA, Compressor.SNAPPY),
            # Response time
            ("issue_response_time", TSDataType.DOUBLE, TSEncoding.GORILLA, Compressor.SNAPPY),
            ("issue_resolution_duration", TSDataType.DOUBLE, TSEncoding.GORILLA, Compressor.SNAPPY),
            # Health scores
            ("health_score", TSDataType.DOUBLE, TSEncoding.GORILLA, Compressor.SNAPPY),
            ("activity_score", TSDataType.DOUBLE, TSEncoding.GORILLA, Compressor.SNAPPY),
            ("diversity_score", TSDataType.DOUBLE, TSEncoding.GORILLA, Compressor.SNAPPY),
            ("response_time_score", TSDataType.DOUBLE, TSEncoding.GORILLA, Compressor.SNAPPY),
            ("code_quality_score", TSDataType.DOUBLE, TSEncoding.GORILLA, Compressor.SNAPPY),
            ("documentation_score", TSDataType.DOUBLE, TSEncoding.GORILLA, Compressor.SNAPPY),
            ("community_atmosphere_score", TSDataType.DOUBLE, TSEncoding.GORILLA, Compressor.SNAPPY),
        ]

        try:
            for measurement, data_type, encoding, compressor in measurements:
                path = f"{device_path}.{measurement}"
                try:
                    self.session.create_time_series(
                        path, data_type, encoding, compressor
                    )
                    logger.debug(f"Created time series: {path}")
                except Exception as e:
                    # Time series might already exist
                    if "already exists" not in str(e).lower():
                        logger.warning(f"Failed to create time series {path}: {e}")

            logger.info(f"Time series schema created for {repo_full_name}")
        except Exception as e:
            logger.error(f"Failed to create time series schema: {e}")
            raise

    def insert_metrics(
        self, repo_full_name: str, timestamp: datetime, metrics: Dict[str, Any]
    ):
        """
        Insert metrics data into IoTDB

        Args:
            repo_full_name: Full repository name
            timestamp: Timestamp for the metrics
            metrics: Dictionary of metric name -> value
        """
        if not self.session:
            self.connect()

        device_path = self._get_device_path(repo_full_name)
        timestamp_ms = int(timestamp.timestamp() * 1000)

        measurements = list(metrics.keys())
        values = list(metrics.values())

        try:
            self.session.insert_record(
                device_path, timestamp_ms, measurements, values
            )
            logger.debug(
                f"Inserted {len(measurements)} metrics for {repo_full_name} at {timestamp}"
            )
        except Exception as e:
            logger.error(f"Failed to insert metrics: {e}")
            raise

    def insert_batch_metrics(
        self, repo_full_name: str, data: List[Dict[str, Any]]
    ):
        """
        Insert batch metrics data

        Args:
            repo_full_name: Full repository name
            data: List of dictionaries with 'timestamp' and metric values
        """
        if not self.session:
            self.connect()

        device_path = self._get_device_path(repo_full_name)

        timestamps = []
        measurements_list = []
        values_list = []

        for record in data:
            timestamp = record.pop("timestamp")
            timestamp_ms = int(timestamp.timestamp() * 1000)
            timestamps.append(timestamp_ms)

            measurements = list(record.keys())
            values = list(record.values())

            measurements_list.append(measurements)
            values_list.append(values)

        try:
            self.session.insert_records(
                [device_path] * len(timestamps),
                timestamps,
                measurements_list,
                values_list,
            )
            logger.info(f"Inserted {len(timestamps)} batch records for {repo_full_name}")
        except Exception as e:
            logger.error(f"Failed to insert batch metrics: {e}")
            raise

    def query_metrics(
        self,
        repo_full_name: str,
        measurements: List[str],
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query metrics from IoTDB

        Args:
            repo_full_name: Full repository name
            measurements: List of measurement names to query
            start_time: Start time for query
            end_time: End time for query

        Returns:
            List of dictionaries with timestamp and metric values
        """
        if not self.session:
            self.connect()

        device_path = self._get_device_path(repo_full_name)

        # Build query
        select_clause = ", ".join([f"{device_path}.{m}" for m in measurements])
        query = f"SELECT {select_clause} FROM {device_path}"

        # Add time range filter
        conditions = []
        if start_time:
            start_ms = int(start_time.timestamp() * 1000)
            conditions.append(f"time >= {start_ms}")
        if end_time:
            end_ms = int(end_time.timestamp() * 1000)
            conditions.append(f"time <= {end_ms}")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        try:
            session_data_set = self.session.execute_query_statement(query)
            results = []

            while session_data_set.has_next():
                record = session_data_set.next()
                timestamp = datetime.fromtimestamp(record.get_timestamp() / 1000)

                data = {"timestamp": timestamp}
                for i, measurement in enumerate(measurements):
                    field = record.get_fields()[i]
                    data[measurement] = field.get_value()

                results.append(data)

            session_data_set.close_operation_handle()
            logger.info(f"Queried {len(results)} records for {repo_full_name}")
            return results

        except Exception as e:
            logger.error(f"Failed to query metrics: {e}")
            raise

    def query_latest_metrics(
        self, repo_full_name: str, measurements: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Query latest metrics for a repository

        Args:
            repo_full_name: Full repository name
            measurements: List of measurement names to query

        Returns:
            Dictionary with latest metric values
        """
        if not self.session:
            self.connect()

        device_path = self._get_device_path(repo_full_name)

        select_clause = ", ".join([f"last_value({device_path}.{m})" for m in measurements])
        query = f"SELECT {select_clause} FROM {device_path}"

        try:
            session_data_set = self.session.execute_query_statement(query)

            if session_data_set.has_next():
                record = session_data_set.next()
                data = {}

                for i, measurement in enumerate(measurements):
                    field = record.get_fields()[i]
                    data[measurement] = field.get_value()

                session_data_set.close_operation_handle()
                return data

            session_data_set.close_operation_handle()
            return None

        except Exception as e:
            logger.error(f"Failed to query latest metrics: {e}")
            return None

    def _get_device_path(self, repo_full_name: str) -> str:
        """
        Get IoTDB device path for a repository

        Args:
            repo_full_name: Full repository name (e.g., 'owner/repo')

        Returns:
            IoTDB device path
        """
        # Replace special characters
        sanitized = repo_full_name.replace("/", ".").replace("-", "_")
        return f"{self.settings.IOTDB_DATABASE}.{sanitized}"

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

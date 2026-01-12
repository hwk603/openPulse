# OpenPulse Test Suite Documentation

## Overview

This document describes the comprehensive test suite for the OpenPulse project. The test suite covers all major components with unit tests, integration tests, and performance tests.

## Test Structure

```
tests/
├── conftest.py                 # Test fixtures and configuration
├── test_api.py                 # API endpoint tests (enhanced)
├── test_models.py              # Data model tests (enhanced)
├── test_data_collection.py     # OpenDigger client tests (NEW)
├── test_storage.py             # IoTDB client tests (NEW)
├── test_graph_analysis.py      # Network analyzer tests (NEW)
├── test_services.py            # Business service tests (NEW)
├── test_tasks.py               # Celery task tests (NEW)
└── test_integration.py         # End-to-end integration tests (NEW)
```

## Test Coverage

### 1. **conftest.py** - Test Fixtures
- ✅ Sample data fixtures for all models
- ✅ Mock clients (OpenDigger, IoTDB, NetworkAnalyzer)
- ✅ Mock database sessions
- ✅ API request data fixtures

**Total Fixtures**: 12

### 2. **test_data_collection.py** - OpenDigger Client Tests
- ✅ Successful data retrieval (OpenRank, activity, contributors, stars, forks)
- ✅ HTTP error handling
- ✅ Timeout handling
- ✅ Invalid JSON response handling
- ✅ Client initialization
- ✅ Multiple platform support

**Total Tests**: 10

### 3. **test_storage.py** - IoTDB Client Tests
- ✅ Client initialization
- ✅ Storage group creation
- ✅ Timeseries creation
- ✅ Metrics insertion (single and batch)
- ✅ Metrics querying (basic, aggregated, latest)
- ✅ Metrics deletion
- ✅ Connection error handling
- ✅ Context manager support
- ✅ Downsampling queries
- ✅ Bulk insert performance
- ✅ Time range validation
- ✅ Metric name sanitization

**Total Tests**: 15

### 4. **test_graph_analysis.py** - Network Analyzer Tests
- ✅ Network building from collaboration data
- ✅ Edge weight handling
- ✅ Empty network handling
- ✅ Centrality metrics calculation
- ✅ Centrality value range validation
- ✅ Structural hole detection
- ✅ Community detection
- ✅ Bus factor calculation
- ✅ Key contributor identification
- ✅ Duplicate edge handling (weight accumulation)
- ✅ Self-loop handling
- ✅ Network statistics
- ✅ Bridge identification
- ✅ Clustering coefficient
- ✅ Large network performance

**Total Tests**: 15

### 5. **test_services.py** - Business Service Tests

#### HealthAssessmentService (10 tests)
- ✅ Health score calculation
- ✅ Activity score calculation
- ✅ Diversity score calculation
- ✅ Response time score calculation
- ✅ Code quality score calculation
- ✅ Lifecycle stage identification (embryonic, growth, mature, decline)
- ✅ Missing data handling

#### ChurnPredictionService (12 tests)
- ✅ Churn prediction
- ✅ Behavior decay score calculation
- ✅ Network marginalization score calculation
- ✅ Temporal anomaly score calculation
- ✅ Community engagement score calculation
- ✅ Alert level determination (green, yellow, orange, red)
- ✅ Retention suggestions generation
- ✅ Insufficient data handling

**Total Tests**: 22

### 6. **test_models.py** - Data Model Tests

#### Pydantic Models (9 tests)
- ✅ HealthScore model and validation
- ✅ ChurnPrediction model and validation
- ✅ AlertLevel enum
- ✅ LifecycleStage enum
- ✅ CollaborationNetwork model
- ✅ StructuralHoleRisk model
- ✅ RiskAssessmentReport model
- ✅ JSON serialization

#### Database Models (8 tests)
- ✅ RepositoryModel CRUD
- ✅ ContributorModel CRUD
- ✅ HealthScoreModel database operations
- ✅ ChurnPredictionModel database operations
- ✅ AnalysisTaskModel operations
- ✅ Repository relationships
- ✅ Automatic timestamps
- ✅ Unique constraints

**Total Tests**: 17

### 7. **test_api.py** - API Endpoint Tests

#### Health Endpoints (3 tests)
- ✅ Root endpoint
- ✅ Health check
- ✅ Detailed health check

#### Repository Endpoints (5 tests)
- ✅ Create repository
- ✅ List repositories
- ✅ Get repository
- ✅ Delete repository
- ✅ Invalid data handling

#### Analysis Endpoints (5 tests)
- ✅ Health assessment
- ✅ Health assessment with missing fields
- ✅ Churn prediction
- ✅ Churn prediction with missing contributor
- ✅ Batch health assessment

#### Network Endpoints (4 tests)
- ✅ Network analysis
- ✅ Contributor centrality
- ✅ Structural holes
- ✅ Communities

#### Error Handling (4 tests)
- ✅ 404 not found
- ✅ Method not allowed
- ✅ Invalid JSON
- ✅ Large payload

#### CORS & Rate Limiting (3 tests)
- ✅ CORS headers
- ✅ Rate limit not exceeded
- ✅ Concurrent requests

**Total Tests**: 24

### 8. **test_tasks.py** - Celery Task Tests

#### Data Collection Tasks (3 tests)
- ✅ Fetch repository metrics
- ✅ Refresh all repositories
- ✅ Collect collaboration data

#### Analysis Tasks (3 tests)
- ✅ Analyze repository health
- ✅ Predict contributor churn
- ✅ Analyze collaboration network

#### Error Handling (2 tests)
- ✅ API error handling
- ✅ Service error handling

#### Task Infrastructure (4 tests)
- ✅ Task retry logic
- ✅ Periodic task registration
- ✅ Task routing
- ✅ Task serialization

**Total Tests**: 12

### 9. **test_integration.py** - Integration Tests

#### End-to-End Workflows (3 tests)
- ✅ Complete health assessment workflow
- ✅ Complete churn prediction workflow
- ✅ Complete network analysis workflow

#### Data Pipeline (1 test)
- ✅ Data collection to storage pipeline

#### Database Integration (2 tests)
- ✅ Database connection
- ✅ Repository CRUD operations

#### External API Integration (2 tests)
- ✅ OpenDigger API integration
- ✅ IoTDB integration

#### Concurrency (2 tests)
- ✅ Concurrent API requests
- ✅ Concurrent health assessments

#### Performance (2 tests)
- ✅ API response time
- ✅ Batch processing performance

#### Error Recovery (2 tests)
- ✅ Database error recovery
- ✅ External API error recovery

#### Data Consistency (1 test)
- ✅ Health score consistency

**Total Tests**: 15

## Total Test Count

| Test File | Test Count |
|-----------|------------|
| test_data_collection.py | 10 |
| test_storage.py | 15 |
| test_graph_analysis.py | 15 |
| test_services.py | 22 |
| test_models.py | 17 |
| test_api.py | 24 |
| test_tasks.py | 12 |
| test_integration.py | 15 |
| **TOTAL** | **130** |

## Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_api.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_services.py::TestHealthAssessmentService -v
```

### Run Specific Test
```bash
pytest tests/test_api.py::TestHealthEndpoints::test_root_endpoint -v
```

### Run Tests by Marker
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run performance tests
pytest -m performance

# Skip slow tests
pytest -m "not slow"
```

### Run with Coverage
```bash
# Generate coverage report
pytest tests/ --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html  # Windows
```

### Run Tests in Parallel
```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest tests/ -n auto
```

## Test Markers

Tests are marked with the following markers:

- `@pytest.mark.unit` - Fast unit tests with no external dependencies
- `@pytest.mark.integration` - Integration tests that may require external services
- `@pytest.mark.performance` - Performance benchmarking tests
- `@pytest.mark.slow` - Slow-running tests

## Mocking Strategy

### External Dependencies
- **OpenDigger API**: Mocked using `unittest.mock.AsyncMock`
- **IoTDB**: Mocked using `unittest.mock.Mock`
- **Database**: Mocked using in-memory SQLite or mock sessions
- **Celery**: Tasks tested with `.apply()` method

### Fixtures
All test fixtures are defined in `conftest.py` and are automatically available to all tests.

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      - name: Run tests
        run: pytest tests/ --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Test Data

### Sample Repositories
- `apache/iotdb` - Primary test repository
- `apache/kafka` - Secondary test repository
- `apache/spark` - Tertiary test repository

### Sample Users
- `testuser` - Generic test user
- `user1`, `user2`, `user3`, `user4`, `user5` - Network analysis test users

## Best Practices

1. **Isolation**: Each test is independent and doesn't rely on other tests
2. **Mocking**: External dependencies are mocked to ensure fast, reliable tests
3. **Fixtures**: Reusable test data is defined in fixtures
4. **Assertions**: Clear, specific assertions with helpful error messages
5. **Coverage**: Aim for >80% code coverage
6. **Documentation**: Each test has a clear docstring explaining what it tests

## Known Limitations

1. **Integration Tests**: Some integration tests are skipped by default as they require actual external services
2. **Performance Tests**: Performance thresholds may need adjustment based on hardware
3. **Async Tests**: Require `pytest-asyncio` plugin

## Future Improvements

1. Add property-based testing with Hypothesis
2. Add mutation testing with mutpy
3. Add contract testing for API endpoints
4. Add load testing with Locust
5. Add security testing with Bandit
6. Add visual regression testing for web dashboard

## Troubleshooting

### Common Issues

**Issue**: `ImportError: No module named 'src'`
**Solution**: Ensure you're running pytest from the project root directory

**Issue**: `fixture 'sample_repo_data' not found`
**Solution**: Ensure `conftest.py` is in the tests directory

**Issue**: Tests hang indefinitely
**Solution**: Check for missing `@pytest.mark.asyncio` on async tests

**Issue**: Coverage report not generated
**Solution**: Install `pytest-cov`: `pip install pytest-cov`

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain >80% code coverage
4. Add appropriate test markers
5. Update this documentation

## Contact

For questions about the test suite, please open an issue on GitHub.

---

**Last Updated**: 2026-01-13
**Test Suite Version**: 1.0.0
**Total Tests**: 130
**Coverage Target**: >80%

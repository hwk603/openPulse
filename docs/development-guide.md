# OpenPulse Development Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Project Structure](#project-structure)
3. [Development Workflow](#development-workflow)
4. [Code Standards](#code-standards)
5. [Testing](#testing)
6. [Debugging](#debugging)
7. [Contributing](#contributing)

---

## Getting Started

### Development Environment Setup

#### Prerequisites

- Python 3.9+
- Git
- Docker & Docker Compose
- VS Code or PyCharm (recommended)

#### Initial Setup

```bash
# 1. Clone repository
git clone https://github.com/hwk603/openPulse.git
cd openRank

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install development dependencies
pip install -r requirements-dev.txt

# 5. Set up pre-commit hooks
pre-commit install

# 6. Copy environment file
cp .env.example .env

# 7. Start infrastructure services
docker-compose up -d postgres redis iotdb

# 8. Initialize database
python -c "from src.database import init_db; init_db()"

# 9. Run tests to verify setup
pytest tests/ -v
```

### IDE Configuration

#### VS Code

Install recommended extensions:
- Python
- Pylance
- Python Test Explorer
- Docker
- GitLens

`.vscode/settings.json`:
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "editor.formatOnSave": true,
  "editor.rulers": [88],
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

#### PyCharm

1. Open project
2. Configure Python interpreter (venv)
3. Enable Black formatter
4. Configure pytest as test runner
5. Enable type checking

---

## Project Structure

```
openRank/
├── src/                          # Source code
│   ├── api/                      # FastAPI application
│   │   ├── main.py              # Application entry point
│   │   └── routes/              # API route handlers
│   │       ├── health.py        # Health check endpoints
│   │       ├── analysis.py      # Analysis endpoints
│   │       ├── repositories.py  # Repository management
│   │       └── network.py       # Network analysis
│   │
│   ├── data_collection/         # Data collection layer
│   │   └── opendigger_client.py # OpenDigger API client
│   │
│   ├── storage/                 # Storage layer
│   │   └── iotdb_client.py     # IoTDB client
│   │
│   ├── graph_analysis/          # Graph analysis layer
│   │   └── network_analyzer.py  # Network analysis algorithms
│   │
│   ├── services/                # Business logic layer
│   │   ├── health_assessment.py # Health scoring
│   │   └── churn_prediction.py  # Churn prediction
│   │
│   ├── tasks/                   # Celery tasks
│   │   ├── celery_app.py       # Celery configuration
│   │   ├── data_collection.py  # Data collection tasks
│   │   └── analysis.py         # Analysis tasks
│   │
│   ├── models/                  # Data models
│   │   ├── schemas.py          # Pydantic models (API)
│   │   └── database.py         # SQLAlchemy models (DB)
│   │
│   ├── utils/                   # Utility functions
│   │   └── logging.py          # Logging configuration
│   │
│   └── database.py              # Database connection
│
├── config/             # Configuration
│   └── settings.py             # Application settings
│
├── tests/                       # Test suite
│   ├── conftest.py             # Test fixtures
│   ├── test_models.py          # Model tests
│   ├── test_api.py             # API tests
│   ├── test_services.py        # Service tests
│   └── test_integration.py     # Integration tests
│
├── docs/                        # Documentation
│   ├── architecture.md         # Architecture overview
│   ├── api-reference.md        # API documentation
│   ├── deployment.md           # Deployment guide
│   └── development-guide.md    # This file
│
├── scripts/                     # Utility scripts
│   ├── init-db.sh              # Database initialization
│   ├── backup.sh               # Backup script
│   └── seed-data.py            # Seed test data
│
├── chrome-extension/            # Chrome extension
│   ├── manifest.json           # Extension manifest
│   ├── popup.html              # Popup UI
│   ├── popup.js                # Popup logic
│   ├── content.js              # Content script
│   └── background.js           # Background service
│
├── web-dashboard/               # Web dashboard
│   └── index.html              # Single-page app
│
├── docker-compose.yml           # Docker orchestration
├── Dockerfile                   # Docker image
├── requirements.txt             # Python dependencies
├── requirements-dev.txt         # Dev dependencies
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── .pre-commit-config.yaml     # Pre-commit hooks
├── pytest.ini                  # Pytest configuration
├── setup.py                    # Package setup
└── README.md                   # Project README
```

---

## Development Workflow

### Feature Development

```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make changes
# ... edit files ...

# 3. Run tests
pytest tests/ -v

# 4. Format code
black src/ tests/
flake8 src/ tests/

# 5. Type check
mypy src/

# 6. Commit changes
git add .
git commit -m "feat: add your feature description"

# 7. Push to remote
git push origin feature/your-feature-name

# 8. Create pull request
```

### Running the Application

#### API Server

```bash
# Development mode (auto-reload)
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Celery Worker

```bash
# Single worker
celery -A src.tasks.celery_app worker --loglevel=info

# Multiple workers
celery -A src.tasks.celery_app worker --loglevel=info --concurrency=4

# With beat scheduler
celery -A src.tasks.celery_app worker --beat --loglevel=info
```

#### Celery Beat (Scheduler)

```bash
celery -A src.tasks.celery_app beat --loglevel=info
```

### Database Operations

#### Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# View current version
alembic current
```

#### Database Shell

```bash
# PostgreSQL
docker-compose exec postgres psql -U openpulse -d openpulse

# Common queries
\dt                    # List tables
\d repositories        # Describe table
SELECT * FROM repositories LIMIT 10;
```

#### Reset Database

```bash
# Drop and recreate
python scripts/reset-db.py

# Or manually
docker-compose down -v
docker-compose up -d postgres
python -c "from src.database import init_db; init_db()"
```

---

#de Standards

### Python Style Guide

Follow PEP 8 with these modifications:
- Line length: 88 characters (Black default)
- Use double quotes for strings
- Use trailing commas in multi-line structures

### Code Formatting

```bash
# Format all code
black src/ tests/

# Check formatting without changes
black --check src/ tests/

# Format specific file
black src/api/main.py
```

### Linting

```bash
# Run flake8
flake8 src/ tests/

# With specific rules
flake8 --max-line-length=88 --extend-ignore=E203,W503 src/
```

### Type Checking

```bash
# Check all files
mypy src/

# Check specific module
mypy src/services/

# Strict mode
mypy --strict src/
```

### Import Organization

Use `isort` for consistent import ordering:

```bash
# Sort imports
isort src/ tests/

# Check without changes
isort --check-only src/ tests/
```

Import order:
1. Standard library
2. Third-party packages
3. Local application imports

Example:
```python
# Standard library
import os
from datetime import datetime
from typing import List, Optional

# Third-party
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

# Local
from src.database import get_db
from src.models.schemas import HealthScore
from src.services.health_assessment import HealthAssessmentService
```

### Naming Conventions

- **Classes**: PascalCase (`HealthAssessmentService`)
- **Functions/Methods**: snake_case (`calculate_health_score`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_RETRY_ATTEMPTS`)
- **Private**: Leading underscore (`_internal_method`)
- **Files**: snake_case (`health_assessment.py`)

### Documentation

#### Docstrings

Use Google-style docstrings:

```python
def calculate_health_score(
    repository: str,
    time_window: int = 30
) -> HealthScore:
    """Calculate health sa repository.

    Args:
        repository: Full repository name (owner/repo)
        time_window: Analysis time window in days

    Returns:
        HealthScore object with calculated metrics

    Raises:
        ValueError: If repository format is invalid
        HTTPException: If data collection fails

    Example:
        >>> score = calculate_health_score("apache/iotdb", 30)
        >>> print(score.overall_score)
        85.5
    """
    pass
```

#### Type Hints

Always use type hints:

```python
from typing import List, Optional, Dict, Any

def process_data(
    data: List[Dict[str, Any]],
    threshold: float = 0.5
) -> Optional[Dict[str, float]]:
    """Process data with type hints."""
    pass
```

### Error Handling

```python
# Good: Specific exceptions
try:
    result = fetch_data(repo)
except HTTPError as e:
    logger.error(f"HTTP error: {e}")
    raise
except ValueError as e:
    logger.warning(f"Invalid data: {e}")
    return None

# Bad: Bare except
try:
    result = fetch_data(repo)
except:  # Don't do this
    pass
```

### Logging

```python
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Use appropriate levels
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)
logger.critical("Critical error")

# Include context
logger.info(
    "Health score calculated",
    extra={
        "repository": repo_name,
        "score": score,
        "duration_ms": duration
    }
)
```

---

## Testing

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/             # Integration tests
│   ├── test_api.py
│   ├── test_database.py
│   └── test_celery.py
└── e2e/                     # End-to-end tests
    └── test_workflows.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run specific test
pytest tests/test_api.py::test_health_endpoint

# Run with markers
pytest -m "not slow"

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run in parallel
pytest -n auto
```

### Writing Tests

#### UniTest Example

```python
# tests/unit/test_health_assessment.py
import pytest
from src.services.health_assessment import HealthAssessmentService

@pytest.fixture
def health_service():
    """Create health assessment service."""
    return HealthAssessmentService()

def test_calculate_activity_score(health_service):
    """Test activity score calculation."""
    metrics = {
        "commits_per_month": 100,
        "prs_per_month": 30,
        "issues_per_month": 20
    }

    score = health_service.calculate_activity_score(metrics)

    assert 0 <= score <= 100
    assert isinstance(score, float)

def test_calculate_activity_score_zero_activity(health_service):
    """Test activity score with zero activity."""
    metrics = {
        "commits_per_month": 0,
        "prs_per_month": 0,
        "issues_per_month": 0
    }

    score = health_service.calculate_activity_score(metrics)

    assert score == 0
```

#### Integration Test Example

```python
# tests/integration/test_api.py
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

@pytest.fixture
def client():
    """Creest client."""
    return TestClient(app)

def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_repository(client):
    """Test repository creation."""
    data = {
        "platform": "github",
        "owner": "apache",
        "repo": "iotdb"
    }

    response = client.post("/api/v1/repositories", json=data)

    assert response.status_code == 201
    assert response.json()["full_name"] == "apache/iotdb"
```

#### Fixtures

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base
from src.models.database import RepositoryModel

@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(engine):
    """Create database session."""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def sample_repository(db_session):
    """Create sample repository."""
    repo = RepositoryModel(
        platform="github",
        owner="apache",
        repo="iotdb"
    )
    db_session.add(repo)
    db_session.commit()
    return repo
```

### Test Coverage

```bash
# Generate coverage report
pytest --cov=src --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html

# Coverage requirements
pytest --cov=src --cov-fail-under=80
```

---

## Debugging

### Debug Mode

```python
# Enabug mode in .env
DEBUG=True

# Or in code
import logging
logging.basicConfig(level=logging.DEBUG)
```

### VS Code Debugging

`.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "src.api.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
      ],
      "jinja": true,
      "justMyCode": false
    },
    {
      "naPytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["-v"],
      "console": "integratedTerminal"
    }
  ]
}
```

### Interactive Debugging

```python
# Use breakpoint()
def calculate_score(data):
    breakpoint()  # Debugger will stop here
    result = process(data)
    return result

# Or use pdb
import pdb
pdb.set_trace()
```

### Logging for Debugging

```python
import logging
logger = logging.getLogger(__name__)

# Add detailed logging
logger.debug(f"Input data: {data}")
logger.debug(f"Intermediate result: {result}")
logger.debug(f"Final output: {output}")
```

---

## Contributing

### Commit Message Format

Follow Conventional Commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting)
- `refactor`: Code refactoring
- `test`: Tests
- `chore`: Build/tools

**Examples:**
```
feat(api): add churn prediction endpoint

Add new endpoint for predicting contributor churn risk.
Includes ng and recommendations.

Closes #123

fix(database): resolve connection pool exhaustion

Increase connection pool size and add timeout handling.

docs(readme): update installation instructions

test(services): add health assessment tests
```

### Pull Request Process

1. **Create branch** from `main`
2. **Make changes** following code standards
3. **Write tests** for new functionality
4. **Update documentation** if needed
5. **Run tests** and ensure they pass
6. **Format code** with Black
7. **Commit** with conventional commit messages
8. **Push** to your fork
9. **Create PR** with description
10. **Address rcomments
11. **Merge** approval

### Code Review Checklist

- [ ] Code follows style guide
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Performance considered
- [ ] Security reviewed
- [ ] Error handling adequate
- [ ] Logging appropriate

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Apache IoTDB Documentation](https://iotdb.apache.org/)
- [EasyGraph Documentation](https://easy-graph.github.io/)

---

## Getting Help

- **Issues**: https://github.com/hwk603/openPulse/issues
- **Discussions**: https://github.com/hwk603/openPulse/discussions
- **Email**: support@openpulse.example.com

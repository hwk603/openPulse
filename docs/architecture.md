# OpenPulse Architecture Documentation

## System Overview

OpenPulse is a microservices-based platform for monitoring open source community health and predicting contributor churn. The system integrates four major open source tools to provide comprehensive analysis.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Client Layer                                 │
├─────────────────────────────────────────────────────────────────────┤
│  Web Dashboard  │  Chrome Extension  │  API Clients  │  CLI Tools   │
└────────┬────────┴──────────┬─────────┴───────┬───────┴──────────────┘
         │                   │                 │
         └───────────────────┴─────────────────┘
                             │
                    ┌────────▼────────┐
                    │   API Gateway   │
                    │   (FastAPI)     │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    ┌────▼─────┐      ┌─────▼──────┐     ┌─────▼──────┐
    │  Health  │      │   Churn    │     │  Network   │
    │Assessment│      │ Prediction │     │  Analysis  │
    │ Service  │      │  Service   │     │  Service   │
    └────┬─────┘      └─────┬──────┘     └─────┬──────┘
         │                  │                   │
         └──────────────────┼───────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
    ┌────▼─────┐      ┌────▼─────┐      ┌────▼─────┐
    │OpenDigger│      │EasyGraph │      │  Celery  │
    │  Client  │      │ Analyzer │      │  Tasks   │
    └────┬─────┘      └────┬─────┘      └────┬─────┘
         │                 │                  │
         └─────────────────┼──────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼─────┐     ┌────▼─────┐     ┌────▼─────┐
    │PostgreSQL│     │  IoTDB   │     │  Redis   │
    │(Metadata)│     │(TimeSeries)    │ (Cache)  │
    └──────────┘     └──────────┘     └──────────┘
```

## Component Architecture

### 1. API Layer (FastAPI)

**Responsibilities:**
- RESTful API endpoints
- Request validation (Pydantic)
- Authentication & authorization
- Rate limiting
- CORS handling
- API documentation (Swagger/ReDoc)

**Key Endpoints:**
- `/api/v1/repositories` - Repository management
- `/api/v1/health-assessment` - Health score calculation
- `/api/v1/churn-prediction` - Contributor churn prediction
- `/api/v1/network-analysis` - Collaboration network analysis

**Technology Stack:**
- FastAPI 0.104+
- Uvicorn (ASGI server)
- Pydantic (data validation)
- Python 3.9+

### 2. Data Collection Layer (OpenDigger)

**Responsibilities:**
- Fetch metrics from OpenDigger API
- Data normalization and validation
- Rate limiting and retry logic
- Caching frequently accessed data

**Metrics Collected:**
- OpenRank scores
- Activity metrics (commits, PRs, issues)
- Contributor information
- Response times
- Stars, forks, watchers

**Implementation:**
- `src/data_collection/opendigger_client.py`
- Async HTTP client (httpx)
- Exponential backoff retry
- Response caching (Redis)

### 3. Time Series Storage (Apache IoTDB)

**Responsibilities:**
- Store time-series metrics
- Efficient compression
- Fast time-range queries
- Downsampling and aggregation

**Schema Design:**
```
root.openpulse.repositories.{platform}.{owner}.{repo}.{metric_type}.{metric_name}
```

**Metric Types:**
- `health.*` - Health scores
- `activity.*` - Activity metrics
- `metrics.*` - OpenRank, stars, forks
- `response.*` - Response times
- `network.*` - Network metrics

**Technology:**
- Apache IoTDB 1.3.0
- RLE encoding for compression
- Automatic data retention policies

### 4. Graph Analysis Layer (EasyGraph)

**Responsibilities:**
- Build collaboration networks
- Calculate centrality metrics
- Detect structural holes
- Community detection
- Bus factor calculation

**Algorithms:**
- **Centrality**: Degree, Betweenness, Closeness, PageRank
- **Structural Holes**: Burt's constraint, Effective size
- **Community Detection**: Louvain algorithm
- **Bus Factor**: Critical contributor identification

**Implementation:**
- `src/graph_analysis/network_analyzer.py`
- NetworkX integration
- Efficient graph algorithms
- Parallel processing support

### 5. Business Services Layer

#### Health Assessment Service
**File:** `src/services/health_assessment.py`

**Six Dimensions:**
1. **Activity** (25%): Commits, PRs, issues, reviews
2. **Diversity** (15%): Contributor count and distribution
3. **Response Time** (15%): Issue/PR response speed
4. **Code Quality** (15%): Review rate, test coverage
5. **Documentation** (15%): README, wiki, API docs
6. **Community Atmosphere** (15%): Issue close rate, sentiment

**Lifecycle Stages:**
- Embryonic: < 3 core contributors
- Growth: Rapid activity increase
- Mature: Stable development
- Decline: Activity drop > 30%

#### Churn Prediction Service
**File:** `src/services/churn_prediction.py`

**Risk Factors:**
1. **Behavioral Decay** (30%): Contribution frequency decline
2. **Network Marginalization** (25%): Centrality decrease
3. **Temporal Anomaly** (25%): Activity pattern changes
4. **Community Engagement** (20%): Participation decline

**Warning Levels:**
- 🟢 Green (0-25): Healthy, no risk
- 🟡 Yellow (25-50): Early warning, 1-2 months
- 🟠 Orange (50-75): High risk, immediate attention
- 🔴 Red (75-100): Critical, likely to churn

### 6. Task Queue (Celery)

**Responsibilities:**
- Asynchronous task execution
- Scheduled periodic tasks
- Task retry and error handling
- Result storage

**Task Types:**
- Data collection tasks
- Health assessment tasks
- Churn prediction tasks
- Network analysis tasks
- Periodic refresh tasks

**Configuration:**
- Broker: Redis
- Result backend: Redis
- Concurrency: 4 workers
- Task timeout: 300 seconds

### 7. Data Storage

#### PostgreSQL (Metadata)
**Purpose:** Store structured metadata

**Tables:**
- `repositories` - Repository information
- `contributors` - Contributor profiles
- `health_scores` - Health assessment results
- `churn_predictions` - Churn prediction results
- `analysis_tasks` - Task execution records
- `network_analysis` - Network analysis results
- `structural_holes` - Structural hole metrics

#### Apache IoTDB (Time Series)
**Purpose:** Store time-series metrics

**Advantages:**
- High compression ratio (10:1)
- Fast time-range queries
- Automatic downsampling
- Low storage cost

#### Redis (Cache & Queue)
**Purpose:** Caching and message queue

**Usage:**
- API response caching
- Session storage
- Celery message broker
- Rate limiting counters

## Data Flow

### Health Assessment Flow

```
1. Client Request
   ↓
2. API Endpoint (/api/v1/health-assessment)
   ↓
3. Create Celery Task
   ↓
4. Fetch Data from OpenDigger
   ↓
5. Store Raw Data in IoTDB
   ↓
6. Calculate Health Scores
   ↓
7. Store Results in PostgreSQL
   ↓
8. Return Response to Client
```

### Churn Prediction Flow

```
1. Client Request
   ↓
2. API Endpoint (/api/v1/churn-prediction)
   ↓
3. Fetch Contributor History (IoTDB)
   ↓
4. Build Collaboration Network (EasyGraph)
   ↓
5. Calculate Risk Factors
   ↓
6. Generate Predictions
   ↓
7. Store Results in PostgreSQL
   ↓
8. Return Predictions with Recommendations
```

### Network Analysis Flow

```
1. Client Request
   ↓
2. API Endpoint (/api/v1/network-analysis)
   ↓
3. Fetch Collaboration Data
   ↓
4. Build Graph (EasyGraph)
   ↓
5. Calculate Network Metrics
   ↓
6. Detect Structural Holes
   ↓
7. Identify Communities
   ↓
8. Calculate Bus Factor
   ↓
9. Store Results in PostgreSQL
   ↓
10. Return Network Analysis
```

## Scalability Considerations

### Horizontal Scaling
- **API Layer**: Multiple FastAPI instances behind load balancer
- **Celery Workers**: Scale workers based on queue length
- **Database**: PostgreSQL read replicas for queries

### Vertical Scaling
- **IoTDB**: Increase memory for better compression
- **Redis**: Increase memory for larger cache
- **PostgreSQL**: Optimize indexes and queries

### Performance Optimization
- **Caching**: Redis for frequently accessed data
- **Async I/O**: FastAPI async endpoints
- **Batch Processing**: Bulk data insertion
- **Connection Pooling**: Database connection pools

## Security Architecture

### Authentication
- API key authentication
- JWT tokens for session management
- OAuth2 integration (future)

### Authorization
- Role-based access control (RBAC)
- Repository-level permissions
- Rate limiting per user

### Data Security
- Encrypted connections (TLS/SSL)
- Encrypted data at rest
- Secure credential storage
- Input validation and sanitization

## Monitoring & Observability

### Logging
- Structured logging (JSON format)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Centralized log aggregation

### Metrics
- API response times
- Task execution times
- Database query performance
- Cache hit rates

### Health Checks
- `/health` endpoint
- Database connectivity
- Redis connectivity
- IoTDB connectivity
- Celery worker status

## Deployment Architecture

### Docker Compose (Development)
```yaml
services:
  - api (FastAPI)
  - celery-worker
  - celery-beat
  - postgres
  - redis
  - iotdb
```

### Kubernetes (Production)
```
- API Deployment (3 replicas)
- Celery Worker Deployment (5 replicas)
- Celery Beat Deployment (1 replica)
- PostgreSQL StatefulSet
- Redis StatefulSet
- IoTDB StatefulSet
- Ingress Controller
- Persistent Volumes
```

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| API | FastAPI | REST API framework |
| Task Queue | Celery | Async task processing |
| Web Server | Uvicorn | ASGI server |
| Database | PostgreSQL | Metadata storage |
| Time Series DB | Apache IoTDB | Metrics storage |
| Cache | Redis | Caching & message broker |
| Graph Analysis | EasyGraph | Network analysis |
| Data Source | OpenDigger | Open source metrics |
| Frontend | HTML/CSS/JS | Web dashboard |
| Browser Extension | Chrome API | GitHub integration |

## Future Enhancements

1. **Real-time Updates**: WebSocket support for live metrics
2. **Machine Learning**: Train custom churn prediction models
3. **Multi-platform**: Support GitLab, Gitee, Bitbucket
4. **Advanced Visualization**: Grafana integration
5. **Alerting**: Email, Slack, webhook notifications
6. **API v2**: GraphQL support
7. **Mobile App**: iOS and Android clients

# OpenPulse API Reference

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API is open for development. Production deployment will require API key authentication.

```http
Authorization: Bearer YOUR_API_KEY
```

## API Endpoints

### Health Check

#### GET /health

Check API service health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-13T00:00:00Z",
  "services": {
    "database": "connected",
    "redis": "connected",
    "iotdb": "connected"
  }
}
```

---

### Repository Management

#### POST /api/v1/repositories

Add a repository to monitoring.

**Request Body:**
```json
{
  "platform": "github",
  "owner": "apache",
  "repo": "iotdb"
}
```

**Response:**
```json
{
  "id": 1,
  "platform": "github",
  "owner": "apache",
  "repo": "iotdb",
  "full_name": "apache/iotdb",
  "created_at": "2024-01-13T00:00:00Z",
  "last_analyzed_at": null,
  "is_active": true
}
```

#### GET /api/v1/repositories

List all monitored repositories.

**Query Parameters:**
- `platform` (optional): Filter by platform (github, gitlab)
- `is_active` (optional): Filter by active status
- `limit` (optional): Number of results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "total": 100,
  "items": [
    {
      "id": 1,
      "platform": "github",
      "owner": "apache",
      "repo": "iotdb",
      "full_name": "apache/iotdb",
      "created_at": "2024-01-13T00:00:00Z",
      "last_analyzed_at": "2024-01-13T01:00:00Z",
      "is_active": true
    }
  ]
}
```

#### GET /api/v1/repositories/{repo_id}

Get repository details.

**Response:**
```json
{
  "id": 1,
  "platform": "github",
  "owner": "apache",
  "repo": "iotdb",
  "full_name": "apache/iotdb",
  "description": "Apache IoTDB",
  "created_at": "2024-01-13T00:00:00Z",
  "last_analyzed_at": "2024-01-13T01:00:00Z",
  "is_active": true,
  "latest_health_score": 85.5,
  "lifecycle_stage": "mature"
}
```

#### DELETE /api/v1/repositories/{repo_id}

Remove repository from monitoring.

**Response:**
```json
{
  "message": "Repository removed successfully"
}
```

---

### Health Assessment

#### POST /api/v1/health-assessment

Evaluate repository health score.

**Request Body:**
```json
{
  "platform": "github",
  "owner": "apache",
  "repo": "iotdb",
  "async": false
}
```

**Parameters:**
- `async` (optional): If true, returns task_id for async processing

**Synchronous Response:**
```json
{
  "repository": {
    "platform": "github",
    "owner": "apache",
    "repo": "iotdb"
  },
  "overall_score": 85.5,
  "dimensions": {
    "activity": {
      "score": 90.0,
      "weight": 0.25,
      "metrics": {
        "commits_per_month": 150,
        "prs_per_month": 45,
        "issues_per_month": 30
      }
    },
    "diversity": {
      "score": 85.0,
      "weight": 0.15,
      "metrics": {
        "total_contributors": 120,
        "active_contributors": 45,
        "new_contributors_3m": 12
      }
    },
    "response_time": {
      "score": 80.0,
      "weight": 0.15,
      "metrics": {
        "avg_issue_response_hours": 12.5,
        "avg_pr_response_hours": 8.3
      }
    },
    "code_quality": {
      "score": 88.0,
      "weight": 0.15,
      "metrics": {
        "pr_review_rate": 0.95,
        "test_coverage": 0.82
      }
    },
    "documentation": {
      "score": 82.0,
      "weight": 0.15,
      "metrics": {
        "readme_quality": 0.9,
        "wiki_pages": 25,
        "api_docs_coverage": 0.75
      }
    },
    "community_atmosphere": {
      "score": 85.0,
      "weight": 0.15,
      "metrics": {
        "issue_close_rate": 0.88,
        "avg_sentiment": 0.75
      }
    }
  },
  "lifecycle_stage": "mature",
  "warnings": [],
  "recommendations": [
    "Consider improving documentation coverage",
    "Response time is good, maintain current level"
  ],
  "analyzed_at": "2024-01-13T00:00:00Z"
}
```

**Asynchronous Response:**
```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "pending",
  "message": "Health assessment task created"
}
```

#### GET /api/v1/health-assessment/{repo_id}/history

Get historical health scores.

**Query Parameters:**
- `start_date` (optional): Start date (ISO 8601)
- `end_date` (optional): End date (ISO 8601)
- `limit` (optional): Number of results (default: 100)

**Response:**
```json
{
  "repository": {
    "platform": "github",
    "owner": "apache",
    "repo": "iotdb"
  },
  "history": [
    {
      "overall_score": 85.5,
      "analyzed_at": "2024-01-13T00:00:00Z"
    },
    {
      "overall_score": 84.2,
      "analyzed_at": "2024-01-12T00:00:00Z"
    }
  ]
}
```

---

### Churn Prediction

#### POST /api/v1/churn-prediction

Predict contributor churn risk.

**Request Body:**
```json
{
  "platform": "github",
  "owner": "apache",
  "repo": "iotdb",
  "contributor_username": "john_doe",
  "async": false
}
```

**Response:**
```json
{
  "contributor": {
    "username": "john_doe",
    "platform": "github"
  },
  "repository": {
    "platform": "github",
    "owner": "apache",
    "repo": "iotdb"
  },
  "churn_risk": {
    "overall_score": 45.5,
    "risk_level": "yellow",
    "risk_factors": {
      "behavioral_decay": {
        "score": 40.0,
        "weight": 0.30,
        "indicators": {
          "contribution_frequency_decline": 0.35,
          "commit_volume_decline": 0.42,
          "review_participation_decline": 0.38
        }
      },
      "network_marginalization": {
        "score": 50.0,
        "weight": 0.25,
        "indicators": {
          "centrality_decline": 0.45,
          "collaboration_decline": 0.55
        }
      },
      "temporal_anomaly": {
        "score": 48.0,
        "weight": 0.25,
        "indicators": {
          "activity_pattern_change": 0.48,
          "time_gap_increase": 0.50
        }
      },
      "community_engagement": {
        "score": 45.0,
        "weight": 0.20,
        "indicators": {
          "issue_participation_decline": 0.40,
          "pr_review_decline": 0.50
        }
      }
    }
  },
  "predictions": {
    "churn_probability_1m": 0.15,
    "churn_probability_3m": 0.35,
    "churn_probability_6m": 0.55
  },
  "recommendations": [
    "Reach out to contributor for feedback",
    "Assign interesting issues to re-engage",
    "Recognize recent contributions publicly"
  ],
  "analyzed_at": "2024-01-13T00:00:00Z"
}
```

#### GET /api/v1/churn-prediction/{repo_id}/at-risk

Get list of at-risk contributors.

**Query Parameters:**
- `risk_level` (optional): Filter by risk level (yellow, orange, red)
- `limit` (optional): Number of results (default: 50)

**Response:**
```json
{
  "repository": {
    "platform": "github",
    "owner": "apache",
    "repo": "iotdb"
  },
  "at_risk_contributors": [
    {
      "username": "john_doe",
      "churn_risk_score": 75.5,
      "risk_level": "orange",
      "last_contribution": "2024-01-01T00:00:00Z",
      "days_since_last_contribution": 12
    }
  ],
  "total": 5
}
```

---

### Network Analysis

#### POST /api/v1/network-analysis

Analyze collaboration network.

**Request Body:**
```json
{
  "platform": "github",
  "owner": "apache",
  "repo": "iotdb",
  "time_window_months": 6,
  "async": false
}
```

**Response:**
```json
{
  "repository": {
    "platform": "github",
    "owner": "apache",
    "repo": "iotdb"
  },
  "network_metrics": {
    "total_nodes": 120,
    "total_edges": 450,
    "density": 0.063,
    "avg_clustering_coefficient": 0.45,
    "diameter": 8,
    "avg_path_length": 3.2
  },
  "centrality_metrics": {
    "top_degree_centrality": [
      {
        "username": "alice",
        "score": 0.85
      },
      {
        "username": "bob",
        "score": 0.72
      }
    ],
    "top_betweenness_centrality": [
      {
        "username": "charlie",
        "score": 0.65
      }
    ],
    "top_pagerank": [
      {
        "username": "alice",
        "score": 0.042
      }
    ]
  },
  "structural_holes": {
    "bridge_contributors": [
      {
        "username": "charlie",
        "constraint": 0.25,
        "effective_size": 8.5,
        "risk_level": "high"
      }
    ]
  },
  "communities": {
    "total_communities": 5,
    "modularity": 0.68,
    "communities": [
      {
        "id": 1,
        "size": 35,
        "members": ["alice", "bob", "charlie"]
      }
    ]
  },
  "bus_factor": {
    "score": 3,
    "critical_contributors": ["alice", "bob", "charlie"],
    "risk_assessment": "medium"
  },
  "analyzed_at": "2024-01-13T00:00:00Z"
}
```

#### GET /api/v1/network-analysis/{repo_id}/graph

Get network graph data for visualization.

**Query Parameters:**
- `format` (optional): Output format (json, gexf, graphml)

**Response:**
```json
{
  "nodes": [
    {
      "id": "alice",
      "label": "Alice",
      "metrics": {
        "degree": 25,
        "betweenness": 0.65,
        "pagerank": 0.042
      }
    }
  ],
  "edges": [
    {
      "source": "alice",
      "target": "bob",
      "weight": 15
    }
  ]
}
```

---

### Task Management

#### GET /api/v1/tasks/{task_id}

Get task status and result.

**Response:**
```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "completed",
  "task_type": "health_assessment",
  "created_at": "2024-01-13T00:00:00Z",
  "completed_at": "2024-01-13T00:05:00Z",
  "result": {
    "overall_score": 85.5
  }
}
```

**Status Values:**
- `pending`: Task is queued
- `running`: Task is executing
- `completed`: Task finished successfully
- `failed`: Task failed with error

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "validation_error",
  "message": "Invalid request parameters",
  "details": [
    {
      "field": "owner",
      "message": "Field required"
    }
  ]
}
```

### 404 Not Found
```json
{
  "error": "not_found",
  "message": "Repository not found"
}
```

### 429 Too Many Requests
```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded. Try again in 60 seconds",
  "retry_after": 60
}
```

### 500 Internal Server Error
```json
{
  "error": "internal_error",
  "message": "An unexpected error occurred",
  "request_id": "req_abc123"
}
```

---

## Rate Limiting

- **Default**: 100 requests per minute per IP
- **Authenticated**: 1000 requests per minute per API key

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1610000000
```

---

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `limit`: Number of items per page (max: 100)
- `offset`: Number of items to skip

**Response Headers:**
```
X-Total-Count: 500
X-Page-Limit: 50
X-Page-Offset: 0
```

---

## Webhooks (Future)

Subscribe to events:

**Events:**
- `health_score.updated`
- `churn_risk.high`
- `structural_hole.detected`

**Webhook Payload:**
```json
{
  "event": "churn_risk.high",
  "timestamp": "2024-01-13T00:00:00Z",
  "data": {
    "repository": "apache/iotdb",
    "contributor": "john_doe",
    "risk_score": 85.5
  }
}
```

---

## SDK Examples

### Python
```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Add repository
response = requests.post(
    f"{BASE_URL}/repositories",
    json={
        "platform": "github",
        "owner": "apache",
        "repo": "iotdb"
    }
)
repo = response.json()

# Assess health
response = requests.post(
    f"{BASE_URL}/health-assessment",
    json={
        "platform": "github",
        "owner": "apache",
        "repo": "iotdb"
    }
)
health = response.json()
print(f"Health Score: {health['overall_score']}")
```

### JavaScript
```javascript
const BASE_URL = "http://localhost:8000/api/v1";

// Add repository
const response = await fetch(`${BASE_URL}/repositories`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    platform: "github",
    owner: "apache",
    repo: "iotdb"
  })
});
const repo = await response.json();

// Assess health
const healthResponse = await fetch(`${BASE_URL}/health-assessment`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    platform: "github",
    owner: "apache",
    repo: "iotdb"
  })
});
const health = await healthResponse.json();
console.log(`Health Score: ${health.overall_score}`);
```

### cURL
```bash
# Add repository
curl -X POST "http://localhost:8000/api/v1/repositories" \
  -H "Content-Type: application/json" \
  -d '{"platform":"github","owner":"apache","repo":"iotdb"}'

# Assess health
curl -X POST "http://localhost:8000/api/v1/health-assessment" \
  -H "Content-Type: application/json" \
  -d '{"platform":"github","owner":"apache","repo":"iotdb"}'
```

---

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

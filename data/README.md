# Data Directory

This directory contains sample data, test fixtures, and database schemas for the OpenPulse project.

## Directory Structure

```
data/
├── raw/                    # Raw data from OpenDigger API
│   ├── openrank/          # OpenRank metric samples
│   ├── activity/          # Activity metric samples
│   └── contributors/      # Contributor data samples
├── processed/             # Processed and transformed data
│   ├── health_scores/     # Health score examples
│   ├── network_graphs/    # Collaboration network data
│   └── predictions/       # Churn prediction results
├── schemas/               # Database schemas and migrations
├── fixtures/              # Test fixtures for unit tests
└── examples/              # Example API responses
```

## Data Sources

### OpenDigger API
- Base URL: https://oss.x-lab.info/open_digger
- Metrics: OpenRank, Activity, Stars, Forks, Issues, PRs, etc.

### Sample Repositories
- apache/iotdb
- kubernetes/kubernetes
- tensorflow/tensorflow
- pytorch/pytorch

## Usage

### Loading Sample Data
```python
from src.data_collection.opendigger_client import OpenDiggerClient

client = OpenDiggerClient()
data = client.get_openrank("github", "apache", "iotdb")
```

### Using Test Fixtures
```python
import json

with open("data/fixtures/health_score_sample.json") as f:
    sample_data = json.load(f)
```

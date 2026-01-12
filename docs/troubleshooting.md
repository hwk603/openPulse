# OpenPulse Troubleshooting Guide

## Table of Contents

1. [Common Issues](#common-issues)
2. [Database Issues](#database-issues)
3. [API Issues](#api-issues)
4. [Celery Issues](#celery-issues)
5. [IoTDB Issues](#iotdb-issues)
6. [Chrome Extension Issues](#chrome-extension-issues)
7. [Performance Issues](#performance-issues)
8. [Debugging Tools](#debugging-tools)

---

## Common Issues

### Issue: Services Won't Start

**Symptoms:**
- Docker containers fail to start
- Port already in use errors
- Connection refused errors

**Solutions:**

```bash
# Check if ports are already in use
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Stop conflicting services
docker-compose down
docker ps -a

# Remove all containers and volumes
docker-compose down -v

# Restart services
docker-compose up -d

# Check service logs
docker-compose logs -f
```

### Issue: Environment Variables Not Loading

**Symptoms:**
- Configuration errors
- Connection failures
- Missing credentials

**Solutions:**

```bash
# Verify .env file exists
ls -la .env

# Check .env file format (no spaces around =)
# Good: API_PORT=8000
# Bad:  API_PORT = 8000

# Verify environment variables are loaded
docker-compose config

# Restart services after .env changes
docker-compose down
docker-compose up -d
```

### Issue: Permission Denied Errors

**Symptoms:**
- Cannot write to log files
- Cannot access database files
- Docker volume permission errors

**Solutions:**

```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Fix Docker volume permissions
docker-compose down -v
docker volume prune
docker-compose up -d

# On Linux, add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

---

## Database Issues

### Issue: PostgreSQL Connection Failed

**Symptoms:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Diagnosis:**

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U openpulse -d openpulse -c "SELECT 1;"
```

**Solutions:**

```bash
# Restart PostgreSQL
docker-compose restart postgres

# Check connection settings in .env
POSTGRES_HOST=localhost  # or postgres for Docker
POSTGRES_PORT=5432
POSTGRES_USER=openpulse
POSTGRES_PASSWORD=openpulse
POSTGRES_DB=openpulse

# Recreate database
docker-compose down postgres
docker volume rm openrank_postgres_data
docker-compose up -d postgres

# Wait for PostgreSQL to be ready
sleep 10

# Initialize database
python -c "from src.database import init_db; init_db()"
```

### Issue: Database Migration Errors

**Symptoms:**
```
alembic.util.exc.CommandError: Can't locate revision identified by 'xyz'
```

**Solutions:**

```bash
# Check current migration version
alembic current

# View migration history
alembic history

# Stamp database to specific version
alembic stamp head

# Reset migrations (CAUTION: loses data)
docker-compose down -v
docker-compose up -d postgres
python -c "from src.database import init_db; init_db()"
alembic stamp head
```

### Issue: Database Locks

**Symptoms:**
- Queries hang indefinitely
- Deadlock errors
- Timeout errors

**Solutions:**

```sql
-- Connect to database
docker-compose exec postgres psql -U openpulse -d openpulse

-- Check for locks
SELECT * FROM pg_locks WHERE NOT granted;

-- Check active queries
SELECT pid, query, state, wait_event_type
FROM pg_stat_activity
WHERE state != 'idle';

-- Kill blocking query (use with caution)
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE pid = <blocking_pid>;
```

---

## API Issues

### Issue: API Returns 500 Internal Server Error

**Symptoms:**
- All endpoints return 500
- No specific error message

**Diagnosis:**

```bash
# Check API logs
docker-compose logs api

# Check if all services are running
docker-compose ps

# Test database connection
docker-compose exec api python -c "from src.database import engine; print(engine.connect())"
```

**Solutions:**

```bash
# Restart API service
docker-compose restart api

# Check for syntax errors
docker-compose exec api python -m py_compile src/api/main.py

# Run in debug mode
# In .env: DEBUG=True
docker-compose restart api
docker-compose logs -f api
```

### Issue: API Endpoint Not Found (404)

**Symptoms:**
```json
{"detail": "Not Found"}
```

**Solutions:**

```bash
# Verify endpoint exists
curl http://localhost:8000/docs

# Check route registration
docker-compose exec api python -c "
from src.api.main import app
for route in app.routes:
    print(f'{route.methods} {route.path}')
"

# Ensure correct API version
# Use: /api/v1/health-assessment
# Not: /health-assessment
```

### Issue: CORS Errors

**Symptoms:**
```
Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000'
has been blocked by CORS policy
```

**Solutions:**

```python
# In src/api/main.py, update CORS settings
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Request Timeout

**Symptoms:**
- Requests take too long
- Gateway timeout errors

**Solutions:**

```python
# Increase timeout in client
import httpx

async with httpx.AsyncClient(timeout=60.0) as client:
    response = await client.get(url)

# Or in nginx
proxy_read_timeout 300s;
proxy_connect_timeout 300s;
proxy_send_timeout 300s;
```

---

## Celery Issues

### Issue: Celery Worker Not Starting

**Symptoms:**
```
[ERROR/MainProcess] consumer: Cannot connect to redis://localhost:6379/0
```

**Diagnosis:**

```bash
# Check Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exis redis-cli ping

# Check Celery logs
docker-compose logs celery-worker
```

**Solutions:**

```bash
# Restart Redis
docker-compose restart redis

# Restart Celery worker
docker-compose restart celery-worker

# Check Redis connection in .env
REDIS_HOST=redis  # Use service name in Docker
REDIS_PORT=6379
REDIS_DB=0
```

### Issue: Tasks Not Executing

**Symptoms:**
- Tasks stay in pending state
- No task results

**Diagnosis:**

```bash
# Check worker status
docker-compose exec celery-worker celery -A src.tasks.celery_app inspect active

# Check registered tasks
docker-compose exec celery-worker celery -A src.tasks.celery_app inspect registered

# Check queue length
docker-compose exec redis redis-cli llen celery
```

**Solutions:**

```bash
# Purge all tasks
docker-compose exec celery-worker celery -A src.tasks.celery_app purge

# Restart worker with higher concurrency
docker-compose exec celery-worker celery -A src.tasks.celery_app worker --concurrency=8

# Check task routing
# Ensure task names match between producer and consumer
```

### Issue: Task Failures

**Symptoms:**
- Tasks fail with exceptions
- No retry attempts

**Solutions:**

```python
# Add retry logic to tasks
from celery import Task

@celery_app.task(bind=True, max_retries=3)
def my_task(self, arg):
    try:
        # Task logic
        pass
    except Exception as exc:
        # Retry after 60 seconds
        raise self.retry(exc=exc, countdown=60)

# Check task logs
docker-compose logs celery-worker | grep ERROR
```

---

## IoTDB Issues

### Issue: IoTDB Connection Failed

**Symptoms:**
```
IoTDBConnectionException: Cannot connect to IoTDB
```

**Diagnosis:**

```bash
# Check if IoTDB is running
docker-compose ps iotdb

# Check IoTDB logs
docker-compose logs iotdb

# Test connection
docker-compose exec iotdb ./sbin/start-cli.sh -h localhost -p 6667 -u root -pw root
```

**Solutions:**

```bash
# Restart IoTDB
docker-compose restart iotdb

# Wait for IoTDB to fully start (can take 30-60 seconds)
sleep 60

# Check IoTDB configuration
docker-compose exec iotdb cat conf/iotdb-engine.properties

# Recreate IoTDB container
docker-compose down iotdb
docker volume rm openrank_iotdb_data
docker-compose up -d iotdb
```

### Issue: IoTDB Storage Full

**Symptoms:**
```
org.apache.iotdb.db.exception.StorageEngineException: disk space is insufficient
```

**Solutions:**

```bash
# Check disk usage
docker-compose exec iotdb df -h

# Clean old data
docker-compose exec iotdb ./sbin/start-cli.sh -h localhost667 -u root -pw root
# In CLI:
DELETE FROM root.openpulse.** WHERE time < 2024-01-01T00:00:00

# Increase volume size in docker-compose.yml
# Or mount external storage
```

### Issue: Time Series Not Found

**Symptoms:**
```
Path [root.openpulse.repositories.github.apache.iotdb.health.overall_score] does not exist
```

**Solutions:**

```python
# Ensure time series is created before insertion
from src.storage.iotdb_client import IoTDBClient

client = IoTDBClient()
client.create_timeseries(
    path="root.openpulse.repositories.github.apache.iotdb.health.overall_score",
    data_type="FLOAT",
    encoding="RLE",
    compressor="SNAPPY"
)
```

---

## Chrome Extension Issues

### Issue: Extension Not Loading

**Symptoms:**
- Extension doesn't appear in Chrome
- Manifest errors

**Solutions:**

```bash
# Check manifest.json syntax
cat chrome-extension/manifest.json | python -m json.tool

# Verify all files exist
ls chrome-extension/

# Reload extension
# 1. Go to chrome://extensions/
# 2. Click "Reload" button
# 3. Check for errors
```

### Issue: API Connection Failed

**Symptoms:**
- Extension shows "Failed to fetch data"
- CORS errors in console

**Solutions:**

```javascript
// In chrome-extension/popup.js
// Ensure correct API URL
const API_URL = "http://localhost:8000/api/v1";

// Check CORS settings in API
// In src/api/main.py:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Content Script Not Injecting

**Symptoms:**
- No health badge on GitHub pages
- Content script errors

**Solutions:**

```javascript
// Check manifest.json permissions
{
  "permissions": ["activeTab", "storage"],
  "host_permissions": ["https://github.com/*"]
}

// Check content script matches
{
  "content_scripts": [{
    "matches": ["https://github.com/*/*"],
    "js": ["content.js"],
    "css": ["content.css"]
  }]
}

// Debug content script
// Open GitHub page
// Press F12 -> Console
// Check for errors
```

---

## Performance Issues

### Issue: Slow API Response Times

**Symptoms:**
- Requests take > 5 seconds
- Timeout errors

**Diagnosis:**

```bash
# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/v1/health-assessment

# curl-format.txt:
time_namelookup:  %{time_namelookup}\n
time_connect:  %{time_connect}\n
time_starttransfer:  %{time_starttransfer}\n
time_total:  %{time_total}\n

# Check database query performance
docker-compose exec postgres psql -U openpulse -d openpulse -c "
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
"
```

**Solutions:**

```python
# Add database indexes
from sqlalchemy import Index

Index('idx_repo_platform_owner_repo',
      RepositoryModel.platform,
      RepositoryModel.owner,
      RepositoryModel.repo)

# Use async
from fastapi import BackgroundTasks

@app.post("/api/v1/health-assessment")
async def assess_health(repo: RepoRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_assessment, repo)
    return {"status": "processing"}

# Enable caching
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
```

### Issue: High Memory Usage

**Symptoms:**
- OOM (Out of Memory) errors
- Container restarts

**Solutions:**

```bash
# Check memory usage
docker stats

# Limit container memory in docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          memory: 2G

# Optimize database queries
# Use pagination
# Limit result sets
# Use select_related/joinedload

# Increase available memory
# Or scale horizontally
```

### Issue: Database Connection Pool Exhausted

**Symptoms:**
```
sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 10 reached
```

**Solutions:**

```python
# In src/database.py
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=20,        # Increase pool size
    max_overflow=40,     # Increase overflow
    pool_timeout=30,     # Increase timeout
    pool_recycle=3600,   # Recycle connections
    pool_pre_ping=True   # Verify connections
)
```

---

## Debugging Tools

### Enable Debug Logging

```python
# In .env
DEBUG=True
LOG_LEVEL=DEBUG

# In code
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Database Query Logging

```python
LAlchemy query logging
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### API Request Logging

```python
# Add middleware to log all requests
from fastapi import Request
import time

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} "
        f"completed in {duration:.2f}s with status {response.status_code}"
    )
    return response
```

### Health Check Script

```bash
#!/bin/bash
# scripts/health-check.sh

echo "Checking OpenPulse services..."

# Check API
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ API is healthy"
else
    echo "✗ API is down"
fi

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready -U openpulse > /dev/null 2>&1; then
    echo "✓ PostgreSQL is healthy"
else
    echo "✗ PostgreSQL is down"
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✓ Redis is healthy"
else
    echo "✗ Redis is down"
fi

# Check Celery
if docker-compose exec -T celery-worker celery -A src.tasks.celery_app inspect ping > /dev/null 2>&1; then
    echo "✓ Celery is healthy"
else
    echo "✗ Celery is down"
fi
```

### Performance Profiling

```python
# Add profiling middleware
from fastapi import Request
import cProfile
import pstats
from io import StringIO

@app.middleware("http")
async def profile_request(request: Request, call_next):
    profiler = cProfile.Profile()
    profiler.enable()

    response = await call_next(request)

    profiler.disable()
    s = StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(10)

    logger.debug(f"Profile for {request.url.path}:\n{s.getvalue()}")

    return response
```

---

## Getting Help

If you can't resolve the issue:

1. **Check logs**: `docker-compose logs -f`
2. **Search issues**: https://github.com/hwk603/openPulse/issues
3. **Create issue**: Include logs, environment details, and steps to reproduce
4. **Ask community**: https://github.com/hwk603/openPulse/discussions

### Issue Template

```markdown
**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.11]
- Docker version: [e.g., 24.0.0]
- Depent method: [Docker Compose / Kubernetes / Local]

**Description:**
[Clear description of the issue]

**Steps to Reproduce:**
1. [First step]
2. [Second step]
3. [...]

**Expected Behavior:**
[What you expected to happen]

**Actual Behavior:**
[What actually happened]

**Logs:**
```
[Paste relevant logs here]
```

**Additional Context:**
[Any other relevant information]
```

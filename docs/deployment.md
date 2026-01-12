# OpenPulse Deployment Guide

## Table of Contents

1. [Development Deployment](#development-deployment)
2. [Production Deployment](#production-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Configuration](#configuration)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)

---

## Development Deployment

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Apache IoTDB 1.3+
- Docker & Docker Compose (optional)

### Option 1: Docker Compose (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/hwk603/openPulse.git
cd openRank

# 2. Create environment file
cp .env.example .env

# 3. Start all services
docker-compose up -d

# 4. Check service status
docker-compose ps

# 5. View logs
docker-compose logs -f api

# 6. Access services
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Web Dashboard: Open web-dashboard/index.html
```

### Option 2: Local Development

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start infrastructure services
docker-compose up -d postgres redis iotdb

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Initialize database
python -c "from src.database import init_db; init_db()"

# 6. Start API server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 7. Start Celery worker (new terminal)
celery -A src.tasks.celery_app worker --loglevel=info

# 8. Start Celery beat scheduler (new terminal, optional)
celery -A src.tasks.celery_app beat --loglevel=info
```

---

## Production Deployment

### System Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8 GB
- Disk: 50 GB SSD
- Network: 100 Mbps

**Recommended:**
- CPU: 8 cores
- RAM: 16 GB
- Disk: 200 GB SSD
- Network: 1 Gbps

### Pre-deployment Checklist

- [ ] Domain name configured
- [ ] SSL certificate obtained
- [ ] Firewall rules configured
- [ ] Backup strategy defined
- [ ] Monitoring tools set up
- [ ] Log aggregation configured
- [ ] Database backups automated
- [ ] Security audit completed

### Production Environment Setup

```bash
# 1. Create production user
sudo useradd -m -s /bin/bash openpulse
sudo usermod -aG docker openpulse

# 2. Clone repository
sudo -u openpulse git clone https://github.com/hwk603/openPulse.git /opt/openpulse
cd /opt/openpulse

# 3. Create production environment file
sudo -u openpulse cp .env.example .env.production
sudo -u olse nano .env.production

# 4. Set production values
DEBUG=False
API_HOST=0.0.0.0
API_PORT=8000
POSTGRES_PASSWORD=<strong-password>
REDIS_PASSWORD=<strong-password>
IOTDB_PASSWORD=<strong-password>

# 5. Build production images
docker-compose -f docker-compose.prod.yml build

# 6. Start services
docker-compose -f docker-compose.prod.yml up -d

# 7. Initialize database
docker-compose -f docker-compose.prod.yml exec api python -c "from src.database import init_db; init_db()"
```

### Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/openpulse

upstream openpulse_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name openpulse.example.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name openpulse.example.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/openpulse.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/openpulse.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/openpulse_access.log;
    error_log /var/log/nginx/openpulse_error.log;

    # API Proxy
    location /api/ {
        proxy_pass http://openpulse_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
   proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API Documentation
    location /docs {
        proxy_pass http://openpulse_api;
        proxy_set_header Host $host;
    }

    # Static Files
    location / {
        root /opt/openpulse/web-dashboard;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/openpulse /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Systemd Service (Alternative to Docker)

```ini
# /etc/systemd/system/openpulse-api.service

[Unit]
Description=OpenPulse API Service
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=openpulse
Group=openpulse
WorkingDirectory=/opt/openpulse
Environment="PATH=/opt/openpulse/venv/bin"
ExecStart=/opt/openpulse/venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/openpulse-celery.service

[Unit]
Description=OpenPulse Celery Worker
After=network.target redis.service

[Service]
Type=simple
User=openpulse
Group=openpulse
WorkingDirectory=/opt/openpulse
Environment="PATH=/opt/openpulse/venv/bin"
ExecStart=/opt/openpulse/venv/bin/celery -A src.tasks.celery_app worker --loglevel=info --concurrency=4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable openpulse-api openpulssudo systemctl start openpulse-api ulse-celery
sudo systemctl status openpulse-api openpulse-celery
```

---

## Docker Deployment

### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: openpulse-postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - openpulse-network
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: openpulse-redis
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - openpulse-network
    restart: always
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  iotdb:
    image: apache/iotdb:1.3.0-standalone
    container_name: openpulse-iotdb
    environment:
      - iotdb_enable_rest_service=true
    volumes:
      - iotdb_data:/iotdb/data
    ports:
      - "6667:6667"
    networks:
      - openpulse-network
    restart: always

  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: openpulse-api
    env_file:
      - .env.production
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      iotdb:
        condition: service_started
    networks:
      - openpulse-network
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

  celery-worker:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: openpulse-celery-worker
    command: celery -A src.tasks.celery_app worker --loglevel=info --concurrency=4
    env_file:
      - .env.production
    depends_on:
      - redis
      - postgres
      - iotdb
    networks:
      - openpulse-network
    restart: always
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '2'
          memory: 2G

  celery-beat:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: openpulse-celery-beat
    command: celery -A src.tasks.celery_app beat --loglevel=info
    env_file:
      - .env.production
    depends_on:
      - redis
    networks:
      - openpulse-network
    restart: always

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  iotdb_data:
    driver: local

networks:
  openpulse-network:
    driver: `

### Production Dockerfile

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 openpulse && \
    chown -R openpulse:openpulse /app

USER openpulse

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

## Kubernetes Deployment

### Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: openpulse
```

### ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: openpulse-config
  namespace: openpulse
data:
  DEBUG: "False"
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  OPENDIGGER_API_URL: "https://oss.x-lab.info/open_digger"
  IOTDB_HOST: "iotdb-service"
  IOTDB_PORT: "6667"
  POSTGRES_HOST: "postgres-service"
  POSTGRES_PORT: "5432"
  REDIS_HOST: "redis-service"
  REDIS_PORT: "6379"
```

### Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: openpulse-secrets
  namespace: openpulse
type: Opaque
stringData:
  POSTGRES_PASSWORD: "your-postgres-password"
  REDIS_PASSWORD: "your-redis-password"
  IOTDB_PASSWORD: "your-iotdb-password"
```

### PostgreSQL StatefulSet

```yaml
# k8s/postgres-statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: openpulse
spec:
  serviceName: postgres-service
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_USER
          value: "openpulse"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: openpulse-secrets
              key: POSTGRES_PASSWORD
        - name: POSTGRES_DB
          value: "openpulse"
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 50Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: openpulse
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
  clusterIP: None
```

### API Deployment

`k8s/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openpulse-api
  namespace: openpulse
spec:
  replicas: 3
  selector:
    matchLabels:
      app: openpulse-api
  template:
    metadata:
      labels:
        app: openpulse-api
    spec:
      containers:
      - name: api
        image: openpulse/api:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: openpulse-config
        - secretRef:
            name: openpulse-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: openpulse-api-service
  namespace: openpulse
spec:
  selector:
    app: openpulse-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: openpulse-ingress
  namespace: openpulse
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - openpulse.example.com
    secretName: openpulse-tls
  rules:
  - host: openpulse.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: openpulse-api-service
            port:
              number: 80
```
	o Kubernetes

```bash
# Apply all configurations
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/postgres-statefulset.yaml
kubectl apply -f k8s/redis-statefulset.yaml
kubectl apply -f k8s/iotdb-statefulset.yaml
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/celery-deployment.yaml
kubectl apply -f k8s/ingress.yaml

# Check status
kubectl get pods -n openpulse
kubectl get services -n openpulse
kubectl get ingress -n openpulse

# View logs
kubectl logs -f deployment/openpulse-api -n openpulse
```

---

## Configon

### Environment Variables

See `.env.example` for all available configuration options.

**Critical Settings:**

```bash
# Security
DEBUG=False  # MUST be False in production
SECRET_KEY=<generate-strong-secret>

# Database
POSTGRES_PASSWORD=<strong-password>
REDIS_PASSWORD=<strong-password>

# API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://yourdomain.com

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/openpulse/app.log
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Monitoring

### Prometheus Metrics

Add to `docker-compose.prod.yml`:

```yaml
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - openpulse-network
```

### Grafana Dashboard

```yaml
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - openpulse-network
```

### Log Aggregation

Use ELK Stack or Loki for centralized logging.

---

## Backup Strategy

### Database Backup

```bash
#!/bin/bash
# scripts/backup-postgres.sh

BACKUP_DIR="/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

docker-compose exec -T postgres pg_dump -U openpulse openpulse | \
  gzip > "$BACKUP_DIR/openpulse_$TIMESTAMP.sql.gz"

# Keep only last 7 days
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete
```

### Automated Backups

```bash
# Add to crontab
0 2 * * * /opt/openpulse/scripts/backup-postgres.sh
```

---

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for detailed troubleshooting guide.

---

## Security Checklist

- [ ] Change all default passwords
- [ ] Enable SSL/TLS
- [ ] Configure firewall rules
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerting
- [ ] Regular security updates
- [ ] Backup verification
- [ ] Access control configured
- [ ] Secrets management in place
- [ ] Security headers configured

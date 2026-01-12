# OpenPulse Scripts

This directory contains utility scripts for managing the OpenPulse platform.

## Available Scripts

### Database Management

#### `init-db.sh` / `init-db.bat`
Initialize the database with required tables and schemas.

```bash
# Linux/Mac
./scripts/init-db.sh

# Windows
scripts\init-db.bat
```

**What it does:**
- Waits for all services to be ready
- Creates database tables
- Runs migrations (if using Alembic)
- Creates IoTDB storage groups

#### `reset-db.py`
Reset the database by dropping and recreating all tables.

```bash
python scripts/reset-db.py
```

**⚠️ WARNING:** This will delete ALL data!

#### `seed-data.py`
Populate the database with sample test data.

```bash
python scripts/seed-data.py
```

**What it creates:**
- 10 sample repositories
- 50-100 contributors
- 300+ health score records
- 50-100 churn predictions

### Backup & Restore

#### `backup.sh`
Create backups of all databases.

```bash
./scripts/backup.sh
```

**What it backs up:**
- PostgreSQL database (compressed SQL dump)
- Redis data (RDB file)
- IoTDB data directory (tar.gz)

**Configuration:**
```bash
# Set backup directory (default: ./backups)
export BACKUP_DIR=/path/to/backups

# Set retention period (default: 7 days)
export RETENTION_DAYS=30

./scripts/backup.sh
```

**Automated backups:**
```bash
# Add to crontab for daily backups at 2 AM
0 2 * * * /opt/openpulse/scripts/backup.sh
```

#### `restore.sh`
Restore databases from a backup.

```bash
# List available backups
./scripts/restore.sh

# Restore specific backup
./scripts/restore.sh 20240113_020000
```

**⚠️ WARNING:** This will overwrite existing data!

### Testing & Diagnostics

#### `health-check.sh`
Check the health of all OpenPulse services.

```bash
./scripts/health-check.sh
```

**What it checks:**
- Docker daemon
- API endpoints
- PostgreSQL connection
- Redis connection
- IoTDB container
- Celery workers
- Disk space
- Memory usage

**Exit codes:**
- `0`: All checks passed
- `1`: One or more checks failed

**Use in monitoring:**
```bash
# Run every 5 minutes
*/5 * * * * /opt/openpulse/scripts/health-check.sh || /usr/bin/send-alert
```

#### `test-opendigger.py`
Test OpenDigger API connectivity and data fetching.

```bash
python scripts/test-opendigger.py
```

**What it tests:**
- OpenRank data
- Activity metrics
- Contributors list
- Stars count
- Forks count
- Issue response time

### Maintenance

#### `cleanup.sh`
Clean up Docker resources and temporary files.

```bash
./scripts/cleanup.sh
```

**What it can clean:**
- Stop services
- Remove volumes (data)
- Remove Docker images
- Python cache files
- Log files
- Test artifacts
- Build artifacts

**Interactive:** The script will ask for confirmation before each action.

## Usage Examples

### Fresh Installation

```bash
# 1. Start services
docker-compose up -d

# 2. Initialize database
./scripts/init-db.sh

# 3. Seed test data
python scripts/seed-data.py

# 4. Check health
./scripts/health-check.sh
```

### Daily Operations

```bash
# Morning health check
./scripts/health-check.sh

# Create backup
./scripts/backup.sh

# Test external API
python scripts/test-opendigger.py
```

### Troubleshooting

```bash
# Reset everything
./scripts/cleanup.sh  # Remove all data
docker-compose up -d  # Restart services
./scripts/init-db.sh  # Reinitialize
python scripts/seed-data.py  # Add test data
```

### Development Workflow

```bash
# Reset database for testing
python scripts/reset-db.py

# Seed fresh test data
python scripts/seed-data.py

# Run your tests
pytest tests/

# Clean up after development
./scripts/cleanup.sh
```

## Script Permissions

Make scripts executable on Linux/Mac:

```bash
chmod +x scripts/*.sh
```

## Environment Variables

Scripts use environment variables from `.env` file:

```bash
# Database
POSTGRES_USER=openpulse
POSTGRES_PASSWORD=openpulse
POSTGRES_DB=openpulse

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Backup
BACKUP_DIR=./backups
RETENTION_DAYS=7
```

## Automation

### Cron Jobs

```bash
# Edit crontab
crontab -e

# Add these lines:
# Daily backup at 2 AM
0 2 * * * /opt/openpulse/scripts/backup.sh

# Health check every 5 minutes
*/5 * * * * /opt/openpulse/scripts/health-check.sh

# Weekly cleanup of old logs
0 3 * * 0 find /opt/openpulse/logs -name "*.log" -mtime +30 -delete
```

### Systemd Timers

```ini
# /etc/systemd/system/openpulse-backup.timer
[Unit]
Description=OpenPulse Daily Backup

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

```ini
# /etc/systemd/system/openpulse-backup.service
[Unit]
Description=OpenPulse Backup Service

[Service]
Type=oneshot
ExecStart=/opt/openpulse/scripts/backup.sh
User=openpulse
```

Enable timer:
```bash
sudo systemctl enable openpulse-backup.timer
sudo systemctl start openpulse-backup.timer
```

## Troubleshooting Scripts

### Script Won't Execute

```bash
# Check permissions
ls -l scripts/

# Make executable
chmod +x scripts/*.sh

# Check line endings (Windows vs Unix)
dos2unix scripts/*.sh
```

### Docker Commands Fail

```bash
# Ensure Docker is running
docker info

# Check if services are up
docker-compose ps

# Check Docker Compose version
docker-compose --version
```

### Python Scripts Fail

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Check Python path
which python
python --version
```

## Contributing

When adding new scripts:

1. Add executable permissions: `chmod +x script.sh`
2. Add shebang line: `#!/bin/bash` or `#!/usr/bin/env python3`
3. Add error handling: `set -e` for bash
4. Add documentation to this README
5. Test on both Linux and Windows (if applicable)

## Support

For issues with scripts:
- Check logs: `docker-compose logs`
- Run health check: `./scripts/health-check.sh`
- See troubleshooting guide: `docs/troubleshooting.md`
- Open issue: https://github.com/hwk603/openPulse/issues

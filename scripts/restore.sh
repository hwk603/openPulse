#!/bin/bash
# Restore OpenPulse databases from backup

set -e

# Check if backup timestamp is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <backup_timestamp>"
    echo ""
    echo "Available backups:"
    ls -1 backups/ | grep "postgres_" | sed 's/postgres_/  /' | sed 's/.sql.gz//'
    exit 1
fi

TIMESTAMP=$1
BACKUP_DIR="${BACKUP_DIR:-./backups}"

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "⚠️  WARNING: This will overwrite existing data!"
echo "📦 Restoring from backup: $TIMESTAMP"
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "❌ Restore cancelled"
    exit 0
fi

# Stop services
echo "🛑 Stopping services..."
docker-compose stop api celery-worker celery-beat

# Restore PostgreSQL
if [ -f "$BACKUP_DIR/postgres_$TIMESTAMP.sql.gz" ]; then
    echo "📊 Restoring PostgreSQL..."

    # Drop and recreate database
    docker-compose exec -T postgres psql -U ${POSTGRES_USER:-openpulse} -c "DROP DATABASE IF EXISTS ${POSTGRES_DB:-openpulse};"
    docker-compose exec -T postgres psql -U ${POSTGRES_USER:-openpulse} -c "CREATE DATABASE ${POSTGRES_DB:-openpulse};"

    # Restore from backup
    gunzip -c "$BACKUP_DIR/postgres_$TIMESTAMP.sql.gz" | \
        docker-compose exec -T postgres psql -U ${POSTGRES_USER:-openpulse} ${POSTGRES_DB:-openpulse}

    echo "✅ PostgreSQL restored"
else
    echo "❌ PostgreSQL backup not found: $BACKUP_DIR/postgres_$TIMESTAMP.sql.gz"
    exit 1
fi

# Restore Redis
if [ -f "$BACKUP_DIR/redis_$TIMESTAMP.rdb" ]; then
    echo "💾 Restoring Redis..."

    docker-compose stop redis
    docker cp "$BACKUP_DIR/redis_$TIMESTAMP.rdb" $(docker-compose ps -q redis):/data/dump.rdb
    docker-compose start redis

    echo "✅ Redis restored"
else
    echo "⚠️  Redis backup not found, skipping"
fi

# Restore IoTDB
if [ -f "$BACKUP_DIR/iotdb_$TIMESTAMP.tar.gz" ]; then
    echo "📈 Restoring IoTDB..."

    docker-compose stop iotdb
    docker cp "$BACKUP_DIR/iotdb_$TIMESTAMP.tar.gz" $(docker-compose ps -q iotdb):/tmp/iotdb_backup.tar.gz
    docker-compose exec -T iotdb sh -c "rm -rf /iotdb/data/* && tar xzf /tmp/iotdb_backup.tar.gz -C /iotdb/data"
    docker-compose start iotdb

    echo "✅ IoTDB restored"
else
    echo "⚠️  IoTDB backup not found, skipping"
fi

# Start services
echo "🚀 Starting services..."
docker-compose start api celery-worker celery-beat

echo ""
echo "🎉 Restore completed successfully!"
echo "✅ All services are running"

#!/bin/bash
# Backup OpenPulse databases

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS="${RETENTION_DAYS:-7}"

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "🔄 Starting OpenPulse backup at $(date)"
echo "📁 Backup directory: $BACKUP_DIR"

# Backup PostgreSQL
echo "📊 Backing up PostgreSQL..."
docker-compose exec -T postgres pg_dump -U ${POSTGRES_USER:-openpulse} ${POSTGRES_DB:-openpulse} | \
    gzip > "$BACKUP_DIR/postgres_$TIMESTAMP.sql.gz"

if [ $? -eq 0 ]; then
    POSTGRES_SIZE=$(du -h "$BACKUP_DIR/postgres_$TIMESTAMP.sql.gz" | cut -f1)
    echo "✅ PostgreSQL backup completed: postgres_$TIMESTAMP.sql.gz ($POSTGRES_SIZE)"
else
    echo "❌ PostgreSQL backup failed"
    exit 1
fi

# Backup Redis
echo "💾 Backing up Redis..."
docker-compose exec -T redis redis-cli --rdb /data/dump.rdb SAVE > /dev/null 2>&1
docker cp $(docker-compose ps -q redis):/data/dump.rdb "$BACKUP_DIR/redis_$TIMESTAMP.rdb"

if [ $? -eq 0 ]; then
    REDIS_SIZE=$(du -h "$BACKUP_DIR/redis_$TIMESTAMP.rdb" | cut -f1)
    echo "✅ Redis backup completed: redis_$TIMESTAMP.rdb ($REDIS_SIZE)"
else
    echo "❌ Redis backup failed"
fi

# Backup IoTDB data directory
echo "📈 Backing up IoTDB..."
docker-compose exec -T iotdb tar czf /tmp/iotdb_backup.tar.gz -C /iotdb/data . 2>/dev/null
docker cp $(docker-compose ps -q iotdb):/tmp/iotdb_backup.tar.gz "$BACKUP_DIR/iotdb_$TIMESTAMP.tar.gz"

if [ $? -eq 0 ]; then
    IOTDB_SIZE=$(du -h "$BACKUP_DIR/iotdb_$TIMESTAMP.tar.gz" | cut -f1)
    echo "✅ IoTDB backup completed: iotdb_$TIMESTAMP.tar.gz ($IOTDB_SIZE)"
else
    echo "⚠️  IoTDB backup failed or no data to backup"
fi

# Clean up old backups
echo "🧹 Cleaning up old backups (older than $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.rdb" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

# Create backup manifest
cat > "$BACKUP_DIR/manifest_$TIMESTAMP.txt" << EOF
OpenPulse Backup Manifest
========================
Timestamp: $(date)
Backup ID: $TIMESTAMP

Files:
- postgres_$TIMESTAMP.sql.gz
- redis_$TIMESTAMP.rdb
- iotdb_$TIMESTAMP.tar.gz

Environment:
- PostgreSQL User: ${POSTGRES_USER:-openpulse}
- PostgreSQL DB: ${POSTGRES_DB:-openpulse}
- Redis DB: ${REDIS_DB:-0}

Retention: $RETENTION_DAYS days
EOF

echo "✅ Backup manifest created: manifest_$TIMESTAMP.txt"

# Calculate total backup size
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
echo ""
echo "🎉 Backup completed successfully!"
echo "📦 Total backup size: $TOTAL_SIZE"
echo "📁 Backup location: $BACKUP_DIR"
echo ""

# List recent backups
echo "📋 Recent backups:"
ls -lht "$BACKUP_DIR" | head -n 10

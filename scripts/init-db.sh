#!/bin/bash
# Initialize OpenPulse database

set -e

echo "🚀 Initializing OpenPulse Database..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "❌ .env file not found. Please create one from .env.example"
    exit 1
fi

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until docker-compose exec -T postgres pg_isready -U ${POSTGRES_USER} > /dev/null 2>&1; do
    echo "   PostgreSQL is unavailable - sleeping"
    sleep 2
done
echo "✅ PostgreSQL is ready"

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
until docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; do
    echo "   Redis is unavailable - sleeping"
    sleep 2
done
echo "✅ Redis is ready"

# Wait for IoTDB to be ready
echo "⏳ Waiting for IoTDB to be ready..."
sleep 10  # IoTDB takes longer to start
echo "✅ IoTDB should be ready"

# Create database tables
echo "📊 Creating database tables..."
python -c "from src.database import init_db; init_db()"
echo "✅ Database tables created"

# Run migrations (if using Alembic)
if [ -d "alembic" ]; then
    echo "🔄 Running database migrations..."
    alembic upgrade head
    echo "✅ Migrations completed"
fi

# Create IoTDB storage groups
echo "📈 Creating IoTDB storage groups..."
python -c "
from src.storage.iotdb_client import IoTDBClient
client = IoTDBClient()
try:
    client.session.set_storage_group('root.openpulse')
    print('✅ IoTDB storage group created')
except Exception as e:
    print(f'⚠️  Storage group may already exist: {e}')
"

echo ""
echo "🎉 Database initialization completed successfully!"
echo ""
echo "Next steps:"
echo "  1. Start the API server: uvicorn src.api.main:app --reload"
echo "  2. Start Celery worker: celery -A src.tasks.celery_app worker --loglevel=info"
echo "  3. Visit API docs: http://localhost:8000/docs"

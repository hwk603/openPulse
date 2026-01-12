#!/bin/bash

# OpenPulse Quick Start Script

echo "🔮 OpenPulse - Starting services..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs data/raw data/processed

# Copy .env.example to .env if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
fi

# Start services
echo "🚀 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "✅ Checking service status..."
docker-compose ps

echo ""
echo "🎉 OpenPulse is ready!"
echo ""
echo "📊 Access the services:"
echo "  - API Documentation: http://localhost:8000/docs"
echo "  - API ReDoc: http://localhost:8000/redoc"
echo "  - Web Dashboard: Open web-dashboard/index.html in your browser"
echo ""
echo "🔧 Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop services: docker-compose down"
echo "  - Restart services: docker-compose restart"
echo ""
echo "📖 For more information, see README.md"

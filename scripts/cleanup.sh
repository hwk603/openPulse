#!/bin/bash
# Clean up Docker resources used by OpenPulse

set -e

echo "🧹 OpenPulse Cleanup Script"
echo "=========================="
echo ""

# Function to ask for confirmation
confirm() {
    read -p "$1 (yes/no): " response
    if [ "$response" != "yes" ]; then
        return 1
    fi
    return 0
}

# Stop all services
if confirm "Stop all OpenPulse services?"; then
    echo "🛑 Stopping services..."
    docker-compose down
    echo "✅ Services stopped"
fi

# Remove volumes (data will be lost!)
if confirm "⚠️  Remove all data volumes? (THIS WILL DELETE ALL DATA)"; then
    echo "🗑️  Removing volumes..."
    docker-compose down -v
    echo "✅ Volumes removed"
fi

# Remove Docker images
if confirm "Remove OpenPulse Docker images?"; then
    echo "🗑️  Removing images..."
    docker-compose down --rmi local
    echo "✅ Images removed"
fi

# Clean up Python cache
if confirm "Clean up Python cache files?"; then
    echo "🧹 Cleaning Python cache..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    echo "✅ Python cache cleaned"
fi

# Clean up logs
if confirm "Clean up log files?"; then
    echo "🧹 Cleaning logs..."
    rm -rf logs/*.log 2>/dev/null || true
    echo "✅ Logs cleaned"
fi

# Clean up test artifacts
if confirm "Clean up test artifacts?"; then
    echo "🧹 Cleaning test artifacts..."
    rm -rf .pytest_cache 2>/dev/null || true
    rm -rf htmlcov 2>/dev/null || true
    rm -rf .coverage 2>/dev/null || true
    echo "✅ Test artifacts cleaned"
fi

# Clean up build artifacts
if confirm "Clean up build artifacts?"; then
    echo "🧹 Cleaning build artifacts..."
    rm -rf build dist *.egg-info 2>/dev/null || true
    echo "✅ Build artifacts cleaned"
fi

echo ""
echo "🎉 Cleanup completed!"
echo ""
echo "To start fresh:"
echo "  1. docker-compose up -d"
echo "  2. python scripts/init-db.sh"
echo "  3. python scripts/seed-data.py"

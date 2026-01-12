#!/bin/bash
# Health check script for OpenPulse services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
TOTAL=0
PASSED=0
FAILED=0

# Function to check service
check_service() {
    local service_name=$1
    local check_command=$2

    TOTAL=$((TOTAL + 1))

    if eval "$check_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $service_name is healthy"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $service_name is down"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

echo "🏥 OpenPulse Health Check"
echo "========================="
echo ""

# Check Docker
echo "🐳 Docker Services:"
check_service "Docker daemon" "docker info"

# Check API
echo ""
echo "🌐 API Service:"
check_service "API health endpoint" "curl -f http://localhost:8000/health"
check_service "API docs endpoint" "curl -f http://localhost:8000/docs"

# Check PostgreSQL
echo ""
echo "🐘 PostgreSQL:"
check_service "PostgreSQL connection" "docker-compose exec -T postgres pg_isready -U openpulse"
check_service "PostgreSQL database" "docker-compose exec -T postgres psql -U openpulse -d openpulse -c 'SELECT 1'"

# Check Redis
echo ""
echo "💾 Redis:"
check_service "Redis ping" "docker-compose exec -T redis redis-cli ping"
check_service "Redis info" "docker-compose exec -T redis redis-cli info server"

# Check IoTDB
echo ""
echo "📈 IoTDB:"
check_service "IoTDB container" "docker-compose ps iotdb | grep -q 'Up'"
# Note: IoTDB CLI check is complex, so we just check if container is running

# Check Celery
echo ""
echo "⚙️  Celery:"
check_service "Celery worker" "docker-compose exec -T celery-worker celery -A src.tasks.celery_app inspect ping"
check_service "Celery beat" "docker-compose ps celery-beat | grep -q 'Up'"

# Check disk space
echo ""
echo "💽 Disk Space:"
DISK_USAGE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo -e "${GREEN}✓${NC} Disk usage: ${DISK_USAGE}%"
    PASSED=$((PASSED + 1))
elif [ "$DISK_USAGE" -lt 90 ]; then
    echo -e "${YELLOW}⚠${NC} Disk usage: ${DISK_USAGE}% (warning)"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗${NC} Disk usage: ${DISK_USAGE}% (critical)"
    FAILED=$((FAILED + 1))
fi
TOTAL=$((TOTAL + 1))

# Check memory
echo ""
echo "🧠 Memory:"
if command -v free > /dev/null; then
    MEM_USAGE=$(free | awk 'NR==2 {printf "%.0f", $3/$2 * 100}')
    if [ "$MEM_USAGE" -lt 80 ]; then
        echo -e "${GREEN}✓${NC} Memory usage: ${MEM_USAGE}%"
        PASSED=$((PASSED + 1))
    elif [ "$MEM_USAGE" -lt 90 ]; then
        echo -e "${YELLOW}⚠${NC} Memory usage: ${MEM_USAGE}% (warning)"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗${NC} Memory usage: ${MEM_USAGE}% (critical)"
        FAILED=$((FAILED + 1))
    fi
    TOTAL=$((TOTAL + 1))
fi

# Summary
echo ""
echo "========================="
echo "📊 Summary:"
echo "   Total checks: $TOTAL"
echo -e "   ${GREEN}Passed: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "   ${RED}Failed: $FAILED${NC}"
fi

# Exit code
if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 All systems operational!${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}⚠️  Some services are not healthy${NC}"
    echo "Run 'docker-compose logs' to investigate"
    exit 1
fi

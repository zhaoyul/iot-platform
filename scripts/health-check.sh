#!/bin/bash
# Health check script for all services
# Verifies that the Industrial DevOps Platform is running correctly

set -e

echo "========================================="
echo "Industrial DevOps Platform Health Check"
echo "========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_service() {
    local service_name=$1
    local check_command=$2
    
    echo -n "Checking $service_name... "
    
    if eval "$check_command" &> /dev/null; then
        echo -e "${GREEN}✓${NC}"
        return 0
    else
        echo -e "${RED}✗${NC}"
        return 1
    fi
}

check_http() {
    local service_name=$1
    local url=$2
    local expected_code=${3:-200}
    
    echo -n "Checking $service_name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$response" = "$expected_code" ] || [ "$response" = "302" ] || [ "$response" = "301" ]; then
        echo -e "${GREEN}✓ (HTTP $response)${NC}"
        return 0
    else
        echo -e "${RED}✗ (HTTP $response)${NC}"
        return 1
    fi
}

# Docker services
echo "Docker Services:"
check_service "Docker daemon" "docker info"
check_service "Docker Compose" "docker-compose version"
echo ""

# Container status
echo "Container Status:"
check_service "Forgejo container" "docker ps | grep -q forgejo"
check_service "PostgreSQL container" "docker ps | grep -q forgejo-db"
check_service "MinIO container" "docker ps | grep -q forgejo-minio"
check_service "Keycloak container" "docker ps | grep -q forgejo-keycloak"
check_service "Oxidized container" "docker ps | grep -q oxidized"
check_service "Elasticsearch container" "docker ps | grep -q forgejo-elasticsearch"
echo ""

# HTTP endpoints
echo "HTTP Endpoints:"
check_http "Forgejo Web" "http://localhost:3000"
check_http "MinIO API" "http://localhost:9000/minio/health/live"
check_http "MinIO Console" "http://localhost:9001"
check_http "Keycloak" "http://localhost:8080"
check_http "Elasticsearch" "http://localhost:9200"
echo ""

# Database connectivity
echo "Database:"
if docker exec forgejo-db pg_isready -U forgejo &> /dev/null; then
    echo -e "PostgreSQL: ${GREEN}✓${NC}"
    
    # Check database size
    db_size=$(docker exec forgejo-db psql -U forgejo -d forgejo -t -c "SELECT pg_size_pretty(pg_database_size('forgejo'));" 2>/dev/null | xargs)
    echo "  Database size: $db_size"
else
    echo -e "PostgreSQL: ${RED}✗${NC}"
fi
echo ""

# Storage
echo "Storage:"
# Check disk space
df -h | grep -E "Filesystem|/dev/" | head -5

echo ""
echo "Data directories:"
for dir in data/{forgejo,postgres,minio,elasticsearch,oxidized}; do
    if [ -d "$dir" ]; then
        size=$(du -sh "$dir" 2>/dev/null | cut -f1)
        echo -e "  $dir: ${GREEN}$size${NC}"
    else
        echo -e "  $dir: ${YELLOW}not found${NC}"
    fi
done
echo ""

# Git operations
echo "Git Operations:"
if timeout 5 git ls-remote http://localhost:3000/explore/repos &> /dev/null; then
    echo -e "Git protocol: ${GREEN}✓${NC}"
else
    echo -e "Git protocol: ${YELLOW}not tested (no repos)${NC}"
fi
echo ""

# Resource usage
echo "Resource Usage:"
echo "CPU:"
top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print "  Usage: " 100 - $1 "%"}'

echo "Memory:"
free -h | awk '/^Mem:/ {print "  Total: " $2 "\n  Used: " $3 "\n  Free: " $4}'

echo ""
echo "Top containers by memory:"
docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}" | head -6
echo ""

# Final summary
echo "========================================="
echo "Health Check Complete"
echo "========================================="
echo ""
echo "For detailed logs, run:"
echo "  docker-compose logs -f [service-name]"
echo ""

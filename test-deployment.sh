#!/bin/bash
# Comprehensive deployment validation script for Geo Risk Application
# Tests all services, endpoints, and integration points

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
print_header() {
    echo -e "\n${YELLOW}=== $1 ===${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
    ((TESTS_PASSED++))
}

print_error() {
    echo -e "${RED}✗${NC} $1"
    ((TESTS_FAILED++))
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    print_info "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -sf "$url" > /dev/null 2>&1; then
            print_success "$service_name is ready"
            return 0
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    print_error "$service_name failed to start within $((max_attempts * 2)) seconds"
    return 1
}

# Test 1: Check Docker and Docker Compose
print_header "Checking Prerequisites"

if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    print_success "Docker installed: $DOCKER_VERSION"
else
    print_error "Docker is not installed"
    exit 1
fi

if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    print_success "Docker Compose installed: $COMPOSE_VERSION"
else
    print_error "Docker Compose is not installed"
    exit 1
fi

# Test 2: Check environment file
print_header "Checking Configuration"

if [ -f ".env" ]; then
    print_success ".env file exists"
else
    print_error ".env file not found. Copy .env.example to .env"
    exit 1
fi

# Check for required variables
required_vars=("POSTGRES_USER" "POSTGRES_PASSWORD" "POSTGRES_DB" "SECRET_KEY")
for var in "${required_vars[@]}"; do
    if grep -q "^$var=" .env; then
        print_success "$var is set in .env"
    else
        print_error "$var is missing from .env"
    fi
done

# Test 3: Build containers
print_header "Building Docker Containers"

print_info "Building containers (this may take a few minutes)..."
if docker-compose build --quiet 2>&1 | grep -q "ERROR"; then
    print_error "Failed to build containers"
    docker-compose build
    exit 1
else
    print_success "All containers built successfully"
fi

# Test 4: Start services
print_header "Starting Services"

print_info "Starting all services..."
docker-compose up -d

if [ $? -eq 0 ]; then
    print_success "All services started"
else
    print_error "Failed to start services"
    exit 1
fi

# Wait a bit for services to initialize
sleep 5

# Test 5: Check container status
print_header "Checking Container Status"

containers=("georisk_db" "georisk_backend" "georisk_frontend" "georisk_nginx")
for container in "${containers[@]}"; do
    if docker ps --filter "name=$container" --filter "status=running" | grep -q "$container"; then
        print_success "$container is running"
    else
        print_error "$container is not running"
        docker-compose logs "$container" | tail -20
    fi
done

# Test 6: Wait for services to be healthy
print_header "Waiting for Services to be Healthy"

wait_for_service "http://localhost:8000/health" "Backend API" || true
wait_for_service "http://localhost:3000/health" "Frontend" || true
wait_for_service "http://localhost/health" "Nginx Proxy" || true

# Test 7: Database connectivity
print_header "Testing Database Connectivity"

DB_TEST=$(docker-compose exec -T db psql -U georisk -d georisk_db -c "SELECT 1;" 2>&1)
if echo "$DB_TEST" | grep -q "1 row"; then
    print_success "Database is accessible"
else
    print_error "Database connection failed"
fi

# Test tables exist
TABLES_TEST=$(docker-compose exec -T db psql -U georisk -d georisk_db -c "\dt" 2>&1)
if echo "$TABLES_TEST" | grep -q "locations"; then
    print_success "Database tables created"
else
    print_error "Database tables not found"
fi

# Test 8: Backend API endpoints
print_header "Testing Backend API Endpoints"

# Health check
HEALTH=$(curl -s http://localhost:8000/health)
if echo "$HEALTH" | grep -q "healthy"; then
    print_success "Backend health check: OK"
else
    print_error "Backend health check: FAILED"
fi

# Root endpoint
ROOT=$(curl -s http://localhost:8000/)
if echo "$ROOT" | grep -q "Geo Risk"; then
    print_success "Backend root endpoint: OK"
else
    print_error "Backend root endpoint: FAILED"
fi

# Locations endpoint
LOCATIONS=$(curl -s http://localhost:8000/api/locations)
if echo "$LOCATIONS" | grep -q "San Francisco" || echo "$LOCATIONS" | grep -q "\[\]"; then
    print_success "Locations API endpoint: OK"
else
    print_error "Locations API endpoint: FAILED"
fi

# Hazards endpoint
HAZARDS=$(curl -s http://localhost:8000/api/hazards)
if echo "$HAZARDS" | grep -q "earthquake" || echo "$HAZARDS" | grep -q "\[\]"; then
    print_success "Hazards API endpoint: OK"
else
    print_error "Hazards API endpoint: FAILED"
fi

# Test 9: Frontend endpoints
print_header "Testing Frontend"

# Frontend health
FRONTEND_HEALTH=$(curl -s http://localhost:3000/health)
if echo "$FRONTEND_HEALTH" | grep -q "healthy"; then
    print_success "Frontend health check: OK"
else
    print_error "Frontend health check: FAILED"
fi

# Frontend index page
FRONTEND_INDEX=$(curl -s http://localhost:3000/)
if echo "$FRONTEND_INDEX" | grep -q "<!DOCTYPE html>"; then
    print_success "Frontend serves HTML: OK"
else
    print_error "Frontend HTML: FAILED"
fi

# Test 10: Nginx reverse proxy
print_header "Testing Nginx Reverse Proxy"

# Nginx health
NGINX_HEALTH=$(curl -s http://localhost/health)
if echo "$NGINX_HEALTH" | grep -q "healthy"; then
    print_success "Nginx health check: OK"
else
    print_error "Nginx health check: FAILED"
fi

# API proxying through nginx
NGINX_API=$(curl -s http://localhost/api/locations)
if echo "$NGINX_API" | grep -q "San Francisco" || echo "$NGINX_API" | grep -q "\[\]"; then
    print_success "Nginx API proxy: OK"
else
    print_error "Nginx API proxy: FAILED"
fi

# Frontend proxying through nginx
NGINX_FRONTEND=$(curl -s http://localhost/)
if echo "$NGINX_FRONTEND" | grep -q "<!DOCTYPE html>"; then
    print_success "Nginx frontend proxy: OK"
else
    print_error "Nginx frontend proxy: FAILED"
fi

# API docs through nginx
NGINX_DOCS=$(curl -s http://localhost/docs)
if echo "$NGINX_DOCS" | grep -q "OpenAPI" || echo "$NGINX_DOCS" | grep -q "swagger"; then
    print_success "Nginx docs proxy: OK"
else
    print_error "Nginx docs proxy: FAILED"
fi

# Test 11: CORS headers
print_header "Testing CORS Configuration"

CORS_HEADERS=$(curl -s -I -X OPTIONS http://localhost/api/locations)
if echo "$CORS_HEADERS" | grep -qi "Access-Control-Allow"; then
    print_success "CORS headers configured: OK"
else
    print_error "CORS headers: MISSING"
fi

# Test 12: Database initialization
print_header "Testing Database Initialization"

# Check if sample data exists
LOCATION_COUNT=$(docker-compose exec -T db psql -U georisk -d georisk_db -t -c "SELECT COUNT(*) FROM locations;" 2>/dev/null | tr -d ' ')
if [ "$LOCATION_COUNT" -gt 0 ]; then
    print_success "Sample locations loaded: $LOCATION_COUNT locations"
else
    print_info "No sample locations found (may need to run init_db.py)"
fi

HAZARD_COUNT=$(docker-compose exec -T db psql -U georisk -d georisk_db -t -c "SELECT COUNT(*) FROM hazards;" 2>/dev/null | tr -d ' ')
if [ "$HAZARD_COUNT" -gt 0 ]; then
    print_success "Sample hazards loaded: $HAZARD_COUNT hazards"
else
    print_info "No sample hazards found (may need to run init_db.py)"
fi

# Test 13: Integration test - Create and assess risk
print_header "Testing End-to-End Risk Assessment"

# Create a test location
TEST_LOCATION=$(curl -s -X POST http://localhost/api/locations \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Test City",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "population_density": 10000,
        "building_code_rating": 7.5,
        "infrastructure_quality": 8.0
    }' 2>&1)

if echo "$TEST_LOCATION" | grep -q "Test City"; then
    print_success "Location creation: OK"
    
    # Extract location ID (simple grep approach)
    LOCATION_ID=$(echo "$TEST_LOCATION" | grep -o '"id":[0-9]*' | grep -o '[0-9]*' | head -1)
    
    if [ -n "$LOCATION_ID" ]; then
        # Assess risk for the location
        RISK_ASSESSMENT=$(curl -s -X POST http://localhost/api/assess-risk \
            -H "Content-Type: application/json" \
            -d "{
                \"location_id\": $LOCATION_ID,
                \"hazard_types\": [\"earthquake\"]
            }" 2>&1)
        
        if echo "$RISK_ASSESSMENT" | grep -q "risk_score"; then
            print_success "Risk assessment: OK"
        else
            print_error "Risk assessment: FAILED"
        fi
    else
        print_info "Could not extract location ID for risk assessment test"
    fi
else
    print_error "Location creation: FAILED"
fi

# Test 14: Container logs check
print_header "Checking for Errors in Logs"

ERROR_COUNT=$(docker-compose logs 2>&1 | grep -i "error" | grep -v "0 errors" | wc -l)
if [ "$ERROR_COUNT" -eq 0 ]; then
    print_success "No errors found in logs"
else
    print_info "Found $ERROR_COUNT error messages in logs (review recommended)"
fi

# Test 15: Resource usage
print_header "Checking Resource Usage"

docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep georisk
print_success "Resource usage displayed above"

# Final summary
print_header "Test Summary"

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
echo -e "\nTotal Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed! Deployment is successful.${NC}\n"
    echo "You can now access:"
    echo "  - Application: http://localhost"
    echo "  - API Docs: http://localhost/docs"
    echo "  - Backend API: http://localhost:8000"
    echo "  - Frontend: http://localhost:3000"
    exit 0
else
    echo -e "\n${RED}⚠️  Some tests failed. Please review the output above.${NC}\n"
    echo "To view logs:"
    echo "  docker-compose logs"
    echo ""
    echo "To stop services:"
    echo "  docker-compose down"
    exit 1
fi

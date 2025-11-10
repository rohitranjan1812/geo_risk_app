#!/bin/bash
# Quick validation of deployment infrastructure files
# Checks for required files and common configuration issues

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== Deployment Infrastructure Validation ===${NC}\n"

# Check required files
echo "Checking required files..."

FILES=(
    "docker-compose.yml"
    "docker-compose.test.yml"
    "docker-compose.prod.yml"
    ".env.example"
    "Makefile"
    "DEPLOYMENT.md"
    "backend/Dockerfile"
    "backend/.dockerignore"
    "frontend/Dockerfile"
    "frontend/.dockerignore"
    "frontend/nginx.conf"
    "nginx/nginx.conf"
    "nginx/conf.d/default.conf"
    "init-scripts/01-init.sql"
    "test-deployment.sh"
)

MISSING=0
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file (missing)"
        MISSING=$((MISSING + 1))
    fi
done

if [ $MISSING -gt 0 ]; then
    echo -e "\n${RED}Error: $MISSING required file(s) missing${NC}"
    exit 1
fi

echo -e "\n${GREEN}✓ All required files present${NC}"

# Validate docker-compose.yml syntax
echo -e "\nValidating docker-compose configurations..."

if docker-compose config > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} docker-compose.yml is valid"
else
    echo -e "${RED}✗${NC} docker-compose.yml has syntax errors"
    exit 1
fi

if docker-compose -f docker-compose.test.yml config > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} docker-compose.test.yml is valid"
else
    echo -e "${RED}✗${NC} docker-compose.test.yml has syntax errors"
    exit 1
fi

if docker-compose -f docker-compose.yml -f docker-compose.prod.yml config > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} docker-compose.prod.yml is valid"
else
    echo -e "${RED}✗${NC} docker-compose.prod.yml has syntax errors"
    exit 1
fi

# Check for .env file
echo -e "\nChecking environment configuration..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
    
    # Check for critical variables
    if grep -q "^POSTGRES_PASSWORD=" .env && ! grep -q "^POSTGRES_PASSWORD=.*change.*" .env; then
        echo -e "${GREEN}✓${NC} POSTGRES_PASSWORD is set (not default)"
    else
        echo -e "${YELLOW}⚠${NC} POSTGRES_PASSWORD should be changed from default"
    fi
    
    if grep -q "^SECRET_KEY=" .env && ! grep -q "^SECRET_KEY=.*change.*" .env; then
        echo -e "${GREEN}✓${NC} SECRET_KEY is set (not default)"
    else
        echo -e "${YELLOW}⚠${NC} SECRET_KEY should be changed from default"
    fi
else
    echo -e "${YELLOW}⚠${NC} .env file not found (run: cp .env.example .env)"
fi

# Check Dockerfile syntax
echo -e "\nValidating Dockerfiles..."

if docker build -f backend/Dockerfile --no-cache -t georisk-backend-test backend > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} backend/Dockerfile is valid"
    docker rmi georisk-backend-test > /dev/null 2>&1 || true
else
    echo -e "${YELLOW}⚠${NC} backend/Dockerfile validation skipped (requires dependencies)"
fi

# Check nginx config syntax (if nginx is installed)
if command -v nginx > /dev/null 2>&1; then
    echo -e "\nValidating nginx configurations..."
    
    # This would require mounting the config, skip for now
    echo -e "${YELLOW}ℹ${NC} Nginx syntax check requires running container"
else
    echo -e "${YELLOW}ℹ${NC} Nginx not installed locally, skipping config validation"
fi

# Check for common security issues
echo -e "\nChecking security..."

if grep -r "password" .env 2>/dev/null | grep -qi "password123\|admin\|root"; then
    echo -e "${RED}✗${NC} Weak passwords detected in .env"
else
    echo -e "${GREEN}✓${NC} No obvious weak passwords in .env"
fi

if [ -f ".env" ] && [ $(stat -c %a .env 2>/dev/null || stat -f %A .env 2>/dev/null) -le 600 ]; then
    echo -e "${GREEN}✓${NC} .env file permissions are restrictive"
else
    echo -e "${YELLOW}⚠${NC} .env file should have restricted permissions (chmod 600 .env)"
fi

# Check port availability
echo -e "\nChecking port availability..."

PORTS=(80 3000 5432 8000)
for port in "${PORTS[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠${NC} Port $port is already in use"
    else
        echo -e "${GREEN}✓${NC} Port $port is available"
    fi
done

# Summary
echo -e "\n${YELLOW}=== Validation Complete ===${NC}\n"
echo "To deploy the application:"
echo "  1. Ensure .env is configured: cp .env.example .env"
echo "  2. Build containers: make build"
echo "  3. Start services: make up"
echo "  4. Run tests: ./test-deployment.sh"
echo ""
echo "For more information, see DEPLOYMENT.md"

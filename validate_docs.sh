#!/bin/bash

# Documentation Validation Script

echo "════════════════════════════════════════════════════════"
echo "     GEO RISK - DOCUMENTATION VALIDATION"
echo "════════════════════════════════════════════════════════"
echo

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 exists"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} $1 missing"
        ((FAIL++))
    fi
}

check_content() {
    if grep -q "$2" "$1" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $1 contains: $3"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} $1 missing: $3"
        ((FAIL++))
    fi
}

echo "1. Checking Documentation Files..."
echo "───────────────────────────────────────────────────────"
check_file "README.md"
check_file "docs/API_DOCS.md"
check_file "docs/USER_MANUAL.md"
check_file "docs/DEVELOPMENT.md"
check_file "DEPLOYMENT.md"
echo

echo "2. Checking README Content..."
echo "───────────────────────────────────────────────────────"
check_content "README.md" "Quick Start" "Quick start section"
check_content "README.md" "Architecture" "Architecture section"
check_content "README.md" "Tech Stack" "Tech stack section"
check_content "README.md" "Testing" "Testing section"
check_content "README.md" "docker-compose up" "Docker commands"
echo

echo "3. Checking API Documentation..."
echo "───────────────────────────────────────────────────────"
check_content "docs/API_DOCS.md" "POST /api/v1/assess-risk" "Risk assessment endpoint"
check_content "docs/API_DOCS.md" "GET /api/v1/locations" "Locations endpoint"
check_content "docs/API_DOCS.md" "GET /api/v1/hazards" "Hazards endpoint"
check_content "docs/API_DOCS.md" "earthquake.*flood.*fire.*storm" "Hazard types"
check_content "docs/API_DOCS.md" "curl" "Example requests"
echo

echo "4. Checking User Manual..."
echo "───────────────────────────────────────────────────────"
check_content "docs/USER_MANUAL.md" "Quick Location Assessment" "User workflows"
check_content "docs/USER_MANUAL.md" "FAQ" "FAQ section"
check_content "docs/USER_MANUAL.md" "Troubleshooting" "Troubleshooting section"
check_content "docs/USER_MANUAL.md" "Features" "Features overview"
echo

echo "5. Checking Development Guide..."
echo "───────────────────────────────────────────────────────"
check_content "docs/DEVELOPMENT.md" "Development Setup" "Setup instructions"
check_content "docs/DEVELOPMENT.md" "Architecture Overview" "Architecture details"
check_content "docs/DEVELOPMENT.md" "Testing Strategy" "Testing information"
check_content "docs/DEVELOPMENT.md" "Contribution Guidelines" "Contribution guide"
check_content "docs/DEVELOPMENT.md" "pytest" "Testing tools"
echo

echo "6. Checking Deployment Guide..."
echo "───────────────────────────────────────────────────────"
check_content "DEPLOYMENT.md" "docker-compose" "Docker deployment"
check_content "DEPLOYMENT.md" "Production" "Production setup"
check_content "DEPLOYMENT.md" "Security" "Security section"
echo

echo "7. Checking Code Examples..."
echo "───────────────────────────────────────────────────────"
check_content "docs/API_DOCS.md" "curl.*POST" "curl examples"
check_content "docs/API_DOCS.md" "python" "Python examples"
check_content "docs/API_DOCS.md" "javascript" "JavaScript examples"
echo

echo "8. Checking Links..."
echo "───────────────────────────────────────────────────────"
check_content "README.md" "docs/API_DOCS.md" "API docs link"
check_content "README.md" "docs/USER_MANUAL.md" "User manual link"
check_content "README.md" "docs/DEVELOPMENT.md" "Development link"
check_content "README.md" "DEPLOYMENT.md" "Deployment link"
echo

echo "════════════════════════════════════════════════════════"
echo "               VALIDATION SUMMARY"
echo "════════════════════════════════════════════════════════"
echo -e "Passed: ${GREEN}${PASS}${NC}"
echo -e "Failed: ${RED}${FAIL}${NC}"
echo
if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ ALL DOCUMENTATION CHECKS PASSED!${NC}"
    exit 0
else
    echo -e "${RED}❌ SOME DOCUMENTATION CHECKS FAILED${NC}"
    exit 1
fi

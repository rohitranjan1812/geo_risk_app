#!/bin/bash
set -e

echo "=== Running E2E Tests ==="
echo ""

# Navigate to E2E test directory
cd "$(dirname "$0")"

# Check if setup was run
if [ ! -d "node_modules" ]; then
    echo "ERROR: Dependencies not installed. Run ./setup.sh first"
    exit 1
fi

# Check if services are running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "ERROR: Backend service not running. Start with: docker-compose up"
    exit 1
fi

if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "ERROR: Frontend service not running. Start with: docker-compose up"
    exit 1
fi

echo "✓ Services are running"
echo ""

# Parse arguments
BROWSER=""
MODE="headless"
SPEC=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --headed)
            MODE="headed"
            shift
            ;;
        --debug)
            MODE="debug"
            shift
            ;;
        --browser)
            BROWSER="--project=$2"
            shift 2
            ;;
        --spec)
            SPEC="$2"
            shift 2
            ;;
        --ui)
            MODE="ui"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run tests based on mode
if [ "$MODE" == "headed" ]; then
    echo "Running tests with visible browser..."
    npx playwright test $BROWSER $SPEC --headed
elif [ "$MODE" == "debug" ]; then
    echo "Running tests in debug mode..."
    npx playwright test $BROWSER $SPEC --debug
elif [ "$MODE" == "ui" ]; then
    echo "Starting Playwright UI..."
    npx playwright test $BROWSER --ui
else
    echo "Running tests in headless mode..."
    npx playwright test $BROWSER $SPEC
fi

# Show results
echo ""
echo "=== Test Results ==="
if [ -f "test-results/results.json" ]; then
    echo "JSON results: test-results/results.json"
fi

if [ -f "test-results/junit.xml" ]; then
    echo "JUnit XML: test-results/junit.xml"
fi

echo ""
echo "View HTML report with:"
echo "  npm run test:report"
echo ""

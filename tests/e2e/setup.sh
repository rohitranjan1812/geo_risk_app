#!/bin/bash
set -e

echo "=== E2E Test Setup Script ==="
echo ""

# Navigate to E2E test directory
cd "$(dirname "$0")"

echo "1. Installing Playwright dependencies..."
npm install

echo ""
echo "2. Installing Playwright browsers..."
npx playwright install

echo ""
echo "3. Creating necessary directories..."
mkdir -p screenshots videos test-results

echo ""
echo "4. Checking Docker services..."
if ! docker ps | grep -q "geo_risk"; then
    echo "   Starting Docker services..."
    cd ../..
    docker-compose up -d
    
    echo "   Waiting for services to be ready..."
    sleep 10
    
    # Wait for backend to be healthy
    max_attempts=30
    attempt=0
    until curl -s http://localhost:8000/health > /dev/null 2>&1; do
        attempt=$((attempt + 1))
        if [ $attempt -ge $max_attempts ]; then
            echo "   ERROR: Backend failed to start"
            exit 1
        fi
        echo "   Waiting for backend... (attempt $attempt/$max_attempts)"
        sleep 2
    done
    
    # Wait for frontend to be ready
    attempt=0
    until curl -s http://localhost:3000 > /dev/null 2>&1; do
        attempt=$((attempt + 1))
        if [ $attempt -ge $max_attempts ]; then
            echo "   ERROR: Frontend failed to start"
            exit 1
        fi
        echo "   Waiting for frontend... (attempt $attempt/$max_attempts)"
        sleep 2
    done
    
    echo "   ✓ Services are ready"
else
    echo "   ✓ Services are already running"
fi

echo ""
echo "5. Initializing test database..."
cd ../..
docker-compose exec -T backend python init_db.py 2>/dev/null || echo "   Database already initialized"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Run tests with:"
echo "  npm test                    # Run all tests"
echo "  npm run test:headed         # Run with browser visible"
echo "  npm run test:debug          # Debug mode"
echo "  npm run test:chromium       # Chrome only"
echo "  npm run test:firefox        # Firefox only"
echo "  npm run test:webkit         # Safari only"
echo "  npm run test:ui             # Interactive UI mode"
echo ""

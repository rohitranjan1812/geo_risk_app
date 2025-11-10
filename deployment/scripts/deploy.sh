#!/bin/bash
# Production deployment script

set -e

echo "🚀 Deploying GeoRisk Application..."

# Build and start all services
docker-compose build
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check health
echo "🏥 Checking service health..."
curl -f http://localhost:8000/api/v1/health || echo "Backend health check failed"
curl -f http://localhost/ || echo "Frontend health check failed"

echo ""
echo "✅ Deployment complete!"
echo "   - Frontend: http://localhost"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/api/v1/docs"

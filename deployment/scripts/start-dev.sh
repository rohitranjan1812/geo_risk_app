#!/bin/bash
# Development environment startup script

set -e

echo "🚀 Starting GeoRisk Development Environment..."

# Create .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend/.env from .env.example..."
    cp backend/.env.example backend/.env
fi

# Start services
echo "🐳 Starting Docker containers..."
docker-compose -f docker-compose.dev.yml up -d db

echo "⏳ Waiting for database to be ready..."
sleep 5

docker-compose -f docker-compose.dev.yml up -d backend

echo "✅ Backend started on http://localhost:8000"
echo "📚 API Docs available at http://localhost:8000/api/v1/docs"

# Frontend (development mode)
echo "🎨 To start frontend development server:"
echo "   cd frontend && npm install && npm run dev"

echo ""
echo "🎉 Development environment ready!"
echo "   - Backend: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/api/v1/docs"
echo "   - Database: postgresql://georisk:georisk_password@localhost:5432/georisk_db"

# GeoRisk - Geographic Risk Assessment Application

A comprehensive geo risk simulation application for assessing natural hazard risks at specific locations.

## Features

- 🗺️ **Interactive Map Interface** - Visualize risk zones with Leaflet/MapBox
- 📊 **Risk Assessment** - Calculate risk scores for earthquakes, floods, fires, and storms
- 📈 **Data Visualization** - Heat maps and charts for risk analysis
- 🔍 **Location Search** - Find and assess any geographic location
- 📁 **Data Export** - Export assessment results and visualizations
- 🔒 **Secure API** - RESTful API with authentication

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Relational database
- **Pydantic** - Data validation

### Frontend
- **React 18** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool
- **Leaflet** - Interactive maps
- **Recharts** - Data visualization

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Web server and reverse proxy

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 20+ (for local development)

### Development Setup

1. **Clone and navigate to project:**
```bash
cd geo_risk_app
```

2. **Start development environment:**
```bash
chmod +x deployment/scripts/start-dev.sh
./deployment/scripts/start-dev.sh
```

3. **Start frontend development server:**
```bash
cd frontend
npm install
npm run dev
```

4. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/v1/docs

### Production Deployment

```bash
chmod +x deployment/scripts/deploy.sh
./deployment/scripts/deploy.sh
```

## Project Structure

```
geo_risk_app/
├── backend/
│   ├── app/
│   │   ├── models/         # Database models
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   ├── tests/              # Backend tests
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API clients
│   │   └── types/          # TypeScript types
│   ├── package.json        # Node dependencies
│   └── Dockerfile
├── deployment/
│   ├── nginx/              # Nginx configs
│   └── scripts/            # Deployment scripts
└── docker-compose.yml      # Container orchestration
```

## API Endpoints

### Health Check
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/db` - Database health check

### Risk Assessment (Coming Soon)
- `POST /api/v1/risk/calculate` - Calculate risk for location
- `GET /api/v1/risk/location/{id}` - Get location risk details
- `GET /api/v1/risk/history` - Get risk assessment history

## Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run locally
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure:

```env
DATABASE_URL=postgresql+asyncpg://georisk:password@db:5432/georisk_db
SECRET_KEY=your-secret-key
MAPBOX_API_KEY=your-mapbox-key
```

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=app --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

## Contributing

1. Follow the project structure
2. Write tests for new features
3. Update documentation
4. Ensure all tests pass before committing

## License

MIT License - See LICENSE file for details

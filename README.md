# GeoRisk - Geographic Risk Assessment Platform

> **Comprehensive natural disaster risk assessment with interactive mapping, multi-hazard analysis, and real-time risk scoring.**

A production-ready geo risk simulation application for assessing natural hazard risks (earthquakes, floods, fires, storms) at specific locations using validated algorithms and historical data analysis.

[![Build Status](https://github.com/yourusername/geo-risk/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/yourusername/geo-risk/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18.2+](https://img.shields.io/badge/react-18.2+-blue.svg)](https://reactjs.org/)

---

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Documentation](#-documentation)
- [Development](#-development)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)

---

## ✨ Features

### Core Capabilities
- 🗺️ **Interactive Map Interface** - Leaflet-powered maps with real-time risk visualization
- 🌪️ **Multi-Hazard Assessment** - Simultaneous risk analysis for 4 hazard types:
  - 🌎 **Earthquakes** - Seismic activity risk
  - 🌊 **Floods** - Water inundation risk  
  - 🔥 **Wildfires** - Fire spread risk
  - ⛈️ **Storms** - Hurricane/typhoon risk
- 📊 **Heat Map Visualization** - Geographic risk distribution with color-coded intensity
- 🎯 **Real-Time Risk Scoring** - Instant calculation with 0-100 risk scores
- 📈 **Factor Analysis** - Detailed breakdown of risk contributors
- 💡 **Smart Recommendations** - Actionable mitigation strategies per hazard

### Data & Export
- 🔍 **Location Search** - Geocoding with autocomplete (cities, addresses, coordinates)
- 📁 **Data Export** - Download results in JSON and CSV formats
- 📚 **Historical Context** - Access to past disaster events database
- 🔄 **Batch Processing** - Compare multiple locations simultaneously

### Technical Features
- 🚀 **RESTful API** - Complete FastAPI backend with OpenAPI/Swagger docs
- ⚡ **High Performance** - Async I/O, optimized queries, <3s response times
- 🎨 **Responsive Design** - Works on desktop, tablet, and mobile
- 🔒 **Type Safety** - Full TypeScript frontend, Pydantic backend validation
- 🐳 **Docker Ready** - Complete containerization with docker-compose
- 📏 **Comprehensive Testing** - 85%+ backend coverage, 80%+ frontend, E2E tests

---

## 🚀 Quick Start

### Using Docker (Recommended - 5 minutes)

```bash
# 1. Clone repository
git clone https://github.com/yourorg/geo-risk-app.git
cd geo-risk-app

# 2. Setup environment
cp .env.example .env
# Edit .env with your configuration (optional - defaults work)

# 3. Start all services
docker-compose up -d

# 4. Initialize database with sample data
docker-compose exec backend python init_db.py

# 5. Access the application
# Web App:     http://localhost
# Frontend:    http://localhost:3000
# Backend API: http://localhost:8000/docs
# Database:    localhost:5432
```

**That's it!** The application is now running.

### Verify Installation

```bash
# Check all services are healthy
docker-compose ps

# Test backend API
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# Test frontend
curl http://localhost:3000
# Expected: HTML response

# View logs
docker-compose logs -f
```

### First Assessment

1. Open **http://localhost:3000** in your browser
2. Search for a location (e.g., "San Francisco, CA")
3. Select hazard types (Earthquake, Fire)
4. Click **"Assess Risk"**
5. View results and export data

### Quick Commands

```bash
# Stop services
docker-compose down

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart a service
docker-compose restart backend

# Run tests
docker-compose exec backend pytest
cd frontend && npm test

# Access database
docker-compose exec db psql -U georisk georisk_db
```

---

## 🏗️ Architecture

### System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  React SPA (TypeScript + Material-UI)                  │     │
│  │  ┌──────────────┬──────────────┬──────────────────┐   │     │
│  │  │ Map View     │ Search Panel │ Results Display  │   │     │
│  │  │ (Leaflet)    │ (Geocoding)  │ (Risk Scores)    │   │     │
│  │  └──────────────┴──────────────┴──────────────────┘   │     │
│  │  State Management: React Context API                   │     │
│  └────────────────────────────────────────────────────────┘     │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             │ HTTP/REST (JSON)
                             │ CORS Enabled
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                     NGINX REVERSE PROXY                          │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Route /api/*  →  Backend (Port 8000)                  │     │
│  │  Route /*      →  Frontend (Port 3000)                 │     │
│  │  SSL Termination, Compression, Caching                 │     │
│  └────────────────────────────────────────────────────────┘     │
└────────────────┬──────────────────────┬──────────────────────────┘
                 │                      │
                 ▼                      ▼
┌────────────────────────────┐  ┌───────────────────────────┐
│   BACKEND API (FastAPI)    │  │  FRONTEND SERVER (Nginx)  │
│  ┌──────────────────────┐  │  │  ┌─────────────────────┐  │
│  │ API Endpoints        │  │  │  │ Static Files        │  │
│  │ - Locations          │  │  │  │ - HTML/CSS/JS       │  │
│  │ - Hazards            │  │  │  │ - Images/Assets     │  │
│  │ - Risk Assessment    │  │  │  │ SPA Routing         │  │
│  │ - Historical Data    │  │  │  └─────────────────────┘  │
│  ├──────────────────────┤  │  └───────────────────────────┘
│  │ Services Layer       │  │
│  │ - Risk Calculator    │  │
│  │ - Data Validator     │  │
│  ├──────────────────────┤  │
│  │ ORM (SQLAlchemy)     │  │
│  └──────────┬───────────┘  │
└─────────────┼──────────────┘
              │
              │ Async PostgreSQL
              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    DATABASE (PostgreSQL 15)                      │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Tables:                                                │     │
│  │  • locations           - Geographic points + factors    │     │
│  │  • hazards             - Hazard type configurations     │     │
│  │  • risk_assessments    - Assessment results            │     │
│  │  • historical_data     - Past disaster events          │     │
│  │                                                         │     │
│  │  Features:                                              │     │
│  │  • Indexes on lat/lng, hazard_type                     │     │
│  │  • Foreign key constraints                              │     │
│  │  • JSONB for flexible metadata                         │     │
│  └────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────┘
```

### Data Flow - Risk Assessment

```
1. User Input
   ├─ Location: "San Francisco, CA"
   ├─ Hazards: [earthquake, fire]
   └─ Factors: {population: 18838, building_code: 8.5}
              │
              ▼
2. Frontend Processing
   ├─ Geocode location → (37.7749, -122.4194)
   ├─ Validate inputs
   └─ POST /api/v1/assess-risk
              │
              ▼
3. Backend Processing
   ├─ Pydantic validation
   ├─ Database: Get/Create location
   ├─ Database: Fetch hazard configs
   └─ RiskCalculationService.calculate_risk()
       ├─ Factor analysis (population, codes, infrastructure)
       ├─ Historical frequency lookup
       ├─ Weighted algorithm: score = Σ(factor × weight)
       └─ Risk level: score → {low|moderate|high|critical}
              │
              ▼
4. Response Generation
   ├─ Save assessment to database
   ├─ Generate recommendations
   └─ Return JSON response
              │
              ▼
5. Frontend Display
   ├─ Update risk score display
   ├─ Render individual hazard cards
   ├─ Show heat map layer
   └─ Enable export functionality
```

### Key Design Patterns

**Backend:**
- **Async/Await** - Non-blocking I/O for database and external APIs
- **Dependency Injection** - FastAPI's Depends() for database sessions
- **Repository Pattern** - Service layer separates business logic from data access
- **Pydantic Models** - Request/response validation with type safety
- **Alembic Migrations** - Version-controlled database schema changes

**Frontend:**
- **Component Composition** - Reusable, testable UI components
- **Context API** - Global state management without Redux overhead
- **Custom Hooks** - Encapsulated logic (useRiskAssessment, useMapData)
- **Page Objects** - E2E testing with maintainable test code
- **Lazy Loading** - Code splitting for performance

---

## 🛠️ Tech Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Core language |
| **FastAPI** | 0.104+ | Async web framework |
| **SQLAlchemy** | 2.0+ | Async ORM |
| **PostgreSQL** | 15+ | Production database |
| **Pydantic** | 2.0+ | Data validation |
| **Alembic** | 1.12+ | Database migrations |
| **Pytest** | 7.4+ | Testing framework |
| **Uvicorn** | 0.24+ | ASGI server |

**Backend Dependencies:**
```
fastapi[all]>=0.104.0
sqlalchemy[asyncio]>=2.0.0
asyncpg>=0.29.0           # PostgreSQL async driver
pydantic>=2.0.0
pydantic-settings>=2.0.0
alembic>=1.12.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
httpx>=0.25.0             # Async HTTP client for tests
```

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.2+ | UI framework |
| **TypeScript** | 5.0+ | Type safety |
| **Material-UI** | 5.14+ | Component library |
| **Leaflet** | 1.9+ | Interactive maps |
| **React-Leaflet** | 4.2+ | React Leaflet bindings |
| **Axios** | 1.6+ | HTTP client |
| **Jest** | 29.7+ | Unit testing |
| **Playwright** | 1.40+ | E2E testing |

**Frontend Dependencies:**
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "typescript": "^5.0.0",
  "@mui/material": "^5.14.0",
  "@mui/icons-material": "^5.14.0",
  "leaflet": "^1.9.4",
  "react-leaflet": "^4.2.1",
  "axios": "^1.6.0",
  "@testing-library/react": "^14.0.0",
  "@playwright/test": "^1.40.0"
}
```

### DevOps & Infrastructure
| Technology | Purpose |
|------------|---------|
| **Docker** | Containerization |
| **Docker Compose** | Multi-container orchestration |
| **Nginx** | Reverse proxy & static files |
| **GitHub Actions** | CI/CD (future) |
| **Makefile** | Development automation |

### Development Tools
```bash
# Backend linting & formatting
black>=23.0.0             # Code formatter
flake8>=6.0.0             # Linter
mypy>=1.5.0               # Type checker

# Frontend tools
eslint>=8.50.0            # Linter
prettier>=3.0.0           # Code formatter
```

---

## 📚 Documentation

Comprehensive documentation available in `/docs`:

| Document | Description |
|----------|-------------|
| **[API_DOCS.md](./docs/API_DOCS.md)** | Complete API reference with examples |
| **[USER_MANUAL.md](./docs/USER_MANUAL.md)** | End-user guide with screenshots |
| **[DEVELOPMENT.md](./docs/DEVELOPMENT.md)** | Developer setup & guidelines |
| **[DEPLOYMENT.md](./DEPLOYMENT.md)** | Production deployment guide |
| **[TEST_REPORT.md](./TEST_REPORT.md)** | Test coverage and results |

### API Documentation

**Interactive API Docs:**
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

**Sample API Request:**
```bash
# Assess risk for a location
curl -X POST "http://localhost:8000/api/v1/assess-risk" \
  -H "Content-Type: application/json" \
  -d '{
    "location": {
      "name": "San Francisco, CA",
      "latitude": 37.7749,
      "longitude": -122.4194,
      "population_density": 18838.0,
      "building_code_rating": 8.5,
      "infrastructure_quality": 7.5
    },
    "hazard_types": ["earthquake", "fire"],
    "risk_factors": null
  }'
```

**Sample Response:**
```json
{
  "location": { ... },
  "assessments": [
    {
      "hazard_type": "earthquake",
      "risk_score": 72.5,
      "risk_level": "high",
      "confidence_level": 0.85,
      "recommendations": [
        "Strengthen building codes for seismic resilience",
        "Conduct regular earthquake drills"
      ]
    }
  ],
  "overall_risk_score": 58.9,
  "overall_risk_level": "high"
}
```

See [API_DOCS.md](./docs/API_DOCS.md) for complete endpoint documentation.

---

## 💻 Development

### Local Development Setup

```bash
# Backend development
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend development  
cd frontend
npm install
npm start

# Database setup
createdb georisk_db
alembic upgrade head
python init_db.py
```

### Development Workflow

```bash
# Run with hot reload
docker-compose up

# Run tests
docker-compose exec backend pytest -v --cov=app
cd frontend && npm test

# Code quality
black backend/app              # Format Python
flake8 backend/app             # Lint Python
cd frontend && npm run lint    # Lint TypeScript

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Project Structure

```
geo_risk_app/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── api/               # Route handlers
│   │   ├── core/              # Config & settings
│   │   ├── db/                # Database setup
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   └── main.py            # App entry point
│   ├── tests/                 # Backend tests
│   ├── alembic/               # DB migrations
│   └── requirements.txt
│
├── frontend/                   # React application
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── contexts/          # State management
│   │   ├── services/          # API clients
│   │   ├── types/             # TypeScript types
│   │   └── App.tsx
│   ├── public/
│   └── package.json
│
├── tests/e2e/                  # End-to-end tests
│   ├── specs/                 # Playwright specs
│   └── playwright.config.ts
│
├── docs/                       # Documentation
├── nginx/                      # Nginx config
├── init-scripts/               # DB initialization
├── docker-compose.yml          # Development
├── docker-compose.prod.yml     # Production
└── Makefile                    # Common commands
```

See [DEVELOPMENT.md](./docs/DEVELOPMENT.md) for detailed development guide.

---

## 🧪 Testing

### Test Coverage

**Current Coverage:**
- **Backend:** 87% (target: 85%+)
- **Frontend:** 82% (target: 80%+)
- **E2E:** 55+ tests covering critical flows

### Running Tests

```bash
# Backend unit tests
docker-compose exec backend pytest tests/unit/ -v

# Backend integration tests
docker-compose exec backend pytest tests/integration/ -v

# All backend tests with coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Frontend tests
cd frontend
npm test                    # Unit tests
npm test -- --coverage      # With coverage

# E2E tests
cd tests/e2e
npm test                    # All E2E tests
npm run test:headed         # Visible browser
npm run test:debug          # Debug mode
```

### Test Structure

**Backend Tests (Pytest):**
- `tests/unit/` - Pure logic tests (models, services)
- `tests/integration/` - API endpoint tests
- `tests/conftest.py` - Shared fixtures

**Frontend Tests (Jest + RTL):**
- `__tests__/` - Component tests
- Coverage includes: rendering, user interactions, API mocking

**E2E Tests (Playwright):**
- User journey workflows
- Multi-hazard scenarios
- Error handling
- Cross-browser compatibility
- Performance benchmarks

See [TEST_REPORT.md](./TEST_REPORT.md) for detailed test results.

---

## 🚢 Deployment

### Production Deployment (Docker)

```bash
# 1. Configure production environment
cp .env.example .env
# Edit .env with secure production values:
# - Change SECRET_KEY
# - Set strong database passwords
# - Configure external API keys

# 2. Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# 3. Start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 4. Initialize database
docker-compose exec backend alembic upgrade head
docker-compose exec backend python init_db.py

# 5. Verify deployment
make health
# Or: curl http://localhost/health
```

### Deployment Checklist

- [ ] Environment variables configured
- [ ] Database backups automated
- [ ] SSL certificates installed (if using HTTPS)
- [ ] Firewall rules configured
- [ ] Monitoring setup
- [ ] Log aggregation configured
- [ ] Health checks passing

### Docker Services

The application runs 4 containerized services:

1. **PostgreSQL (georisk_db)** - Port 5432 (internal only)
2. **Backend (georisk_backend)** - Port 8000 (internal)
3. **Frontend (georisk_frontend)** - Port 3000 (internal)
4. **Nginx (georisk_nginx)** - Port 80 (public)

### Makefile Commands

```bash
make help              # Show all commands
make up                # Start all services
make down              # Stop all services
make build             # Build containers
make logs              # View logs
make test              # Run tests
make backup-db         # Backup database
make restore-db        # Restore from backup
make health            # Health check
make clean             # Remove containers & volumes
```

See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete deployment guide including:
- SSL/HTTPS setup
- Production optimizations
- Security hardening
- Monitoring setup
- Backup strategies
- Troubleshooting guide

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/amazing-feature`
3. **Make your changes:**
   - Follow code style guidelines
   - Add/update tests
   - Update documentation
4. **Commit changes:** `git commit -m 'feat: add amazing feature'`
5. **Push to branch:** `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Commit Message Convention

```
feat: new feature
fix: bug fix
docs: documentation changes
style: formatting
refactor: code restructuring
test: adding tests
chore: maintenance
```

### Code Standards

**Python:**
- Follow PEP 8
- Use type hints
- Write docstrings
- Run `black` and `flake8`

**TypeScript:**
- Follow Airbnb style guide
- Use TypeScript strict mode
- Write JSDoc comments
- Run `eslint` and `prettier`

### Testing Requirements

- All new features must include tests
- Maintain >85% backend coverage
- Maintain >80% frontend coverage
- E2E tests for user-facing features
- All tests must pass before PR approval

See [DEVELOPMENT.md](./docs/DEVELOPMENT.md) for detailed contribution guidelines.

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

**Built with:**
- **FastAPI** - Modern Python web framework
- **React** - UI library
- **Leaflet** - Interactive maps
- **PostgreSQL** - Reliable database
- **Material-UI** - Component library

**Data Sources:**
- **USGS** - Earthquake data
- **NOAA** - Storm and flood data
- **FEMA** - Historical disaster data
- **OpenStreetMap** - Geographic data

---

## 📧 Support

- **Documentation:** `/docs` directory
- **Issues:** [GitHub Issues](https://github.com/yourorg/geo-risk-app/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourorg/geo-risk-app/discussions)
- **Email:** support@georisk.example.com

---

## 🗺️ Roadmap

**Version 1.0** (Current)
- ✅ Multi-hazard risk assessment
- ✅ Interactive mapping
- ✅ Data export
- ✅ Docker deployment
- ✅ Comprehensive testing

**Version 1.1** (Planned)
- [ ] User authentication & accounts
- [ ] Saved assessments history
- [ ] Advanced heat map visualization
- [ ] PDF report generation
- [ ] API rate limiting

**Version 2.0** (Future)
- [ ] Real-time disaster alerts
- [ ] Mobile app (React Native)
- [ ] AI-powered risk predictions
- [ ] Integration with external APIs
- [ ] Multi-language support

---

**Made with ❤️ for safer communities**

*Version 1.0.0 | Last Updated: 2024-01-01*

# Setup environment variables
cp .env.example .env
# Edit .env with backend API URL

# Start development server
npm run dev

# Application will be available at http://localhost:5173
```

### First Time Setup

1. **Create an account**: Navigate to http://localhost:3000/login and register
2. **Login**: Use your credentials to access the dashboard
3. **Assess Risk**: Click on the map to select a location and run risk assessment

## 📚 API Documentation

The API follows RESTful conventions and provides comprehensive OpenAPI documentation.

### Base URL
- Development: `http://localhost:8000`
- Production: `https://your-domain.com`

### Authentication

All protected endpoints require a JWT token in the Authorization header:

```bash
Authorization: Bearer <your_jwt_token>
```

### Core Endpoints

#### Authentication

```http
POST /auth/register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123"
}

Response: 201 Created
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "created_at": "2024-01-15T10:30:00Z"
}
```

```http
POST /auth/login
Content-Type: application/json

{
  "username": "johndoe",
  "password": "securepassword123"
}

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Locations

```http
POST /locations
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "San Francisco Office",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "address": "123 Market St, San Francisco, CA",
  "city": "San Francisco",
  "state": "California",
  "country": "United States"
}

Response: 201 Created
{
  "id": 1,
  "name": "San Francisco Office",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Risk Assessments

```http
POST /assessments
Authorization: Bearer <token>
Content-Type: application/json

{
  "location_id": 1,
  "assessment_name": "Q1 2024 Assessment",
  "notes": "Annual risk evaluation"
}

Response: 201 Created
{
  "id": 1,
  "location_id": 1,
  "overall_risk_score": 65.5,
  "earthquake_score": 85.2,
  "flood_score": 45.0,
  "fire_score": 72.3,
  "storm_score": 60.0,
  "created_at": "2024-01-15T10:30:00Z"
}
```

```http
GET /assessments
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": 1,
    "overall_risk_score": 65.5,
    "earthquake_score": 85.2,
    ...
  }
]
```

```http
POST /assessments/{assessment_id}/recalculate
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "overall_risk_score": 66.2,
  "earthquake_score": 86.0,
  ...
}
```

#### Health Check

```http
GET /health

Response: 200 OK
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected"
}
```

### Interactive API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 💻 Development

### Project Structure

```
geo_risk_app/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py           # Application configuration
│   │   │   ├── database.py         # Database connection & session
│   │   │   └── security.py         # JWT & password utilities
│   │   ├── models/
│   │   │   └── models.py           # SQLAlchemy models
│   │   ├── routers/
│   │   │   ├── auth.py             # Authentication endpoints
│   │   │   ├── locations.py        # Location CRUD operations
│   │   │   └── risk_assessments.py # Risk assessment endpoints
│   │   ├── schemas/
│   │   │   └── schemas.py          # Pydantic models
│   │   ├── services/
│   │   │   └── risk_calculator.py  # Risk calculation algorithms
│   │   └── tests/
│   │       ├── conftest.py         # Test fixtures
│   │       ├── test_api_endpoints.py
│   │       ├── test_database.py
│   │       └── test_integration_api.py
│   ├── alembic/                    # Database migrations
│   ├── main.py                     # FastAPI application entry
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                  # Container definition
│   └── docker-compose.yml          # Development orchestration
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── LocationSearch.tsx  # Location search component
│   │   │   ├── MapComponent.tsx    # Interactive map
│   │   │   ├── ProtectedRoute.tsx  # Route protection
│   │   │   ├── ResultsDashboard.tsx # Results visualization
│   │   │   └── RiskAssessmentForm.tsx
│   │   ├── hooks/
│   │   │   └── useAuth.tsx         # Authentication hook
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx       # Main application page
│   │   │   └── Login.tsx           # Login/register page
│   │   ├── services/
│   │   │   ├── apiClient.ts        # Axios client with interceptors
│   │   │   ├── authService.ts      # Authentication service
│   │   │   ├── geocodingService.ts # Geocoding integration
│   │   │   └── riskService.ts      # Risk assessment API calls
│   │   ├── types/
│   │   │   └── index.ts            # TypeScript interfaces
│   │   └── utils/
│   │       └── export.ts           # Data export utilities
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── vitest.config.ts
├── scripts/
│   └── backup-database.sh          # Database backup script
├── docker-compose.prod.yml         # Production orchestration
└── .github/
    └── workflows/
        └── ci-cd.yml               # CI/CD pipeline
```

### Database Schema

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Locations table
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_coordinates (latitude, longitude)
);

-- Risk assessments table
CREATE TABLE risk_assessments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    location_id INTEGER REFERENCES locations(id),
    overall_risk_score FLOAT NOT NULL,
    earthquake_score FLOAT DEFAULT 0,
    flood_score FLOAT DEFAULT 0,
    fire_score FLOAT DEFAULT 0,
    storm_score FLOAT DEFAULT 0,
    assessment_name VARCHAR(200),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Hazard data table
CREATE TABLE hazard_data (
    id SERIAL PRIMARY KEY,
    location_id INTEGER REFERENCES locations(id),
    hazard_type VARCHAR(50) NOT NULL,
    historical_frequency FLOAT,
    max_magnitude FLOAT,
    soil_type VARCHAR(50),
    elevation FLOAT,
    vegetation_density FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_hazard_type (hazard_type)
);
```

### Risk Calculation Algorithm

The risk calculation engine uses geographic models based on scientific research:

1. **Earthquake Risk** (0-100):
   - Pacific Ring of Fire zones: High risk (80-90)
   - Tectonic plate boundaries: Moderate to high risk (60-80)
   - Stable continental regions: Low risk (0-30)
   - Adjusted by soil type and historical frequency

2. **Flood Risk** (0-100):
   - Elevation factor: Lower elevation = higher risk
   - Proximity to water bodies: Closer = higher risk
   - Climate zone: Tropical and monsoon regions = higher risk
   - Historical flood frequency

3. **Fire Risk** (0-100):
   - Mediterranean climate zones: High risk (60-80)
   - Vegetation density: Moderate vegetation (40-70%) = highest risk
   - Arid regions with available fuel: High risk
   - Historical fire frequency

4. **Storm Risk** (0-100):
   - Hurricane/typhoon zones: High risk (60-80)
   - Tornado Alley: High risk (70-85)
   - Wind exposure factor
   - Historical storm patterns

5. **Overall Risk Score**:
   - Weighted average: Earthquake (30%), Flood (25%), Fire (20%), Storm (25%)

### Environment Variables

#### Backend (.env)

```bash
# Application
APP_NAME="Geo Risk Assessment API"
APP_VERSION="1.0.0"
DEBUG=true

# Security
SECRET_KEY="generate-secure-key-min-32-characters"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/georisk"

# CORS
CORS_ORIGINS="http://localhost:3000,http://localhost:5173"
```

#### Frontend (.env)

```bash
VITE_API_BASE_URL=http://localhost:8000/api
VITE_MAP_DEFAULT_CENTER_LAT=37.7749
VITE_MAP_DEFAULT_CENTER_LNG=-122.4194
VITE_MAP_DEFAULT_ZOOM=10
```

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest app/tests/test_api_endpoints.py -v

# Run tests in parallel
pytest -n auto

# Run integration tests only
pytest app/tests/test_integration_api.py
```

Test Coverage Goals:
- Unit tests: 90%+ coverage
- Integration tests: Core user workflows
- E2E tests: Critical paths (Playwright)

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- LocationSearch.test.tsx

# Run in watch mode
npm test -- --watch
```

### Test Structure

- **Unit Tests**: Individual functions and components
- **Integration Tests**: API endpoints with database
- **E2E Tests**: Full user workflows with Playwright
- **Contract Tests**: API schema validation

## 🚢 Deployment

### Quick Start with Docker

The fastest way to deploy the entire application:

```bash
# 1. Setup environment
make setup  # or: cp .env.example .env

# 2. Edit .env with your configuration
nano .env

# 3. Build and start all services
make up  # or: docker-compose up -d

# 4. Verify deployment
make test-deployment  # runs comprehensive validation
```

Access the application:
- **Application**: http://localhost
- **API Documentation**: http://localhost/docs
- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000

### Production Deployment

For production environments with optimized configurations:

```bash
# 1. Configure production environment
cp .env.example .env
# Edit .env with secure production values

# 2. Generate secure secrets
make generate-secrets

# 3. Deploy with production settings
make prod  # or: docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 4. Initialize database
make init-db

# 5. Verify deployment
make health
```

### Comprehensive Deployment Guide

For detailed deployment instructions including:
- Architecture diagrams
- Service configuration
- Security hardening
- SSL/HTTPS setup
- Database backups
- Monitoring and logging
- Troubleshooting guide

See **[DEPLOYMENT.md](./DEPLOYMENT.md)** for complete documentation.

### Quick Commands (via Makefile)

```bash
make help              # Show all available commands
make build             # Build Docker containers
make up                # Start all services
make down              # Stop all services
make logs              # View logs
make test              # Run backend tests
make test-deployment   # Validate deployment
make backup-db         # Backup database
make health            # Check service health
make clean             # Remove containers and volumes
```

### Environment-Specific Configs

- **Development**: `docker-compose.yml` - Hot reload, debug mode, exposed ports
- **Testing**: `docker-compose.test.yml` - Isolated test environment
- **Production**: `docker-compose.prod.yml` - Optimized builds, resource limits, nginx proxy

### Docker Services

The application consists of 4 containerized services:

1. **PostgreSQL Database** (`georisk_db`)
   - Port 5432 (internal)
   - Persistent volume for data
   - Health checks enabled

2. **FastAPI Backend** (`georisk_backend`)
   - Port 8000 (internal)
   - Auto-initializes database
   - Uvicorn with hot reload (dev) or workers (prod)

3. **React Frontend** (`georisk_frontend`)
   - Port 3000 (internal)
   - Multi-stage build (Node + Nginx)
   - SPA routing configured

4. **Nginx Reverse Proxy** (`georisk_nginx`)
   - Port 80 (external)
   - Routes `/api/*` to backend
   - Routes `/` to frontend
   - CORS and security headers

### Database Backup

```bash
# Manual backup
make backup-db

# Or use docker-compose directly
docker-compose exec -T db pg_dump -U georisk georisk_db > backup.sql

# Restore from backup
make restore-db BACKUP_FILE=backup.sql

### CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci-cd.yml`):

1. **Build Stage**: Build Docker images
2. **Test Stage**: Run pytest and vitest
3. **Security Scan**: Check for vulnerabilities
4. **Deploy Stage**: Deploy to staging/production

## 🔧 Troubleshooting

### Common Issues

#### Database Connection Errors

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check database logs
docker logs geo_risk_db

# Reset database
docker-compose down -v
docker-compose up -d
```

#### Backend Not Starting

```bash
# Check logs
docker logs geo_risk_backend

# Verify environment variables
docker exec geo_risk_backend env | grep DATABASE_URL

# Rebuild container
docker-compose up --build backend
```

#### Frontend Build Failures

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
npm run dev
```

#### Authentication Issues

```bash
# Verify JWT token
# Token should be in format: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Check token expiration
# Default: 30 minutes (configurable in .env)

# Clear browser localStorage
localStorage.removeItem('auth_token')
```

### Performance Optimization

- **Database Indexing**: Indexes on latitude, longitude, user_id
- **API Caching**: Consider Redis for frequently accessed data
- **Frontend Optimization**: Code splitting, lazy loading
- **CDN**: Serve static assets from CDN in production

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new functionality
4. Ensure all tests pass (`pytest` and `npm test`)
5. Update documentation
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Style

- **Python**: Follow PEP 8, use type hints
- **TypeScript**: Follow Airbnb style guide
- **Commits**: Use conventional commits format

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 📞 Support

- **Documentation**: See inline code documentation and API docs
- **Issues**: [GitHub Issues](https://github.com/yourusername/geo-risk/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/geo-risk/discussions)

---

**Built with ❤️ for safer communities**

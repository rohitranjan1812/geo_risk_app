# Geo Risk Development Guide

## Table of Contents

1. [Development Setup](#development-setup)
2. [Architecture Overview](#architecture-overview)
3. [Project Structure](#project-structure)
4. [Development Workflow](#development-workflow)
5. [Testing Strategy](#testing-strategy)
6. [Contribution Guidelines](#contribution-guidelines)
7. [Code Standards](#code-standards)
8. [API Development](#api-development)
9. [Frontend Development](#frontend-development)
10. [Database Management](#database-management)

---

## Development Setup

### Prerequisites

**Required Software:**
```bash
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (or Docker)
- Git
- Docker & Docker Compose (optional but recommended)
```

**Verify Installation:**
```bash
python --version    # Should be 3.11+
node --version      # Should be v18+
npm --version       # Should be 9+
docker --version    # Should be 20+
git --version       # Should be 2.30+
```

### Quick Start (Docker - Recommended)

```bash
# 1. Clone repository
git clone https://github.com/yourorg/geo-risk-app.git
cd geo-risk-app

# 2. Setup environment
cp .env.example .env
# Edit .env with your local settings

# 3. Start all services
docker-compose up -d

# 4. Initialize database
docker-compose exec backend python init_db.py

# 5. Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
# Nginx Proxy: http://localhost
```

Application should be running in **under 5 minutes**!

### Manual Setup (Local Development)

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup PostgreSQL database
createdb georisk_db

# Configure environment
cp .env.example .env
# Edit DATABASE_URL in .env:
# DATABASE_URL=postgresql+asyncpg://username:password@localhost/georisk_db

# Run migrations
alembic upgrade head

# Initialize with sample data
python init_db.py

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend API now available at: http://localhost:8000

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit REACT_APP_API_URL in .env:
# REACT_APP_API_URL=http://localhost:8000/api/v1

# Start development server
npm start
```

Frontend now available at: http://localhost:3000

### Development Tools

**Recommended IDE Extensions:**

**VS Code:**
- Python (Microsoft)
- Pylance
- ESLint
- Prettier
- Docker
- GitLens
- REST Client

**IntelliJ/PyCharm:**
- Python
- JavaScript and TypeScript
- Docker
- Database Tools

**Recommended Terminal Tools:**
```bash
# Backend tools
pip install black flake8 mypy pytest pytest-cov

# Frontend tools
npm install -g typescript eslint prettier
```

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  React SPA (TypeScript)                                  │   │
│  │  - Leaflet Map                                           │   │
│  │  - Material-UI Components                                │   │
│  │  - React Context API (State)                             │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
                             │ JSON
┌────────────────────────────▼────────────────────────────────────┐
│                      NGINX REVERSE PROXY                        │
│  - Route /api/* → Backend                                       │
│  - Route /* → Frontend                                          │
│  - CORS Headers                                                 │
│  - Static Asset Caching                                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
           ┌─────────────────┴──────────────────┐
           │                                    │
┌──────────▼──────────┐            ┌───────────▼──────────┐
│   BACKEND API       │            │   FRONTEND SPA       │
│   (FastAPI/Python)  │            │   (React/Nginx)      │
│                     │            │                      │
│ - REST Endpoints    │            │ - Static Files       │
│ - Business Logic    │            │ - SPA Routing        │
│ - Risk Algorithms   │            │ - Asset Serving      │
│ - Data Validation   │            │                      │
└──────────┬──────────┘            └──────────────────────┘
           │
           │ SQLAlchemy ORM
           │ Async I/O
┌──────────▼──────────┐
│   DATABASE          │
│   (PostgreSQL)      │
│                     │
│ - Locations         │
│ - Hazards           │
│ - Assessments       │
│ - Historical Data   │
└─────────────────────┘
```

### Component Interaction Flow

**Risk Assessment Flow:**
```
User Input → React Form → API Request → FastAPI Router
    ↓
FastAPI Endpoint → Pydantic Validation → Service Layer
    ↓
RiskCalculationService → Database Queries → Risk Algorithm
    ↓
Algorithm Result → Database Save → Pydantic Response
    ↓
JSON Response → React State Update → UI Render
```

### Technology Stack

**Backend:**
- **Framework:** FastAPI 0.104+
- **Language:** Python 3.11+
- **ORM:** SQLAlchemy 2.0 (async)
- **Validation:** Pydantic 2.0
- **Database:** PostgreSQL 15
- **Migrations:** Alembic
- **Testing:** Pytest, pytest-asyncio
- **ASGI Server:** Uvicorn

**Frontend:**
- **Framework:** React 18.2+
- **Language:** TypeScript 5.0+
- **UI Library:** Material-UI (MUI) 5.14+
- **Mapping:** Leaflet 1.9+, React-Leaflet
- **State Management:** React Context API
- **HTTP Client:** Axios
- **Testing:** Jest, React Testing Library, Playwright
- **Build Tool:** Create React App / Webpack

**DevOps:**
- **Containerization:** Docker, Docker Compose
- **Reverse Proxy:** Nginx
- **CI/CD:** GitHub Actions (future)
- **Monitoring:** (future)

---

## Project Structure

### Backend Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry
│   │
│   ├── api/                    # API route handlers
│   │   ├── __init__.py
│   │   ├── locations.py        # Location CRUD endpoints
│   │   ├── hazards.py          # Hazard management endpoints
│   │   ├── risk.py             # Risk assessment endpoints
│   │   └── historical.py       # Historical data endpoints
│   │
│   ├── core/                   # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py           # App settings (Pydantic BaseSettings)
│   │   └── security.py         # Security utilities (future)
│   │
│   ├── db/                     # Database configuration
│   │   ├── __init__.py
│   │   ├── session.py          # Database session management
│   │   └── base.py             # SQLAlchemy base classes
│   │
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── location.py         # Location model
│   │   ├── hazard.py           # Hazard model
│   │   ├── risk_assessment.py  # Risk assessment model
│   │   └── historical_data.py  # Historical event model
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py         # All request/response schemas
│   │   └── ...                 # (Currently in single file)
│   │
│   └── services/               # Business logic layer
│       ├── __init__.py
│       └── risk_service.py     # Risk calculation algorithms
│
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_schemas.py
│   │
│   ├── integration/            # Integration tests
│   │   ├── test_api_locations.py
│   │   ├── test_api_risk.py
│   │   └── test_database.py
│   │
│   ├── conftest.py             # Pytest fixtures
│   └── __init__.py
│
├── alembic/                    # Database migrations
│   ├── versions/               # Migration scripts
│   ├── env.py
│   └── script.py.mako
│
├── requirements.txt            # Python dependencies
├── alembic.ini                # Alembic config
├── Dockerfile                 # Container definition
├── init_db.py                 # Database initialization script
└── run.py                     # Development server runner
```

### Frontend Structure

```
frontend/
├── public/
│   └── index.html              # HTML template
│
├── src/
│   ├── components/             # React components
│   │   ├── Map/
│   │   │   ├── MapComponent.tsx       # Main map container
│   │   │   └── HeatmapLayer.tsx       # Heat map overlay
│   │   │
│   │   ├── LocationSearch/
│   │   │   └── LocationSearch.tsx     # Search autocomplete
│   │   │
│   │   ├── RiskForm/
│   │   │   ├── RiskForm.tsx           # Risk factor inputs
│   │   │   └── RiskDisplay.tsx        # Results display
│   │   │
│   │   ├── DataExport/
│   │   │   └── DataExport.tsx         # Export functionality
│   │   │
│   │   └── Charts/
│   │       └── RiskCharts.tsx         # Visualization charts
│   │
│   ├── contexts/               # React Context providers
│   │   └── RiskContext.tsx     # Global state management
│   │
│   ├── services/               # API client services
│   │   └── api.ts              # Axios HTTP client
│   │
│   ├── types/                  # TypeScript type definitions
│   │   ├── index.ts            # Core types
│   │   └── leaflet-heat.d.ts   # Leaflet types
│   │
│   ├── utils/                  # Utility functions
│   │   └── helpers.ts          # Helper functions
│   │
│   ├── __tests__/              # Test files
│   │   ├── mocks/
│   │   │   ├── handlers.ts     # MSW mock handlers
│   │   │   └── server.ts       # MSW server setup
│   │   ├── setup.ts            # Test setup
│   │   └── ...                 # Component tests
│   │
│   ├── App.tsx                 # Root component
│   ├── index.tsx               # Entry point
│   ├── index.css               # Global styles
│   └── setupTests.ts           # Jest setup
│
├── package.json                # NPM dependencies
├── tsconfig.json               # TypeScript config
└── Dockerfile                  # Container definition
```

### E2E Tests Structure

```
tests/e2e/
├── specs/                      # Test specifications
│   ├── 01-user-journey.spec.ts
│   ├── 02-multi-hazard.spec.ts
│   ├── 03-error-handling.spec.ts
│   ├── 04-cross-browser.spec.ts
│   └── 05-performance.spec.ts
│
├── utils/                      # Test utilities
│   ├── api-helpers.ts          # API interaction helpers
│   └── page-objects.ts         # Page Object Model
│
├── fixtures/                   # Test data
│   ├── locations.json
│   └── test-scenarios.json
│
├── playwright.config.ts        # Playwright configuration
├── package.json
└── tsconfig.json
```

---

## Development Workflow

### Git Workflow

**Branch Strategy:**
```
main          - Production-ready code
develop       - Development integration branch
feature/*     - New features
bugfix/*      - Bug fixes
hotfix/*      - Critical production fixes
release/*     - Release preparation
```

**Creating a Feature:**
```bash
# 1. Start from develop
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/add-tsunami-hazard

# 3. Make changes, commit frequently
git add .
git commit -m "feat: add tsunami hazard type"

# 4. Push to remote
git push origin feature/add-tsunami-hazard

# 5. Create Pull Request on GitHub
# Request review from team
```

**Commit Message Convention:**
```
feat: new feature
fix: bug fix
docs: documentation changes
style: formatting, missing semicolons, etc.
refactor: code restructuring
test: adding tests
chore: maintenance tasks

Examples:
feat: add tsunami hazard assessment
fix: correct earthquake risk calculation
docs: update API documentation
test: add unit tests for risk service
```

### Local Development Cycle

**Daily Workflow:**
```bash
# 1. Start services
docker-compose up -d

# 2. Check backend logs
docker-compose logs -f backend

# 3. Check frontend logs
docker-compose logs -f frontend

# 4. Make code changes
# - Edit files in your IDE
# - Changes auto-reload (hot module replacement)

# 5. Run tests
docker-compose exec backend pytest
cd frontend && npm test

# 6. Commit changes
git add .
git commit -m "feat: your change description"

# 7. Stop services (end of day)
docker-compose down
```

### Making Changes

**Backend Changes:**
```bash
# 1. Edit Python files
vim backend/app/api/risk.py

# 2. Auto-reload triggers (no restart needed)

# 3. Test endpoint
curl http://localhost:8000/api/v1/assess-risk

# 4. Run unit tests
docker-compose exec backend pytest tests/unit/test_risk_service.py -v

# 5. Run integration tests
docker-compose exec backend pytest tests/integration/ -v
```

**Frontend Changes:**
```bash
# 1. Edit TypeScript/React files
vim frontend/src/components/RiskForm/RiskForm.tsx

# 2. Auto-reload happens (browser refreshes)

# 3. Test in browser
# Open http://localhost:3000

# 4. Run component tests
cd frontend
npm test -- RiskForm

# 5. Check TypeScript types
npm run type-check
```

**Database Changes:**
```bash
# 1. Create migration
docker-compose exec backend alembic revision --autogenerate -m "add_tsunami_hazard"

# 2. Review generated migration
vim backend/alembic/versions/xxx_add_tsunami_hazard.py

# 3. Apply migration
docker-compose exec backend alembic upgrade head

# 4. Test migration
docker-compose exec backend python -c "from app.db import engine; ..."

# 5. Rollback if needed
docker-compose exec backend alembic downgrade -1
```

---

## Testing Strategy

### Testing Pyramid

```
        ┌───────────────┐
        │   E2E Tests   │  ← Playwright (5-10 tests)
        │  ~5% of tests │
        └───────────────┘
       ┌─────────────────┐
       │ Integration Tests│  ← API + DB (20-30 tests)
       │   ~25% of tests  │
       └─────────────────┘
      ┌───────────────────┐
      │    Unit Tests      │  ← Pure logic (50+ tests)
      │   ~70% of tests    │
      └───────────────────┘
```

### Backend Testing

**Unit Tests:**
```python
# tests/unit/test_risk_service.py
import pytest
from app.services import RiskCalculationService

@pytest.mark.asyncio
async def test_calculate_earthquake_risk():
    """Test earthquake risk calculation."""
    service = RiskCalculationService(mock_db)
    
    location = create_mock_location(
        latitude=37.7749,
        population_density=10000,
        building_code_rating=8.0
    )
    hazard = create_mock_hazard(hazard_type="earthquake")
    
    score, level, confidence, _, _ = await service.calculate_risk(
        location, hazard, None
    )
    
    assert 0 <= score <= 100
    assert level in ["low", "moderate", "high", "critical"]
    assert 0 <= confidence <= 1
```

**Integration Tests:**
```python
# tests/integration/test_api_risk.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_assess_risk_endpoint(client: AsyncClient, db_session):
    """Test risk assessment API endpoint."""
    # Setup
    location = await create_test_location(db_session)
    
    # Request
    response = await client.post("/api/v1/assess-risk", json={
        "location_id": location.id,
        "hazard_types": ["earthquake", "fire"]
    })
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["overall_risk_score"] >= 0
    assert len(data["assessments"]) == 2
```

**Run Backend Tests:**
```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific module
pytest tests/unit/test_risk_service.py -v

# Watch mode (continuous)
pytest-watch

# Parallel execution
pytest -n auto
```

### Frontend Testing

**Component Tests:**
```typescript
// src/components/RiskForm/__tests__/RiskForm.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { RiskForm } from '../RiskForm';

describe('RiskForm', () => {
  it('submits risk assessment request', async () => {
    const onSubmit = jest.fn();
    render(<RiskForm onSubmit={onSubmit} />);
    
    // Fill form
    fireEvent.change(screen.getByLabelText('Population Density'), {
      target: { value: '10000' }
    });
    
    // Check hazards
    fireEvent.click(screen.getByLabelText('Earthquake'));
    fireEvent.click(screen.getByLabelText('Flood'));
    
    // Submit
    fireEvent.click(screen.getByText('Assess Risk'));
    
    // Assert
    expect(onSubmit).toHaveBeenCalledWith({
      population_density: 10000,
      hazard_types: ['earthquake', 'flood']
    });
  });
});
```

**Run Frontend Tests:**
```bash
# All tests
npm test

# With coverage
npm test -- --coverage

# Watch mode
npm test -- --watch

# Specific file
npm test -- RiskForm

# Update snapshots
npm test -- -u
```

### E2E Testing

**User Journey Test:**
```typescript
// tests/e2e/specs/01-user-journey.spec.ts
import { test, expect } from '@playwright/test';

test('complete risk assessment workflow', async ({ page }) => {
  // Navigate to app
  await page.goto('http://localhost:3000');
  
  // Search location
  await page.fill('[data-testid="location-search"]', 'San Francisco');
  await page.click('text=San Francisco, CA');
  
  // Select hazards
  await page.check('[data-testid="hazard-earthquake"]');
  await page.check('[data-testid="hazard-fire"]');
  
  // Assess risk
  await page.click('text=Assess Risk');
  
  // Verify results
  await expect(page.locator('[data-testid="risk-score"]')).toBeVisible();
  await expect(page.locator('[data-testid="risk-level"]')).toContainText(/low|moderate|high|critical/);
});
```

**Run E2E Tests:**
```bash
cd tests/e2e

# All tests
npm test

# Headed mode (visible browser)
npm run test:headed

# Debug mode
npm run test:debug

# Specific browser
npm run test:chromium
npm run test:firefox

# Generate report
npm run test:report
```

### Test Coverage Goals

**Backend:**
- Overall: >85%
- Critical paths: 100% (risk calculation, data validation)
- API endpoints: >90%
- Models: >80%

**Frontend:**
- Overall: >80%
- Components: >85%
- Utils: >90%
- Services: >85%

**E2E:**
- Critical user flows: 100%
- Error scenarios: >80%
- Cross-browser: Chrome, Firefox, Safari

---

## Contribution Guidelines

### Before Contributing

1. **Read existing documentation**
2. **Check open issues** - avoid duplicates
3. **Discuss major changes** - create issue first
4. **Follow code standards** - see below

### Pull Request Process

1. **Create feature branch** from `develop`
2. **Make atomic commits** with clear messages
3. **Write/update tests** for changes
4. **Update documentation** if needed
5. **Ensure tests pass** locally
6. **Push and create PR** with description
7. **Request review** from maintainers
8. **Address feedback** promptly
9. **Squash commits** before merge

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added to complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added for changes
- [ ] All tests passing

## Screenshots (if applicable)
[Add screenshots]

## Related Issues
Fixes #123
```

### Code Review Checklist

**Reviewers should verify:**
- ✅ Code follows style guide
- ✅ Tests exist and pass
- ✅ Documentation updated
- ✅ No security vulnerabilities
- ✅ Performance considerations
- ✅ Error handling present
- ✅ Naming is clear
- ✅ No unnecessary complexity

---

## Code Standards

### Python Style Guide

**Follow PEP 8 with these specifics:**

```python
# Type hints on all functions
def calculate_risk(
    location: Location,
    hazard: Hazard,
    custom_factors: Optional[Dict[str, float]] = None
) -> Tuple[float, RiskLevel, float]:
    """Calculate risk score for location and hazard.
    
    Args:
        location: Geographic location with risk factors
        hazard: Hazard type configuration
        custom_factors: Optional override factors
        
    Returns:
        Tuple of (risk_score, risk_level, confidence)
        
    Raises:
        ValueError: If custom_factors contain invalid keys
    """
    pass

# Docstrings for all public methods
# Use Google-style docstrings

# Import organization
# 1. Standard library
import os
from typing import List, Optional

# 2. Third-party
from fastapi import APIRouter
from sqlalchemy import select

# 3. Local
from app.models import Location
from app.schemas import LocationResponse

# Constants in UPPER_CASE
MAX_RISK_SCORE = 100.0
DEFAULT_CONFIDENCE = 0.75

# Classes in PascalCase
class RiskCalculationService:
    pass

# Functions in snake_case
def calculate_weighted_average(values: List[float]) -> float:
    pass
```

**Linting:**
```bash
# Format code
black backend/app

# Check style
flake8 backend/app

# Type checking
mypy backend/app
```

### TypeScript Style Guide

**Follow Airbnb style with these specifics:**

```typescript
// Type everything
interface RiskAssessment {
  locationId: number;
  hazardTypes: HazardType[];
  riskFactors?: RiskFactors;
}

// Use functional components with hooks
const RiskForm: React.FC<RiskFormProps> = ({ onSubmit }) => {
  const [loading, setLoading] = useState<boolean>(false);
  
  // Handler functions
  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    try {
      await onSubmit(formData);
    } catch (error) {
      console.error('Submission failed:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return <form onSubmit={handleSubmit}>...</form>;
};

// Constants in UPPER_SNAKE_CASE
const MAX_POPULATION_DENSITY = 50000;

// Enums for fixed sets
enum RiskLevel {
  Low = 'low',
  Moderate = 'moderate',
  High = 'high',
  Critical = 'critical'
}

// Use async/await over promises
const fetchData = async (): Promise<Data> => {
  const response = await api.get('/endpoint');
  return response.data;
};
```

**Linting:**
```bash
# Check style
npm run lint

# Fix auto-fixable issues
npm run lint:fix

# Type checking
npm run type-check
```

### Naming Conventions

**Database:**
- Tables: `snake_case` (e.g., `risk_assessments`)
- Columns: `snake_case` (e.g., `created_at`)
- Indexes: `ix_table_column`
- Foreign keys: `fk_table_column`

**API:**
- Endpoints: `kebab-case` (e.g., `/assess-risk`)
- Query params: `snake_case` (e.g., `?location_id=1`)
- JSON keys: `snake_case` (e.g., `"risk_score"`)

**Files:**
- Python: `snake_case.py`
- TypeScript: `PascalCase.tsx` (components), `camelCase.ts` (utils)
- Tests: `test_feature.py`, `Feature.test.tsx`

---

## API Development

### Adding a New Endpoint

**1. Define Schema:**
```python
# app/schemas/__init__.py
class NewFeatureRequest(BaseModel):
    """Request schema for new feature."""
    param1: str
    param2: int = Field(ge=0)

class NewFeatureResponse(BaseModel):
    """Response schema for new feature."""
    result: str
    success: bool
```

**2. Create Endpoint:**
```python
# app/api/new_feature.py
from fastapi import APIRouter, Depends
from app.schemas import NewFeatureRequest, NewFeatureResponse

router = APIRouter(prefix="/new-feature", tags=["New Feature"])

@router.post("", response_model=NewFeatureResponse)
async def new_feature_endpoint(
    request: NewFeatureRequest,
    db: AsyncSession = Depends(get_db)
) -> NewFeatureResponse:
    """New feature endpoint."""
    # Business logic
    result = process_feature(request)
    return NewFeatureResponse(result=result, success=True)
```

**3. Register Router:**
```python
# app/api/__init__.py
from app.api import new_feature

api_router.include_router(new_feature.router)
```

**4. Write Tests:**
```python
# tests/integration/test_new_feature.py
async def test_new_feature(client: AsyncClient):
    response = await client.post("/api/v1/new-feature", json={
        "param1": "value",
        "param2": 42
    })
    assert response.status_code == 200
    assert response.json()["success"] is True
```

---

## Frontend Development

### Adding a New Component

**1. Create Component:**
```typescript
// src/components/NewFeature/NewFeature.tsx
import React from 'react';
import { Box, Button } from '@mui/material';

interface NewFeatureProps {
  onAction: () => void;
}

export const NewFeature: React.FC<NewFeatureProps> = ({ onAction }) => {
  return (
    <Box>
      <Button onClick={onAction}>
        Click Me
      </Button>
    </Box>
  );
};
```

**2. Add Types:**
```typescript
// src/types/index.ts
export interface NewFeatureData {
  id: number;
  name: string;
}
```

**3. Create Test:**
```typescript
// src/components/NewFeature/__tests__/NewFeature.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { NewFeature } from '../NewFeature';

describe('NewFeature', () => {
  it('calls onAction when clicked', () => {
    const onAction = jest.fn();
    render(<NewFeature onAction={onAction} />);
    
    fireEvent.click(screen.getByText('Click Me'));
    
    expect(onAction).toHaveBeenCalled();
  });
});
```

---

## Database Management

### Creating Migrations

```bash
# Auto-generate migration
alembic revision --autogenerate -m "descriptive_name"

# Manual migration
alembic revision -m "manual_change"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# Check current version
alembic current
```

### Migration Best Practices

- **Always review auto-generated migrations**
- **Test migrations on development data**
- **Include both upgrade and downgrade**
- **Keep migrations small and focused**
- **Never edit applied migrations**

---

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete deployment guide.

**Quick Production Deploy:**
```bash
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Initialize data
docker-compose exec backend python init_db.py
```

---

## Troubleshooting Development Issues

### Common Issues

**Backend not starting:**
```bash
# Check logs
docker-compose logs backend

# Common fixes:
docker-compose down
docker-compose build --no-cache backend
docker-compose up backend
```

**Database connection errors:**
```bash
# Verify database is running
docker-compose ps db

# Check connection string
echo $DATABASE_URL

# Reset database
docker-compose down -v
docker-compose up -d db
```

**Frontend not compiling:**
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install

# Check for TypeScript errors
npm run type-check
```

---

## Resources

**Documentation:**
- FastAPI: https://fastapi.tiangolo.com
- React: https://react.dev
- SQLAlchemy: https://docs.sqlalchemy.org
- Playwright: https://playwright.dev

**Learning:**
- Python async: https://docs.python.org/3/library/asyncio.html
- React Hooks: https://react.dev/reference/react
- TypeScript: https://www.typescriptlang.org/docs

---

**Questions?** Open an issue or contact the development team.

*Last Updated: 2024-01-01*

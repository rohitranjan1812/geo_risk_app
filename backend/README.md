# Geo Risk Assessment Backend API

FastAPI-based backend for geographic risk assessment and simulation.

## Features

- **Risk Assessment**: Comprehensive algorithms for earthquake, flood, fire, and storm hazards
- **Location Management**: CRUD operations for geographic locations with risk factors
- **Historical Data**: Storage and analysis of past hazard events
- **RESTful API**: Full OpenAPI/Swagger documentation
- **Async Database**: SQLAlchemy with async PostgreSQL/SQLite support
- **Type Safety**: Pydantic models for request/response validation
- **Comprehensive Testing**: Unit and integration tests with >85% coverage

## Quick Start

### Installation

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Setup

Copy the example environment file and configure:

```bash
cp .env.example .env
```

Edit `.env` for your database configuration:

```env
DATABASE_URL=sqlite+aiosqlite:///./georisk.db
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Database Initialization

Create tables and load sample data:

```bash
python init_db.py
```

This creates:
- 4 hazard types (earthquake, flood, fire, storm)
- 5 sample locations (San Francisco, New Orleans, Tokyo, Miami, Los Angeles)
- Historical event data

### Run Development Server

```bash
python run.py
```

Or using uvicorn directly:

```bash
uvicorn app.main:app --reload
```

API will be available at: http://localhost:8000

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Risk Assessment

**POST /api/assess-risk**
- Assess risk for a location across multiple hazard types
- Accepts existing location_id or creates new location
- Returns risk scores, levels, and recommendations

Example request:
```json
{
  "location_id": 1,
  "hazard_types": ["earthquake", "flood"],
  "risk_factors": {
    "population_density": 5000.0,
    "building_code_rating": 7.0,
    "infrastructure_quality": 6.5
  }
}
```

Example response:
```json
{
  "location": {
    "id": 1,
    "name": "San Francisco, CA",
    "latitude": 37.7749,
    "longitude": -122.4194
  },
  "assessments": [
    {
      "hazard_type": "earthquake",
      "risk_score": 68.5,
      "risk_level": "high",
      "confidence_level": 0.85,
      "recommendations": [
        "Retrofit buildings to meet seismic standards",
        "Establish earthquake early warning systems"
      ]
    }
  ],
  "overall_risk_score": 55.3,
  "overall_risk_level": "high"
}
```

### Locations

- **GET /api/locations** - List all locations
- **POST /api/locations** - Create new location
- **GET /api/locations/{id}** - Get specific location
- **PUT /api/locations/{id}** - Update location
- **DELETE /api/locations/{id}** - Delete location

### Hazards

- **GET /api/hazards** - List all hazard types
- **POST /api/hazards** - Create new hazard type
- **GET /api/hazards/{id}** - Get specific hazard

### Historical Data

- **GET /api/historical-data/{location_id}** - Get events for location
- **POST /api/historical-data** - Record new historical event
- **GET /api/historical-data** - List all historical events

## Risk Calculation Algorithms

### Earthquake Risk
Emphasizes building codes (35%) and infrastructure (25%):
```python
risk_score = (
    pop_density * 0.15 +
    building_codes * 0.35 +
    infrastructure * 0.25 +
    hazard_severity * 0.15 +
    historical_frequency * 0.10
)
```

### Flood Risk
Emphasizes infrastructure/drainage (35%):
```python
risk_score = (
    pop_density * 0.20 +
    building_codes * 0.15 +
    infrastructure * 0.35 +
    hazard_severity * 0.20 +
    historical_frequency * 0.10
)
```

### Fire Risk
Emphasizes population density (30%) and building codes (30%):
```python
risk_score = (
    pop_density * 0.30 +
    building_codes * 0.30 +
    infrastructure * 0.15 +
    hazard_severity * 0.15 +
    historical_frequency * 0.10
)
```

### Storm Risk
Emphasizes infrastructure resilience (30%):
```python
risk_score = (
    pop_density * 0.20 +
    building_codes * 0.25 +
    infrastructure * 0.30 +
    hazard_severity * 0.15 +
    historical_frequency * 0.10
)
```

## Risk Levels

| Score Range | Risk Level |
|-------------|------------|
| 0-25        | LOW        |
| 25-50       | MODERATE   |
| 50-75       | HIGH       |
| 75-100      | CRITICAL   |

## Testing

### Run All Tests

```bash
pytest -v
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html --cov-report=term
```

View coverage report:
```bash
open htmlcov/index.html  # On macOS
# or
firefox htmlcov/index.html  # On Linux
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Specific test file
pytest tests/unit/test_risk_service.py -v
```

## Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   ├── risk.py       # Risk assessment endpoints
│   │   ├── locations.py  # Location CRUD
│   │   ├── hazards.py    # Hazard management
│   │   └── historical.py # Historical data
│   ├── core/             # Core configuration
│   │   └── config.py     # Settings management
│   ├── db/               # Database setup
│   │   └── session.py    # Async session management
│   ├── models/           # SQLAlchemy models
│   │   └── __init__.py   # Location, Hazard, RiskAssessment, HistoricalData
│   ├── schemas/          # Pydantic schemas
│   │   └── __init__.py   # Request/response models
│   ├── services/         # Business logic
│   │   └── risk_service.py  # Risk calculation algorithms
│   └── main.py           # FastAPI application
├── tests/
│   ├── unit/             # Unit tests
│   │   ├── test_schemas.py
│   │   └── test_risk_service.py
│   ├── integration/      # Integration tests
│   │   └── test_api_endpoints.py
│   └── conftest.py       # Test fixtures
├── alembic/              # Database migrations
│   ├── versions/
│   └── env.py
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
├── init_db.py            # Database initialization
└── run.py                # Development server
```

## Database Models

### Location
- Geographic coordinates (lat/lon)
- Population density
- Building code rating (0-10)
- Infrastructure quality (0-10)
- Custom metadata

### Hazard
- Type (earthquake, flood, fire, storm)
- Base severity (0-10)
- Weight factors for risk calculation
- Description

### RiskAssessment
- Location-hazard pairing
- Risk score (0-100)
- Risk level (LOW/MODERATE/HIGH/CRITICAL)
- Confidence level (0-1)
- Detailed factor analysis
- Mitigation recommendations

### HistoricalData
- Past hazard events
- Event severity and date
- Casualties and economic damage
- Impact descriptions

## CORS Configuration

CORS is enabled for frontend integration. Configure allowed origins in `.env`:

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://yourfrontend.com
```

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

Required for production:
- `DATABASE_URL` - PostgreSQL connection string
- `CORS_ORIGINS` - Comma-separated allowed origins
- `ENVIRONMENT=production`
- `LOG_LEVEL=INFO`

## Performance Considerations

- Uses async SQLAlchemy for non-blocking database operations
- Connection pooling configured automatically
- Efficient risk calculation with minimal database queries
- Pagination supported on all list endpoints

## Security

- Input validation via Pydantic models
- SQL injection protection via SQLAlchemy
- CORS configuration for cross-origin requests
- Environment-based configuration (no hardcoded secrets)

## Troubleshooting

### Database Connection Errors

Ensure your `DATABASE_URL` is correct. For PostgreSQL:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/georisk
DATABASE_URL_SYNC=postgresql://user:password@localhost:5432/georisk
```

For SQLite (development):
```env
DATABASE_URL=sqlite+aiosqlite:///./georisk.db
DATABASE_URL_SYNC=sqlite:///./georisk.db
```

### CORS Issues

Add your frontend URL to `CORS_ORIGINS` in `.env`.

### Import Errors

Ensure virtual environment is activated and dependencies installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Contributing

1. All code must have type hints
2. Write tests for new features (>85% coverage)
3. Follow existing code structure
4. Update documentation

## License

MIT License - See LICENSE file for details

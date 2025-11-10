# Comprehensive Risk Assessment System

## Overview

This system provides enterprise-grade risk assessment capabilities for multi-hazard environments with location-based scoring, historical analysis, and real-time visualization.

## Features

### 1. Multi-Hazard Support
- **Earthquake**: Ground motion impact analysis
- **Flood**: Water level and inundation modeling
- **Fire**: Spread risk and intensity analysis
- **Storm**: Wind speed and precipitation assessment
- Extensible architecture for additional hazard types

### 2. Location-Based Risk Scoring

#### Risk Factors Analyzed
- **Population Density**: Impact based on number of people at risk
- **Building Code Rating**: Structural resilience (0-10 scale)
- **Infrastructure Quality**: Utility system robustness (0-10 scale)
- **Hazard Severity**: Base hazard intensity for the location
- **Historical Frequency**: Past event occurrences

#### Risk Calculation
```
Risk Score = f(population_density, building_code, infrastructure, hazard_severity, historical_frequency)
Risk Level = {LOW: 0-25, MODERATE: 25-50, HIGH: 50-75, CRITICAL: 75-100}
```

### 3. Historical Data Analysis

The system processes historical event data to:
- Calculate event frequency and trends
- Analyze severity patterns over time
- Identify increasing/decreasing/stable trends
- Compute casualty and economic impact statistics
- Generate frequency-of-occurrence baselines

**Trend Analysis Includes**:
- Event count and frequency per year
- Average, min, max severity
- Standard deviation of severity
- Total casualties and economic damage
- Trend direction (increasing/decreasing/stable)

### 4. Advanced Analytics

#### Trend Analysis
```
GET /api/analytics/trends/{location_id}/{hazard_id}?years=10
```
Returns historical trends with frequency, severity patterns, and event statistics.

#### Risk Hotspot Identification
```
GET /api/analytics/hotspots/{hazard_id}?limit=20
```
Identifies the 20 highest-risk locations for a specific hazard type.

#### Location Comparison
```
POST /api/analytics/compare-locations
?location_ids=1,2,3&hazard_id=1
```
Compares risk profiles across multiple locations with infrastructure factors.

#### Regional Risk Index
```
GET /api/analytics/regional-risk
?min_latitude=-34.5&max_latitude=-34.0
&min_longitude=18.5&max_longitude=19.0
```
Calculates aggregate risk statistics for a geographic region.

#### Risk Forecasting
```
GET /api/analytics/forecast/{location_id}/{hazard_id}?months_ahead=12
```
Forecasts risk evolution using historical trend analysis with confidence intervals.

#### Critical Risk Factors
```
GET /api/analytics/critical-factors/{location_id}/{hazard_id}
```
Ranks risk factors by impact on overall risk score.

## Real-Time Visualization

### WebSocket Streams

#### Location Risk Updates
```
ws://api.example.com/api/ws/location/{location_id}
```
Streams real-time risk assessments for a specific location every 5 seconds.

**Message Format**:
```json
{
  "type": "risk_update",
  "timestamp": "2024-11-10T14:00:00Z",
  "data": [
    {
      "assessment_id": 123,
      "hazard_id": 1,
      "risk_score": 65.5,
      "risk_level": "high",
      "confidence": 0.92,
      "assessed_at": "2024-11-10T14:00:00Z"
    }
  ]
}
```

#### Regional Risk Visualization
```
ws://api.example.com/api/ws/region?min_latitude=-34.5&max_latitude=-34.0
&min_longitude=18.5&max_longitude=19.0
```
Streams regional risk statistics every 10 seconds.

**Message Format**:
```json
{
  "type": "region_risk_update",
  "timestamp": "2024-11-10T14:00:00Z",
  "data": {
    "assessment_count": 45,
    "risk_statistics": {
      "average_risk_score": 52.3,
      "median_risk_score": 50.0,
      "risk_level_distribution": {
        "low": 10,
        "moderate": 15,
        "high": 15,
        "critical": 5
      }
    }
  }
}
```

#### Hazard Risk Heatmap
```
ws://api.example.com/api/ws/hazard/{hazard_id}
```
Streams high-risk hotspots for a hazard type every 15 seconds.

**Message Format**:
```json
{
  "type": "hotspot_update",
  "timestamp": "2024-11-10T14:00:00Z",
  "hazard_type": "earthquake",
  "data": [
    {
      "location_id": 10,
      "location_name": "Downtown District",
      "latitude": -34.42,
      "longitude": 18.87,
      "risk_score": 78.5
    }
  ]
}
```

## API Endpoints

### Risk Assessment
- `POST /assess-risk` - Calculate risk for a location across multiple hazards
- `GET /assess-risk/{id}` - Get specific risk assessment

### Hazards
- `POST /hazards` - Create hazard type
- `GET /hazards` - List all hazards
- `GET /hazards/{id}` - Get hazard details

### Locations
- `POST /locations` - Create location
- `GET /locations` - List locations
- `GET /locations/{id}` - Get location details
- `GET /locations/search?latitude=X&longitude=Y&radius=10` - Search by coordinates

### Historical Data
- `POST /historical-data` - Record historical event
- `GET /historical-data` - List historical data
- `GET /historical-data/{location_id}` - Get location history

### Analytics
- `GET /analytics/hotspots/{hazard_id}` - Risk hotspots
- `GET /analytics/trends/{location_id}/{hazard_id}` - Historical trends
- `POST /analytics/compare-locations` - Compare locations
- `GET /analytics/regional-risk` - Regional statistics
- `GET /analytics/forecast/{location_id}/{hazard_id}` - Risk forecast
- `GET /analytics/critical-factors/{location_id}/{hazard_id}` - Critical factors

## Data Models

### Location
```python
{
  "id": int,
  "name": str,
  "latitude": float,
  "longitude": float,
  "population_density": float,  # people per sq km
  "building_code_rating": float,  # 0-10
  "infrastructure_quality": float,  # 0-10
}
```

### Hazard
```python
{
  "id": int,
  "hazard_type": "earthquake|flood|fire|storm",
  "name": str,
  "description": str,
  "base_severity": float,  # 0-10
  "weight_factors": dict  # Custom weights
}
```

### RiskAssessment
```python
{
  "id": int,
  "location_id": int,
  "hazard_id": int,
  "risk_score": float,  # 0-100
  "risk_level": "low|moderate|high|critical",
  "confidence_level": float,  # 0-1
  "factors_analysis": dict,
  "recommendations": list[str],
  "assessed_at": datetime
}
```

### HistoricalData
```python
{
  "id": int,
  "location_id": int,
  "hazard_id": int,
  "event_date": datetime,
  "severity": float,  # 0-10
  "casualties": int,
  "economic_damage": float  # USD
}
```

## Usage Examples

### Calculate Risk Assessment
```bash
curl -X POST http://api.example.com/api/assess-risk \
  -H "Content-Type: application/json" \
  -d '{
    "location": {
      "name": "Downtown",
      "latitude": -34.42,
      "longitude": 18.87,
      "population_density": 5000,
      "building_code_rating": 7.0,
      "infrastructure_quality": 6.5
    },
    "hazard_types": ["earthquake", "flood"]
  }'
```

### Get Risk Hotspots
```bash
curl http://api.example.com/api/analytics/hotspots/1?limit=20
```

### Compare Locations
```bash
curl -X POST http://api.example.com/api/analytics/compare-locations \
  ?location_ids=1,2,3&hazard_id=1
```

### Stream Real-Time Updates
```javascript
const ws = new WebSocket('ws://api.example.com/api/ws/location/1');
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log('Risk Update:', update);
};
```

## Architecture

### Service Layer
- **RiskCalculationService**: Core risk calculation engine
- **AdvancedAnalyticsService**: Historical analysis and forecasting
- **WebSocket Manager**: Real-time stream management

### Database
- SQLAlchemy ORM with async support
- PostgreSQL backend (configurable)
- Automatic migrations with Alembic

### API Framework
- FastAPI for REST endpoints
- WebSocket support for real-time updates
- Comprehensive validation with Pydantic

## Performance Characteristics

- **Risk Calculation**: ~100ms per hazard-location pair
- **Hotspot Query**: ~500ms for 10-year historical analysis
- **Forecast Generation**: ~200ms for 12-month forecast
- **WebSocket Updates**: 5-15 second refresh intervals

## Configuration

Set environment variables:
```bash
DATABASE_URL=postgresql://user:pass@localhost/risk_db
API_PREFIX=/api
CORS_ORIGINS=["http://localhost:3000"]
LOG_LEVEL=INFO
```

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200 OK` - Successful request
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

Error responses include detailed messages for debugging.

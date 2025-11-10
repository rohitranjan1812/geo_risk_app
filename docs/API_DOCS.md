# Geo Risk API Documentation

## Table of Contents
- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Error Handling](#error-handling)
- [API Endpoints](#api-endpoints)
  - [Health & Status](#health--status)
  - [Locations](#locations)
  - [Hazards](#hazards)
  - [Risk Assessment](#risk-assessment)
  - [Historical Data](#historical-data)
- [Data Models](#data-models)
- [Examples](#examples)

---

## Overview

The Geo Risk API provides comprehensive natural disaster risk assessment services. It enables users to:

- Manage geographic locations with risk factors
- Configure hazard types and severity parameters
- Perform multi-hazard risk assessments
- Access historical disaster data
- Generate risk recommendations

**API Version:** 1.0.0  
**Framework:** FastAPI  
**Data Format:** JSON  
**Protocol:** HTTP/HTTPS

---

## Base URL

```
Development:  http://localhost:8000
Production:   https://api.georisk.example.com
Docker:       http://localhost/api
```

All API endpoints are prefixed with `/api/v1` in production.

---

## Authentication

Currently, the API is **open** (no authentication required). Future versions will implement:

- **API Keys** for programmatic access
- **JWT Tokens** for user sessions
- **OAuth 2.0** for third-party integrations

---

## Error Handling

### Error Response Format

All errors follow this structure:

```json
{
  "detail": "Error description",
  "error_code": "OPTIONAL_ERROR_CODE"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid input data |
| 404 | Not Found | Resource not found |
| 422 | Validation Error | Request validation failed |
| 500 | Internal Server Error | Server error |

### Example Error Response

```json
{
  "detail": "Location with id 999 not found"
}
```

---

## API Endpoints

### Health & Status

#### GET `/health`

Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy"
}
```

#### GET `/`

Root endpoint with API information.

**Response:**
```json
{
  "name": "Geo Risk Assessment API",
  "version": "1.0.0",
  "status": "running"
}
```

---

### Locations

Manage geographic locations with risk assessment factors.

#### POST `/api/v1/locations`

Create a new location.

**Request Body:**
```json
{
  "name": "San Francisco, CA",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "population_density": 18838.0,
  "building_code_rating": 8.5,
  "infrastructure_quality": 7.5,
  "extra_data": {
    "city": "San Francisco",
    "state": "California",
    "country": "USA"
  }
}
```

**Field Descriptions:**

| Field | Type | Required | Range | Description |
|-------|------|----------|-------|-------------|
| `name` | string | Yes | 1-255 chars | Location name |
| `latitude` | float | Yes | -90 to 90 | Latitude coordinate |
| `longitude` | float | Yes | -180 to 180 | Longitude coordinate |
| `population_density` | float | No | ≥ 0 | People per sq km (default: 0) |
| `building_code_rating` | float | No | 0-10 | Building code quality (default: 5) |
| `infrastructure_quality` | float | No | 0-10 | Infrastructure rating (default: 5) |
| `extra_data` | object | No | - | Additional metadata |

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "San Francisco, CA",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "population_density": 18838.0,
  "building_code_rating": 8.5,
  "infrastructure_quality": 7.5,
  "extra_data": {
    "city": "San Francisco",
    "state": "California",
    "country": "USA"
  },
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

#### GET `/api/v1/locations`

Retrieve all locations with pagination.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | integer | 0 | Number of records to skip |
| `limit` | integer | 100 | Maximum records to return (max: 1000) |

**Example Request:**
```http
GET /api/v1/locations?skip=0&limit=10
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "San Francisco, CA",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "population_density": 18838.0,
    "building_code_rating": 8.5,
    "infrastructure_quality": 7.5,
    "extra_data": {},
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
]
```

#### GET `/api/v1/locations/{location_id}`

Retrieve a specific location.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `location_id` | integer | Location ID |

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "San Francisco, CA",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "population_density": 18838.0,
  "building_code_rating": 8.5,
  "infrastructure_quality": 7.5,
  "extra_data": {},
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Error Response (404):**
```json
{
  "detail": "Location with id 999 not found"
}
```

#### PUT `/api/v1/locations/{location_id}`

Update a location (partial update supported).

**Request Body:**
```json
{
  "name": "San Francisco Bay Area",
  "building_code_rating": 9.0
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "San Francisco Bay Area",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "population_density": 18838.0,
  "building_code_rating": 9.0,
  "infrastructure_quality": 7.5,
  "extra_data": {},
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T14:30:00Z"
}
```

#### DELETE `/api/v1/locations/{location_id}`

Delete a location.

**Response (200 OK):**
```json
{
  "message": "Location 1 deleted successfully"
}
```

---

### Hazards

Manage hazard type configurations.

#### POST `/api/v1/hazards`

Create a new hazard type.

**Request Body:**
```json
{
  "hazard_type": "earthquake",
  "name": "Earthquake",
  "description": "Seismic activity risk",
  "base_severity": 7.5,
  "weight_factors": {
    "population_density": 0.3,
    "building_code": 0.4,
    "infrastructure": 0.3
  }
}
```

**Hazard Types:**
- `earthquake` - Seismic activity
- `flood` - Water inundation
- `fire` - Wildfire risk
- `storm` - Hurricane/typhoon

**Response (201 Created):**
```json
{
  "id": 1,
  "hazard_type": "earthquake",
  "name": "Earthquake",
  "description": "Seismic activity risk",
  "base_severity": 7.5,
  "weight_factors": {
    "population_density": 0.3,
    "building_code": 0.4,
    "infrastructure": 0.3
  },
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Error Response (400):**
```json
{
  "detail": "Hazard type earthquake already exists"
}
```

#### GET `/api/v1/hazards`

Retrieve all configured hazard types.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "hazard_type": "earthquake",
    "name": "Earthquake",
    "description": "Seismic activity risk",
    "base_severity": 7.5,
    "weight_factors": {},
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
]
```

#### GET `/api/v1/hazards/{hazard_id}`

Retrieve a specific hazard.

**Response (200 OK):**
```json
{
  "id": 1,
  "hazard_type": "earthquake",
  "name": "Earthquake",
  "description": "Seismic activity risk",
  "base_severity": 7.5,
  "weight_factors": {},
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

---

### Risk Assessment

Perform comprehensive risk assessments.

#### POST `/api/v1/assess-risk`

Assess risk for a location across multiple hazard types.

**Request Body (Existing Location):**
```json
{
  "location_id": 1,
  "hazard_types": ["earthquake", "fire"],
  "risk_factors": {
    "population_density": 20000.0,
    "building_code_rating": 8.0,
    "infrastructure_quality": 7.0
  }
}
```

**Request Body (New Location):**
```json
{
  "location": {
    "name": "Los Angeles, CA",
    "latitude": 34.0522,
    "longitude": -118.2437,
    "population_density": 8483.0,
    "building_code_rating": 7.5,
    "infrastructure_quality": 6.5
  },
  "hazard_types": ["earthquake", "fire", "flood"],
  "risk_factors": null
}
```

**Field Descriptions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `location_id` | integer | No* | Existing location ID |
| `location` | object | No* | New location data |
| `hazard_types` | array | Yes | List of hazards to assess (min: 1) |
| `risk_factors` | object | No | Override location risk factors |

*Either `location_id` OR `location` must be provided.

**Response (200 OK):**
```json
{
  "location": {
    "id": 1,
    "name": "San Francisco, CA",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "population_density": 18838.0,
    "building_code_rating": 8.5,
    "infrastructure_quality": 7.5,
    "extra_data": {},
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  },
  "assessments": [
    {
      "id": 1,
      "location_id": 1,
      "hazard_id": 1,
      "hazard_type": "earthquake",
      "risk_score": 72.5,
      "risk_level": "high",
      "confidence_level": 0.85,
      "factors_analysis": {
        "population_density_impact": 15.2,
        "building_code_impact": -8.5,
        "infrastructure_impact": -5.0,
        "hazard_severity_impact": 60.0,
        "historical_frequency_impact": 10.8
      },
      "recommendations": [
        "Strengthen building codes for seismic resilience",
        "Conduct regular earthquake drills",
        "Retrofit older structures"
      ],
      "assessed_at": "2024-01-01T15:00:00Z"
    },
    {
      "id": 2,
      "location_id": 1,
      "hazard_id": 3,
      "hazard_type": "fire",
      "risk_score": 45.3,
      "risk_level": "moderate",
      "confidence_level": 0.78,
      "factors_analysis": {
        "population_density_impact": 12.0,
        "building_code_impact": -6.0,
        "infrastructure_impact": -4.0,
        "hazard_severity_impact": 35.0,
        "historical_frequency_impact": 8.3
      },
      "recommendations": [
        "Implement fire prevention programs",
        "Maintain firebreaks in high-risk areas"
      ],
      "assessed_at": "2024-01-01T15:00:00Z"
    }
  ],
  "overall_risk_score": 58.9,
  "overall_risk_level": "high"
}
```

**Risk Levels:**
- `low` - Risk score 0-25
- `moderate` - Risk score 26-50
- `high` - Risk score 51-75
- `critical` - Risk score 76-100

**Error Responses:**

404 - Location not found:
```json
{
  "detail": "Location with id 999 not found"
}
```

404 - Hazard types not found:
```json
{
  "detail": "Hazard types not found: {'invalid_hazard'}"
}
```

400 - Missing required data:
```json
{
  "detail": "Either location_id or location data must be provided"
}
```

---

### Historical Data

Access historical disaster event data.

#### POST `/api/v1/historical`

Record a historical disaster event.

**Request Body:**
```json
{
  "location_id": 1,
  "hazard_id": 1,
  "event_date": "1906-04-18T05:12:00Z",
  "severity": 9.5,
  "impact_description": "Major earthquake causing widespread destruction",
  "casualties": 3000,
  "economic_damage": 400000000.0,
  "extra_data": {
    "magnitude": 7.9,
    "epicenter": "San Francisco Bay"
  }
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "location_id": 1,
  "hazard_id": 1,
  "event_date": "1906-04-18T05:12:00Z",
  "severity": 9.5,
  "impact_description": "Major earthquake causing widespread destruction",
  "casualties": 3000,
  "economic_damage": 400000000.0,
  "extra_data": {
    "magnitude": 7.9,
    "epicenter": "San Francisco Bay"
  },
  "created_at": "2024-01-01T12:00:00Z"
}
```

#### GET `/api/v1/historical`

Retrieve historical events with filters.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `location_id` | integer | Filter by location |
| `hazard_id` | integer | Filter by hazard type |
| `skip` | integer | Pagination offset |
| `limit` | integer | Max records (default: 100) |

**Example:**
```http
GET /api/v1/historical?location_id=1&hazard_id=1&limit=10
```

---

## Data Models

### Location

```typescript
{
  id: number;
  name: string;
  latitude: number;        // -90 to 90
  longitude: number;       // -180 to 180
  population_density: number;      // ≥ 0
  building_code_rating: number;    // 0-10
  infrastructure_quality: number;  // 0-10
  extra_data: object | null;
  created_at: string;      // ISO 8601 datetime
  updated_at: string;
}
```

### Hazard

```typescript
{
  id: number;
  hazard_type: "earthquake" | "flood" | "fire" | "storm";
  name: string;
  description: string | null;
  base_severity: number;   // 0-10
  weight_factors: object | null;
  created_at: string;
  updated_at: string;
}
```

### Risk Assessment

```typescript
{
  id: number;
  location_id: number;
  hazard_id: number;
  hazard_type: string;
  risk_score: number;      // 0-100
  risk_level: "low" | "moderate" | "high" | "critical";
  confidence_level: number;  // 0-1
  factors_analysis: {
    population_density_impact: number;
    building_code_impact: number;
    infrastructure_impact: number;
    hazard_severity_impact: number;
    historical_frequency_impact: number;
  };
  recommendations: string[];
  assessed_at: string;
}
```

---

## Examples

### Complete Workflow Example

```bash
# 1. Check API health
curl -X GET http://localhost:8000/health

# 2. Create a location
curl -X POST http://localhost:8000/api/v1/locations \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tokyo, Japan",
    "latitude": 35.6762,
    "longitude": 139.6503,
    "population_density": 6168.0,
    "building_code_rating": 9.0,
    "infrastructure_quality": 8.5
  }'

# 3. Get all hazard types
curl -X GET http://localhost:8000/api/v1/hazards

# 4. Perform risk assessment
curl -X POST http://localhost:8000/api/v1/assess-risk \
  -H "Content-Type: application/json" \
  -d '{
    "location_id": 1,
    "hazard_types": ["earthquake", "storm", "flood"],
    "risk_factors": {
      "population_density": 6168.0,
      "building_code_rating": 9.0,
      "infrastructure_quality": 8.5
    }
  }'

# 5. Get all locations
curl -X GET "http://localhost:8000/api/v1/locations?limit=10"
```

### Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Create location
location_data = {
    "name": "New York, NY",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "population_density": 10933.0,
    "building_code_rating": 8.0,
    "infrastructure_quality": 7.0
}
response = requests.post(f"{BASE_URL}/locations", json=location_data)
location = response.json()

# Assess risk
assessment_request = {
    "location_id": location["id"],
    "hazard_types": ["flood", "storm"]
}
response = requests.post(f"{BASE_URL}/assess-risk", json=assessment_request)
assessment = response.json()

print(f"Overall Risk: {assessment['overall_risk_level']}")
print(f"Risk Score: {assessment['overall_risk_score']}")

for result in assessment['assessments']:
    print(f"\n{result['hazard_type'].upper()}:")
    print(f"  Score: {result['risk_score']}")
    print(f"  Level: {result['risk_level']}")
    print(f"  Recommendations: {', '.join(result['recommendations'])}")
```

### JavaScript Client Example

```javascript
const BASE_URL = 'http://localhost:8000/api/v1';

// Create location and assess risk
async function assessLocationRisk() {
  // Create location
  const locationData = {
    name: 'Miami, FL',
    latitude: 25.7617,
    longitude: -80.1918,
    population_density: 4770.0,
    building_code_rating: 7.5,
    infrastructure_quality: 6.5
  };
  
  const locationResponse = await fetch(`${BASE_URL}/locations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(locationData)
  });
  const location = await locationResponse.json();
  
  // Assess risk
  const assessmentRequest = {
    location_id: location.id,
    hazard_types: ['storm', 'flood']
  };
  
  const assessmentResponse = await fetch(`${BASE_URL}/assess-risk`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(assessmentRequest)
  });
  const assessment = await assessmentResponse.json();
  
  console.log('Overall Risk:', assessment.overall_risk_level);
  console.log('Risk Score:', assessment.overall_risk_score);
  
  assessment.assessments.forEach(result => {
    console.log(`\n${result.hazard_type.toUpperCase()}:`);
    console.log(`  Score: ${result.risk_score}`);
    console.log(`  Level: ${result.risk_level}`);
  });
}

assessLocationRisk();
```

---

## Interactive API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

These interfaces allow you to:
- Browse all endpoints
- View request/response schemas
- Test endpoints directly from the browser
- Download OpenAPI specification (JSON)

---

## Rate Limiting

Currently **no rate limiting** is implemented. Future versions will include:

- 100 requests/minute for unauthenticated users
- 1000 requests/minute for authenticated users
- Burst allowance for batch operations

---

## Changelog

### Version 1.0.0 (Current)
- Initial API release
- Location management endpoints
- Hazard configuration endpoints
- Multi-hazard risk assessment
- Historical data storage
- Automated risk scoring algorithm

---

## Support

For API questions and issues:

- **Documentation:** See `/docs` directory
- **Issues:** GitHub Issues (if applicable)
- **Email:** support@georisk.example.com

---

*Last Updated: 2024-01-01*

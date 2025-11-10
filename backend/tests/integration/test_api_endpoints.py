"""Integration tests for API endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestLocationEndpoints:
    """Test location API endpoints."""
    
    async def test_create_location(self, client: AsyncClient):
        """Test creating a new location."""
        location_data = {
            "name": "San Francisco",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "population_density": 7174.0,
            "building_code_rating": 8.5,
            "infrastructure_quality": 7.5
        }
        
        response = await client.post("/api/locations", json=location_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "San Francisco"
        assert data["latitude"] == 37.7749
        assert "id" in data
        assert "created_at" in data
    
    async def test_get_locations(self, client: AsyncClient):
        """Test retrieving all locations."""
        # Create a location first
        location_data = {
            "name": "Test City",
            "latitude": 40.7128,
            "longitude": -74.0060
        }
        await client.post("/api/locations", json=location_data)
        
        # Get all locations
        response = await client.get("/api/locations")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    async def test_get_location_by_id(self, client: AsyncClient):
        """Test retrieving a specific location."""
        # Create location
        location_data = {"name": "NYC", "latitude": 40.7128, "longitude": -74.0060}
        create_response = await client.post("/api/locations", json=location_data)
        location_id = create_response.json()["id"]
        
        # Get by ID
        response = await client.get(f"/api/locations/{location_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == location_id
        assert data["name"] == "NYC"
    
    async def test_get_nonexistent_location(self, client: AsyncClient):
        """Test retrieving a non-existent location returns 404."""
        response = await client.get("/api/locations/99999")
        
        assert response.status_code == 404
    
    async def test_update_location(self, client: AsyncClient):
        """Test updating a location."""
        # Create location
        location_data = {"name": "Original", "latitude": 0.0, "longitude": 0.0}
        create_response = await client.post("/api/locations", json=location_data)
        location_id = create_response.json()["id"]
        
        # Update
        update_data = {"name": "Updated", "building_code_rating": 9.0}
        response = await client.put(f"/api/locations/{location_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated"
        assert data["building_code_rating"] == 9.0
    
    async def test_delete_location(self, client: AsyncClient):
        """Test deleting a location."""
        # Create location
        location_data = {"name": "To Delete", "latitude": 0.0, "longitude": 0.0}
        create_response = await client.post("/api/locations", json=location_data)
        location_id = create_response.json()["id"]
        
        # Delete
        response = await client.delete(f"/api/locations/{location_id}")
        
        assert response.status_code == 200
        
        # Verify deleted
        get_response = await client.get(f"/api/locations/{location_id}")
        assert get_response.status_code == 404


@pytest.mark.asyncio
class TestHazardEndpoints:
    """Test hazard API endpoints."""
    
    async def test_create_hazard(self, client: AsyncClient):
        """Test creating a hazard type."""
        hazard_data = {
            "hazard_type": "earthquake",
            "name": "Earthquake",
            "description": "Seismic activity",
            "base_severity": 7.0
        }
        
        response = await client.post("/api/hazards", json=hazard_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["hazard_type"] == "earthquake"
        assert data["base_severity"] == 7.0
    
    async def test_create_duplicate_hazard_type(self, client: AsyncClient, sample_hazards):
        """Test that creating duplicate hazard type fails."""
        hazard_data = {
            "hazard_type": "earthquake",  # Already exists in sample_hazards
            "name": "Duplicate",
            "base_severity": 5.0
        }
        
        response = await client.post("/api/hazards", json=hazard_data)
        
        assert response.status_code == 400
    
    async def test_get_hazards(self, client: AsyncClient, sample_hazards):
        """Test retrieving all hazards."""
        response = await client.get("/api/hazards")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 4  # All sample hazards


@pytest.mark.asyncio
class TestRiskAssessmentEndpoints:
    """Test risk assessment API endpoints."""
    
    async def test_assess_risk_existing_location(self, client: AsyncClient, sample_hazards):
        """Test risk assessment with existing location."""
        # Create location
        location_data = {
            "name": "Risk Test City",
            "latitude": 37.0,
            "longitude": -122.0,
            "population_density": 5000.0,
            "building_code_rating": 6.0,
            "infrastructure_quality": 7.0
        }
        create_response = await client.post("/api/locations", json=location_data)
        location_id = create_response.json()["id"]
        
        # Assess risk
        assessment_request = {
            "location_id": location_id,
            "hazard_types": ["earthquake", "flood"]
        }
        
        response = await client.post("/api/assess-risk", json=assessment_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "location" in data
        assert "assessments" in data
        assert "overall_risk_score" in data
        assert "overall_risk_level" in data
        
        # Should have 2 assessments
        assert len(data["assessments"]) == 2
        
        # Each assessment should have required fields
        for assessment in data["assessments"]:
            assert "risk_score" in assessment
            assert "risk_level" in assessment
            assert "confidence_level" in assessment
            assert "factors_analysis" in assessment
            assert "recommendations" in assessment
            assert 0 <= assessment["risk_score"] <= 100
            assert 0 <= assessment["confidence_level"] <= 1
    
    async def test_assess_risk_new_location(self, client: AsyncClient, sample_hazards):
        """Test risk assessment with new location."""
        assessment_request = {
            "location": {
                "name": "New Risk City",
                "latitude": 40.0,
                "longitude": -74.0,
                "population_density": 8000.0,
                "building_code_rating": 4.0,
                "infrastructure_quality": 5.0
            },
            "hazard_types": ["storm", "fire"]
        }
        
        response = await client.post("/api/assess-risk", json=assessment_request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["location"]["name"] == "New Risk City"
        assert len(data["assessments"]) == 2
    
    async def test_assess_risk_custom_factors(self, client: AsyncClient, sample_hazards):
        """Test risk assessment with custom risk factors."""
        # Create location
        location_data = {"name": "Custom Test", "latitude": 35.0, "longitude": -118.0}
        create_response = await client.post("/api/locations", json=location_data)
        location_id = create_response.json()["id"]
        
        # Assess with custom factors
        assessment_request = {
            "location_id": location_id,
            "hazard_types": ["earthquake"],
            "risk_factors": {
                "population_density": 10000.0,
                "building_code_rating": 2.0,
                "infrastructure_quality": 3.0
            }
        }
        
        response = await client.post("/api/assess-risk", json=assessment_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Risk should be high due to poor factors
        assert data["assessments"][0]["risk_score"] > 40
    
    async def test_assess_risk_invalid_hazard_type(self, client: AsyncClient):
        """Test risk assessment with invalid hazard type."""
        assessment_request = {
            "location": {"name": "Test", "latitude": 0.0, "longitude": 0.0},
            "hazard_types": ["invalid_hazard"]
        }
        
        response = await client.post("/api/assess-risk", json=assessment_request)
        
        assert response.status_code == 422  # Validation error
    
    async def test_assess_risk_no_location(self, client: AsyncClient):
        """Test risk assessment without location fails."""
        assessment_request = {
            "hazard_types": ["earthquake"]
        }
        
        response = await client.post("/api/assess-risk", json=assessment_request)
        
        assert response.status_code == 400


@pytest.mark.asyncio
class TestHistoricalDataEndpoints:
    """Test historical data API endpoints."""
    
    async def test_create_historical_data(self, client: AsyncClient, sample_hazards):
        """Test creating historical event data."""
        # Create location
        location_data = {"name": "Historical City", "latitude": 38.0, "longitude": -120.0}
        loc_response = await client.post("/api/locations", json=location_data)
        location_id = loc_response.json()["id"]
        
        # Get hazard ID
        hazards_response = await client.get("/api/hazards")
        hazard_id = hazards_response.json()[0]["id"]
        
        # Create historical data
        historical_data = {
            "location_id": location_id,
            "hazard_id": hazard_id,
            "event_date": "2020-01-15T10:30:00",
            "severity": 8.0,
            "impact_description": "Major earthquake damage",
            "casualties": 50,
            "economic_damage": 5000000.0
        }
        
        response = await client.post("/api/historical-data", json=historical_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["severity"] == 8.0
        assert data["casualties"] == 50
    
    async def test_get_historical_data_by_location(self, client: AsyncClient, sample_hazards):
        """Test retrieving historical data for a location."""
        # Create location and historical data
        location_data = {"name": "Event City", "latitude": 36.0, "longitude": -115.0}
        loc_response = await client.post("/api/locations", json=location_data)
        location_id = loc_response.json()["id"]
        
        hazards_response = await client.get("/api/hazards")
        hazard_id = hazards_response.json()[0]["id"]
        
        # Create 3 events
        for i in range(3):
            historical_data = {
                "location_id": location_id,
                "hazard_id": hazard_id,
                "event_date": f"2020-0{i+1}-01T00:00:00",
                "severity": 5.0 + i
            }
            await client.post("/api/historical-data", json=historical_data)
        
        # Retrieve
        response = await client.get(f"/api/historical-data/{location_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
    
    async def test_get_historical_data_with_hazard_filter(self, client: AsyncClient, sample_hazards):
        """Test filtering historical data by hazard type."""
        # Setup
        location_data = {"name": "Filter Test", "latitude": 33.0, "longitude": -117.0}
        loc_response = await client.post("/api/locations", json=location_data)
        location_id = loc_response.json()["id"]
        
        hazards_response = await client.get("/api/hazards")
        hazards = hazards_response.json()
        
        # Create events for different hazards
        for hazard in hazards[:2]:
            historical_data = {
                "location_id": location_id,
                "hazard_id": hazard["id"],
                "event_date": "2020-01-01T00:00:00",
                "severity": 6.0
            }
            await client.post("/api/historical-data", json=historical_data)
        
        # Filter by first hazard
        response = await client.get(
            f"/api/historical-data/{location_id}?hazard_id={hazards[0]['id']}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["hazard_id"] == hazards[0]["id"]

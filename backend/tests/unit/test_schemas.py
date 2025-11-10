"""Unit tests for Pydantic schemas."""
import pytest
from datetime import datetime
from pydantic import ValidationError

from app.schemas import (
    LocationCreate,
    LocationUpdate,
    HazardCreate,
    RiskAssessmentRequest,
    RiskFactors,
    HazardType,
    HistoricalDataCreate
)


class TestLocationSchemas:
    """Test location schema validation."""
    
    def test_location_create_valid(self):
        """Test valid location creation."""
        data = {
            "name": "San Francisco",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "population_density": 7174.0,
            "building_code_rating": 8.5,
            "infrastructure_quality": 7.5
        }
        
        location = LocationCreate(**data)
        assert location.name == "San Francisco"
        assert location.latitude == 37.7749
        assert location.building_code_rating == 8.5
    
    def test_location_create_defaults(self):
        """Test location creation with default values."""
        data = {
            "name": "Test City",
            "latitude": 0.0,
            "longitude": 0.0
        }
        
        location = LocationCreate(**data)
        assert location.population_density == 0.0
        assert location.building_code_rating == 5.0
        assert location.infrastructure_quality == 5.0
    
    def test_location_latitude_validation(self):
        """Test latitude boundary validation."""
        with pytest.raises(ValidationError):
            LocationCreate(
                name="Test",
                latitude=91.0,  # Invalid: > 90
                longitude=0.0
            )
        
        with pytest.raises(ValidationError):
            LocationCreate(
                name="Test",
                latitude=-91.0,  # Invalid: < -90
                longitude=0.0
            )
    
    def test_location_longitude_validation(self):
        """Test longitude boundary validation."""
        with pytest.raises(ValidationError):
            LocationCreate(
                name="Test",
                latitude=0.0,
                longitude=181.0  # Invalid: > 180
            )
    
    def test_location_update_partial(self):
        """Test partial location update."""
        update = LocationUpdate(name="Updated Name")
        assert update.name == "Updated Name"
        assert update.latitude is None


class TestHazardSchemas:
    """Test hazard schema validation."""
    
    def test_hazard_create_valid(self):
        """Test valid hazard creation."""
        data = {
            "hazard_type": HazardType.EARTHQUAKE,
            "name": "Earthquake",
            "description": "Seismic hazard",
            "base_severity": 7.5
        }
        
        hazard = HazardCreate(**data)
        assert hazard.hazard_type == HazardType.EARTHQUAKE
        assert hazard.base_severity == 7.5
    
    def test_hazard_severity_validation(self):
        """Test severity boundary validation."""
        with pytest.raises(ValidationError):
            HazardCreate(
                hazard_type=HazardType.FLOOD,
                name="Flood",
                base_severity=11.0  # Invalid: > 10
            )


class TestRiskAssessmentSchemas:
    """Test risk assessment schema validation."""
    
    def test_risk_assessment_request_with_location_id(self):
        """Test risk assessment request with existing location."""
        data = {
            "location_id": 1,
            "hazard_types": [HazardType.EARTHQUAKE, HazardType.FLOOD]
        }
        
        request = RiskAssessmentRequest(**data)
        assert request.location_id == 1
        assert len(request.hazard_types) == 2
    
    def test_risk_assessment_request_with_new_location(self):
        """Test risk assessment request with new location."""
        data = {
            "location": {
                "name": "New City",
                "latitude": 40.7128,
                "longitude": -74.0060
            },
            "hazard_types": [HazardType.STORM]
        }
        
        request = RiskAssessmentRequest(**data)
        assert request.location is not None
        assert request.location.name == "New City"
    
    def test_risk_factors_validation(self):
        """Test risk factors schema."""
        factors = RiskFactors(
            population_density=5000.0,
            building_code_rating=7.5,
            infrastructure_quality=6.0
        )
        
        assert factors.population_density == 5000.0
        assert factors.building_code_rating == 7.5
    
    def test_hazard_types_required(self):
        """Test that at least one hazard type is required."""
        with pytest.raises(ValidationError):
            RiskAssessmentRequest(
                location_id=1,
                hazard_types=[]  # Invalid: empty list
            )


class TestHistoricalDataSchemas:
    """Test historical data schema validation."""
    
    def test_historical_data_create_valid(self):
        """Test valid historical data creation."""
        data = {
            "location_id": 1,
            "hazard_id": 1,
            "event_date": datetime.utcnow(),
            "severity": 7.5,
            "impact_description": "Major earthquake",
            "casualties": 100,
            "economic_damage": 1000000.0
        }
        
        historical = HistoricalDataCreate(**data)
        assert historical.severity == 7.5
        assert historical.casualties == 100
    
    def test_historical_data_defaults(self):
        """Test historical data default values."""
        data = {
            "location_id": 1,
            "hazard_id": 1,
            "event_date": datetime.utcnow(),
            "severity": 5.0
        }
        
        historical = HistoricalDataCreate(**data)
        assert historical.casualties == 0
        assert historical.economic_damage == 0.0
    
    def test_severity_validation(self):
        """Test severity boundary validation."""
        with pytest.raises(ValidationError):
            HistoricalDataCreate(
                location_id=1,
                hazard_id=1,
                event_date=datetime.utcnow(),
                severity=15.0  # Invalid: > 10
            )

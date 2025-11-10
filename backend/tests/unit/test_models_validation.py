"""Unit tests for database models."""
import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models import Location, Hazard, HazardType, RiskLevel, RiskAssessment, HistoricalData


@pytest.mark.asyncio
class TestLocationModel:
    """Test Location model constraints and relationships."""
    
    async def test_create_location_minimal(self, db_session):
        """Test creating location with minimal required fields."""
        location = Location(
            name="Test City",
            latitude=40.7128,
            longitude=-74.0060
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        assert location.id is not None
        assert location.name == "Test City"
        assert location.population_density == 0.0
        assert location.building_code_rating == 5.0
        assert location.infrastructure_quality == 5.0
        assert location.created_at is not None
        assert location.updated_at is not None
    
    async def test_location_with_extra_data(self, db_session):
        """Test location with JSON extra_data."""
        location = Location(
            name="Data Rich City",
            latitude=51.5074,
            longitude=-0.1278,
            extra_data={
                "country": "UK",
                "region": "London",
                "timezone": "GMT",
                "custom_field": 12345
            }
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        assert location.extra_data["country"] == "UK"
        assert location.extra_data["custom_field"] == 12345
    
    async def test_location_updated_at_changes(self, db_session):
        """Test that updated_at changes on update."""
        location = Location(
            name="Update Test",
            latitude=0.0,
            longitude=0.0
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        original_updated = location.updated_at
        
        # Update location
        location.name = "Updated Name"
        await db_session.commit()
        await db_session.refresh(location)
        
        assert location.updated_at >= original_updated
    
    async def test_location_cascade_delete_assessments(self, db_session, sample_hazards):
        """Test that deleting location cascades to risk assessments."""
        location = Location(
            name="Cascade Test",
            latitude=35.0,
            longitude=139.0
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        hazard = sample_hazards[0]
        
        # Create assessment
        assessment = RiskAssessment(
            location_id=location.id,
            hazard_id=hazard.id,
            risk_score=50.0,
            risk_level=RiskLevel.MODERATE,
            confidence_level=0.7
        )
        db_session.add(assessment)
        await db_session.commit()
        
        assessment_id = assessment.id
        
        # Delete location
        await db_session.delete(location)
        await db_session.commit()
        
        # Assessment should be deleted too
        from sqlalchemy import select
        result = await db_session.execute(
            select(RiskAssessment).where(RiskAssessment.id == assessment_id)
        )
        assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
class TestHazardModel:
    """Test Hazard model constraints."""
    
    async def test_hazard_type_uniqueness(self, db_session):
        """Test that hazard_type must be unique."""
        hazard1 = Hazard(
            hazard_type=HazardType.EARTHQUAKE,
            name="Earthquake",
            base_severity=7.0
        )
        db_session.add(hazard1)
        await db_session.commit()
        
        # Try to add duplicate
        hazard2 = Hazard(
            hazard_type=HazardType.EARTHQUAKE,  # Duplicate
            name="Another Earthquake",
            base_severity=6.0
        )
        db_session.add(hazard2)
        
        with pytest.raises(IntegrityError):
            await db_session.commit()
    
    async def test_hazard_with_weight_factors(self, db_session):
        """Test hazard with JSON weight factors."""
        hazard = Hazard(
            hazard_type=HazardType.FLOOD,
            name="Flood",
            base_severity=6.5,
            weight_factors={
                "drainage": 0.4,
                "elevation": 0.3,
                "rainfall": 0.3
            }
        )
        db_session.add(hazard)
        await db_session.commit()
        await db_session.refresh(hazard)
        
        assert hazard.weight_factors["drainage"] == 0.4
        assert sum(hazard.weight_factors.values()) == pytest.approx(1.0)


@pytest.mark.asyncio
class TestRiskAssessmentModel:
    """Test RiskAssessment model."""
    
    async def test_create_risk_assessment(self, db_session, sample_hazards):
        """Test creating a complete risk assessment."""
        location = Location(
            name="Assessment Test",
            latitude=34.0522,
            longitude=-118.2437
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        hazard = sample_hazards[0]
        
        assessment = RiskAssessment(
            location_id=location.id,
            hazard_id=hazard.id,
            risk_score=67.5,
            risk_level=RiskLevel.HIGH,
            confidence_level=0.85,
            factors_analysis={
                "population": 45.0,
                "building_codes": 60.0,
                "infrastructure": 55.0
            },
            recommendations=[
                "Improve building codes",
                "Strengthen infrastructure"
            ]
        )
        db_session.add(assessment)
        await db_session.commit()
        await db_session.refresh(assessment)
        
        assert assessment.id is not None
        assert assessment.risk_score == 67.5
        assert assessment.risk_level == RiskLevel.HIGH
        assert len(assessment.recommendations) == 2
        assert assessment.assessed_at is not None
    
    async def test_assessment_relationships(self, db_session, sample_hazards):
        """Test assessment relationships to location and hazard."""
        location = Location(
            name="Relationship Test",
            latitude=40.0,
            longitude=-75.0
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        hazard = sample_hazards[1]
        
        assessment = RiskAssessment(
            location_id=location.id,
            hazard_id=hazard.id,
            risk_score=30.0,
            risk_level=RiskLevel.MODERATE,
            confidence_level=0.6
        )
        db_session.add(assessment)
        await db_session.commit()
        await db_session.refresh(assessment)
        
        # Test relationships
        assert assessment.location.name == "Relationship Test"
        assert assessment.hazard.hazard_type == hazard.hazard_type


@pytest.mark.asyncio
class TestHistoricalDataModel:
    """Test HistoricalData model."""
    
    async def test_create_historical_event(self, db_session, sample_hazards):
        """Test creating historical event data."""
        location = Location(
            name="Historical Test",
            latitude=29.7604,
            longitude=-95.3698
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        hazard = sample_hazards[1]  # Flood
        
        event = HistoricalData(
            location_id=location.id,
            hazard_id=hazard.id,
            event_date=datetime(2005, 8, 29),  # Hurricane Katrina
            severity=9.5,
            impact_description="Catastrophic flooding",
            casualties=1833,
            economic_damage=125000000000.0,
            extra_data={
                "name": "Hurricane Katrina",
                "category": 5,
                "wind_speed": 175
            }
        )
        db_session.add(event)
        await db_session.commit()
        await db_session.refresh(event)
        
        assert event.id is not None
        assert event.severity == 9.5
        assert event.casualties == 1833
        assert event.extra_data["name"] == "Hurricane Katrina"
        assert event.created_at is not None
    
    async def test_historical_data_defaults(self, db_session, sample_hazards):
        """Test historical data with default values."""
        location = Location(
            name="Default Test",
            latitude=0.0,
            longitude=0.0
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        hazard = sample_hazards[0]
        
        event = HistoricalData(
            location_id=location.id,
            hazard_id=hazard.id,
            event_date=datetime.utcnow(),
            severity=5.0
        )
        db_session.add(event)
        await db_session.commit()
        await db_session.refresh(event)
        
        assert event.casualties == 0
        assert event.economic_damage == 0.0
    
    async def test_historical_cascade_delete(self, db_session, sample_hazards):
        """Test that deleting location cascades to historical data."""
        location = Location(
            name="Cascade Historical",
            latitude=0.0,
            longitude=0.0
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        hazard = sample_hazards[0]
        
        event = HistoricalData(
            location_id=location.id,
            hazard_id=hazard.id,
            event_date=datetime.utcnow(),
            severity=6.0
        )
        db_session.add(event)
        await db_session.commit()
        
        event_id = event.id
        
        # Delete location
        await db_session.delete(location)
        await db_session.commit()
        
        # Event should be deleted
        from sqlalchemy import select
        result = await db_session.execute(
            select(HistoricalData).where(HistoricalData.id == event_id)
        )
        assert result.scalar_one_or_none() is None

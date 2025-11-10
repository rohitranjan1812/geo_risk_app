"""Unit tests for risk calculation service."""
import pytest
from datetime import datetime, timedelta

from app.services import RiskCalculationService
from app.models import Location, Hazard, HazardType, RiskLevel, HistoricalData


@pytest.mark.asyncio
class TestRiskCalculationService:
    """Test risk calculation algorithms."""
    
    async def test_calculate_earthquake_risk_high_building_code_impact(self, db_session, sample_hazards):
        """Test earthquake risk with poor building codes."""
        # Create location with poor building codes
        location = Location(
            name="Vulnerable City",
            latitude=37.7749,
            longitude=-122.4194,
            population_density=5000.0,
            building_code_rating=2.0,  # Poor building codes
            infrastructure_quality=5.0
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        # Get earthquake hazard
        earthquake = next(h for h in sample_hazards if h.hazard_type == HazardType.EARTHQUAKE)
        
        # Calculate risk
        service = RiskCalculationService(db_session)
        risk_score, risk_level, confidence, factors, recommendations = \
            await service.calculate_risk(location, earthquake)
        
        # Building codes should have high impact (inverse relationship)
        assert factors['building_code_impact'] > 70  # 100 - (2.0 * 10) = 80
        
        # Overall risk should be high due to poor building codes
        assert risk_score > 40
        assert risk_level in [RiskLevel.MODERATE, RiskLevel.HIGH, RiskLevel.CRITICAL]
        
        # Should recommend building code improvements
        assert any("building code" in r.lower() for r in recommendations)
    
    async def test_calculate_flood_risk_infrastructure_critical(self, db_session, sample_hazards):
        """Test flood risk emphasizes infrastructure."""
        location = Location(
            name="Flood Prone",
            latitude=30.0,
            longitude=-90.0,
            population_density=3000.0,
            building_code_rating=7.0,
            infrastructure_quality=3.0  # Poor drainage
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        flood = next(h for h in sample_hazards if h.hazard_type == HazardType.FLOOD)
        
        service = RiskCalculationService(db_session)
        risk_score, risk_level, confidence, factors, recommendations = \
            await service.calculate_risk(location, flood)
        
        # Infrastructure should have high impact for floods
        assert factors['infrastructure_impact'] > 60  # 100 - (3.0 * 10) = 70
        
        # Check that infrastructure weight is significant in flood calculation
        assert risk_score > 30
    
    async def test_calculate_fire_risk_population_density(self, db_session, sample_hazards):
        """Test fire risk with high population density."""
        location = Location(
            name="Dense Urban",
            latitude=34.0,
            longitude=-118.0,
            population_density=8000.0,  # Very dense
            building_code_rating=6.0,
            infrastructure_quality=6.0
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        fire = next(h for h in sample_hazards if h.hazard_type == HazardType.FIRE)
        
        service = RiskCalculationService(db_session)
        risk_score, risk_level, confidence, factors, recommendations = \
            await service.calculate_risk(location, fire)
        
        # Population density should have significant impact
        assert factors['population_density_impact'] > 70  # (8000/10000) * 100 = 80
        
        # High density should increase overall risk
        assert risk_score > 35
    
    async def test_risk_level_thresholds(self, db_session, sample_hazards):
        """Test risk level classification thresholds."""
        service = RiskCalculationService(db_session)
        
        assert service._determine_risk_level(10.0) == RiskLevel.LOW
        assert service._determine_risk_level(24.9) == RiskLevel.LOW
        assert service._determine_risk_level(25.0) == RiskLevel.MODERATE
        assert service._determine_risk_level(49.9) == RiskLevel.MODERATE
        assert service._determine_risk_level(50.0) == RiskLevel.HIGH
        assert service._determine_risk_level(74.9) == RiskLevel.HIGH
        assert service._determine_risk_level(75.0) == RiskLevel.CRITICAL
        assert service._determine_risk_level(100.0) == RiskLevel.CRITICAL
    
    async def test_historical_frequency_impact(self, db_session, sample_hazards):
        """Test that historical events increase risk score."""
        location = Location(
            name="Historical Events",
            latitude=35.0,
            longitude=-100.0,
            population_density=2000.0,
            building_code_rating=7.0,
            infrastructure_quality=7.0
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        earthquake = next(h for h in sample_hazards if h.hazard_type == HazardType.EARTHQUAKE)
        
        # Add historical events
        for i in range(5):
            historical = HistoricalData(
                location_id=location.id,
                hazard_id=earthquake.id,
                event_date=datetime.utcnow() - timedelta(days=365 * i),
                severity=6.0,
                casualties=10,
                economic_damage=100000.0
            )
            db_session.add(historical)
        
        await db_session.commit()
        
        service = RiskCalculationService(db_session)
        risk_score, risk_level, confidence, factors, recommendations = \
            await service.calculate_risk(location, earthquake)
        
        # Historical frequency should contribute to risk
        assert factors['historical_frequency_impact'] > 0
        
        # Confidence should be higher with historical data
        assert confidence > 0.5
    
    async def test_custom_risk_factors_override(self, db_session, sample_hazards):
        """Test that custom risk factors override location defaults."""
        location = Location(
            name="Custom Factors Test",
            latitude=40.0,
            longitude=-75.0,
            population_density=1000.0,  # Low
            building_code_rating=8.0,   # High
            infrastructure_quality=8.0  # High
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        storm = next(h for h in sample_hazards if h.hazard_type == HazardType.STORM)
        
        # Override with worse conditions
        custom_factors = {
            'population_density': 9000.0,  # Very high
            'building_code_rating': 2.0,   # Very low
            'infrastructure_quality': 2.0   # Very low
        }
        
        service = RiskCalculationService(db_session)
        risk_score, risk_level, confidence, factors, recommendations = \
            await service.calculate_risk(location, storm, custom_factors)
        
        # Should use custom values
        assert factors['population_density_impact'] > 80  # Based on 9000
        assert factors['building_code_impact'] > 70       # Based on 2.0
        assert factors['infrastructure_impact'] > 70      # Based on 2.0
        
        # Risk should be much higher than with default location values
        assert risk_score > 50
    
    async def test_deterministic_results(self, db_session, sample_hazards):
        """Test that same inputs produce same outputs."""
        location = Location(
            name="Deterministic Test",
            latitude=42.0,
            longitude=-71.0,
            population_density=4000.0,
            building_code_rating=6.5,
            infrastructure_quality=5.5
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        earthquake = next(h for h in sample_hazards if h.hazard_type == HazardType.EARTHQUAKE)
        
        service = RiskCalculationService(db_session)
        
        # Calculate twice
        score1, level1, conf1, factors1, recs1 = \
            await service.calculate_risk(location, earthquake)
        
        score2, level2, conf2, factors2, recs2 = \
            await service.calculate_risk(location, earthquake)
        
        # Should be identical
        assert score1 == score2
        assert level1 == level2
        assert conf1 == conf2
        assert factors1 == factors2
    
    async def test_recommendations_generation(self, db_session, sample_hazards):
        """Test that recommendations are generated appropriately."""
        location = Location(
            name="Recommendation Test",
            latitude=38.0,
            longitude=-122.0,
            population_density=6000.0,
            building_code_rating=3.0,  # Poor
            infrastructure_quality=4.0  # Poor
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        earthquake = next(h for h in sample_hazards if h.hazard_type == HazardType.EARTHQUAKE)
        
        service = RiskCalculationService(db_session)
        risk_score, risk_level, confidence, factors, recommendations = \
            await service.calculate_risk(location, earthquake)
        
        # Should have recommendations
        assert len(recommendations) > 0
        assert len(recommendations) <= 5  # Capped at 5
        
        # Should include hazard-specific recommendations
        recs_text = " ".join(recommendations).lower()
        assert "earthquake" in recs_text or "seismic" in recs_text

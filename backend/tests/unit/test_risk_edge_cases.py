"""Edge case tests for risk calculation service."""
import pytest
from datetime import datetime, timedelta

from app.services import RiskCalculationService
from app.models import Location, Hazard, HazardType, RiskLevel, HistoricalData


@pytest.mark.asyncio
class TestRiskCalculationEdgeCases:
    """Test edge cases and boundary conditions in risk calculations."""
    
    async def test_zero_population_density(self, db_session, sample_hazards):
        """Test risk calculation with zero population density."""
        location = Location(
            name="Unpopulated Area",
            latitude=0.0,
            longitude=0.0,
            population_density=0.0,
            building_code_rating=5.0,
            infrastructure_quality=5.0
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        fire = next(h for h in sample_hazards if h.hazard_type == HazardType.FIRE)
        
        service = RiskCalculationService(db_session)
        risk_score, risk_level, confidence, factors, recommendations = \
            await service.calculate_risk(location, fire)
        
        # Zero population should give zero population impact
        assert factors['population_density_impact'] == 0.0
        assert 0 <= risk_score <= 100
        assert isinstance(risk_level, RiskLevel)
    
    async def test_maximum_population_density(self, db_session, sample_hazards):
        """Test risk calculation with extremely high population density."""
        location = Location(
            name="Ultra Dense City",
            latitude=35.0,
            longitude=139.0,
            population_density=50000.0,  # Far exceeds max normalization
            building_code_rating=5.0,
            infrastructure_quality=5.0
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        fire = next(h for h in sample_hazards if h.hazard_type == HazardType.FIRE)
        
        service = RiskCalculationService(db_session)
        risk_score, risk_level, confidence, factors, recommendations = \
            await service.calculate_risk(location, fire)
        
        # Should cap at 100
        assert factors['population_density_impact'] == 100.0
        assert risk_score <= 100.0
    
    async def test_perfect_building_codes(self, db_session, sample_hazards):
        """Test with perfect building code rating (10.0)."""
        location = Location(
            name="Perfect Standards",
            latitude=40.0,
            longitude=-74.0,
            population_density=5000.0,
            building_code_rating=10.0,  # Maximum
            infrastructure_quality=10.0  # Maximum
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        earthquake = next(h for h in sample_hazards if h.hazard_type == HazardType.EARTHQUAKE)
        
        service = RiskCalculationService(db_session)
        risk_score, risk_level, confidence, factors, recommendations = \
            await service.calculate_risk(location, earthquake)
        
        # Perfect codes should give zero impact
        assert factors['building_code_impact'] == 0.0
        assert factors['infrastructure_impact'] == 0.0
        
        # Overall risk should be lower
        assert risk_score < 50.0
    
    async def test_worst_case_scenario(self, db_session, sample_hazards):
        """Test worst possible conditions."""
        location = Location(
            name="Worst Case",
            latitude=34.0,
            longitude=-118.0,
            population_density=10000.0,  # Maximum normalized
            building_code_rating=0.0,    # Worst
            infrastructure_quality=0.0   # Worst
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        earthquake = next(h for h in sample_hazards if h.hazard_type == HazardType.EARTHQUAKE)
        
        service = RiskCalculationService(db_session)
        risk_score, risk_level, confidence, factors, recommendations = \
            await service.calculate_risk(location, earthquake)
        
        # All impacts should be at maximum
        assert factors['building_code_impact'] == 100.0
        assert factors['infrastructure_impact'] == 100.0
        
        # Should be critical risk
        assert risk_level == RiskLevel.CRITICAL
        assert risk_score >= 75.0
    
    async def test_negative_values_rejected(self, db_session):
        """Test that negative values are handled by Pydantic validation."""
        # This is handled at the schema level, not model level
        from pydantic import ValidationError
        from app.schemas import LocationCreate
        
        # Negative population should fail validation
        with pytest.raises(ValidationError):
            LocationCreate(
                name="Invalid",
                latitude=0.0,
                longitude=0.0,
                population_density=-100.0
            )
    
    async def test_no_historical_data(self, db_session, sample_hazards):
        """Test confidence calculation with no historical data."""
        location = Location(
            name="No History",
            latitude=45.0,
            longitude=-93.0,
            population_density=3000.0,
            building_code_rating=6.0,
            infrastructure_quality=6.0
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        storm = next(h for h in sample_hazards if h.hazard_type == HazardType.STORM)
        
        service = RiskCalculationService(db_session)
        risk_score, risk_level, confidence, factors, recommendations = \
            await service.calculate_risk(location, storm)
        
        # No historical data means base confidence only
        assert confidence == 0.5
        assert factors['historical_frequency_impact'] == 0.0
    
    async def test_many_historical_events(self, db_session, sample_hazards):
        """Test with excessive historical events (>10)."""
        location = Location(
            name="Disaster Prone",
            latitude=25.0,
            longitude=-80.0,
            population_density=4000.0,
            building_code_rating=6.0,
            infrastructure_quality=6.0
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        flood = next(h for h in sample_hazards if h.hazard_type == HazardType.FLOOD)
        
        # Add 20 historical events
        for i in range(20):
            historical = HistoricalData(
                location_id=location.id,
                hazard_id=flood.id,
                event_date=datetime.utcnow() - timedelta(days=180 * i),
                severity=7.0,
                casualties=50,
                economic_damage=1000000.0
            )
            db_session.add(historical)
        
        await db_session.commit()
        
        service = RiskCalculationService(db_session)
        risk_score, risk_level, confidence, factors, recommendations = \
            await service.calculate_risk(location, flood)
        
        # Should cap frequency impact at 100
        assert factors['historical_frequency_impact'] == 100.0
        
        # Confidence should be capped at 1.0
        assert confidence <= 1.0
        assert confidence >= 0.9  # Should be very high
    
    async def test_old_historical_events_excluded(self, db_session, sample_hazards):
        """Test that events older than 10 years are excluded."""
        location = Location(
            name="Old Events",
            latitude=48.0,
            longitude=-122.0,
            population_density=2000.0,
            building_code_rating=7.0,
            infrastructure_quality=7.0
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        earthquake = next(h for h in sample_hazards if h.hazard_type == HazardType.EARTHQUAKE)
        
        # Add old events (>10 years)
        for i in range(15, 25):
            historical = HistoricalData(
                location_id=location.id,
                hazard_id=earthquake.id,
                event_date=datetime.utcnow() - timedelta(days=365 * i),
                severity=6.0,
                casualties=10,
                economic_damage=500000.0
            )
            db_session.add(historical)
        
        await db_session.commit()
        
        service = RiskCalculationService(db_session)
        risk_score, risk_level, confidence, factors, recommendations = \
            await service.calculate_risk(location, earthquake)
        
        # Old events shouldn't affect frequency calculation
        assert factors['historical_frequency_impact'] == 0.0
    
    async def test_location_with_extra_data(self, db_session, sample_hazards):
        """Test confidence boost from extra_data."""
        location = Location(
            name="Detailed Location",
            latitude=33.0,
            longitude=-117.0,
            population_density=3500.0,
            building_code_rating=7.5,
            infrastructure_quality=7.0,
            extra_data={"state": "California", "region": "Southern"}
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        fire = next(h for h in sample_hazards if h.hazard_type == HazardType.FIRE)
        
        service = RiskCalculationService(db_session)
        risk_score, risk_level, confidence, factors, recommendations = \
            await service.calculate_risk(location, fire)
        
        # Should get 0.1 boost from extra_data
        assert confidence >= 0.6  # 0.5 base + 0.1 metadata
    
    async def test_all_hazard_types_coverage(self, db_session, sample_hazards):
        """Test all hazard types produce valid results."""
        location = Location(
            name="All Hazards Test",
            latitude=36.0,
            longitude=-115.0,
            population_density=4500.0,
            building_code_rating=6.5,
            infrastructure_quality=6.0
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        service = RiskCalculationService(db_session)
        
        for hazard in sample_hazards:
            risk_score, risk_level, confidence, factors, recommendations = \
                await service.calculate_risk(location, hazard)
            
            # All should produce valid results
            assert 0 <= risk_score <= 100
            assert isinstance(risk_level, RiskLevel)
            assert 0 <= confidence <= 1
            assert len(factors) == 5
            assert isinstance(recommendations, list)
    
    async def test_risk_score_boundaries(self, db_session, sample_hazards):
        """Test risk score boundary values for level classification."""
        service = RiskCalculationService(db_session)
        
        # Test exact boundary values
        assert service._determine_risk_level(0.0) == RiskLevel.LOW
        assert service._determine_risk_level(24.99) == RiskLevel.LOW
        assert service._determine_risk_level(25.0) == RiskLevel.MODERATE
        assert service._determine_risk_level(49.99) == RiskLevel.MODERATE
        assert service._determine_risk_level(50.0) == RiskLevel.HIGH
        assert service._determine_risk_level(74.99) == RiskLevel.HIGH
        assert service._determine_risk_level(75.0) == RiskLevel.CRITICAL
        assert service._determine_risk_level(99.99) == RiskLevel.CRITICAL
        assert service._determine_risk_level(100.0) == RiskLevel.CRITICAL
    
    async def test_recommendations_count_limit(self, db_session, sample_hazards):
        """Test that recommendations are capped at 5."""
        location = Location(
            name="Many Issues",
            latitude=39.0,
            longitude=-84.0,
            population_density=9500.0,   # High - triggers recommendation
            building_code_rating=1.0,    # Very low - triggers recommendation
            infrastructure_quality=1.0   # Very low - triggers recommendation
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        earthquake = next(h for h in sample_hazards if h.hazard_type == HazardType.EARTHQUAKE)
        
        service = RiskCalculationService(db_session)
        risk_score, risk_level, confidence, factors, recommendations = \
            await service.calculate_risk(location, earthquake)
        
        # Should be capped at 5 even with many issues
        assert len(recommendations) <= 5
        assert len(recommendations) > 0
    
    async def test_critical_risk_recommendations(self, db_session, sample_hazards):
        """Test that critical risk generates evacuation recommendation."""
        location = Location(
            name="Critical Area",
            latitude=37.0,
            longitude=-121.0,
            population_density=9000.0,
            building_code_rating=1.0,
            infrastructure_quality=1.0
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        earthquake = next(h for h in sample_hazards if h.hazard_type == HazardType.EARTHQUAKE)
        
        service = RiskCalculationService(db_session)
        risk_score, risk_level, confidence, factors, recommendations = \
            await service.calculate_risk(location, earthquake)
        
        if risk_level == RiskLevel.CRITICAL:
            recs_text = " ".join(recommendations).lower()
            assert "evacuation" in recs_text or "critical" in recs_text
    
    async def test_custom_factors_none(self, db_session, sample_hazards):
        """Test with explicitly None custom factors."""
        location = Location(
            name="Default Factors",
            latitude=41.0,
            longitude=-87.0,
            population_density=3000.0,
            building_code_rating=7.0,
            infrastructure_quality=6.5
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        storm = next(h for h in sample_hazards if h.hazard_type == HazardType.STORM)
        
        service = RiskCalculationService(db_session)
        risk_score, risk_level, confidence, factors, recommendations = \
            await service.calculate_risk(location, storm, custom_factors=None)
        
        # Should use location defaults
        assert factors['population_density_impact'] == pytest.approx((3000 / 10000) * 100, rel=0.01)
    
    async def test_partial_custom_factors(self, db_session, sample_hazards):
        """Test with partial custom factor override."""
        location = Location(
            name="Partial Override",
            latitude=43.0,
            longitude=-79.0,
            population_density=5000.0,
            building_code_rating=8.0,
            infrastructure_quality=7.0
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        flood = next(h for h in sample_hazards if h.hazard_type == HazardType.FLOOD)
        
        # Only override one factor
        custom_factors = {
            'infrastructure_quality': 2.0  # Override only this
        }
        
        service = RiskCalculationService(db_session)
        risk_score, risk_level, confidence, factors, recommendations = \
            await service.calculate_risk(location, flood, custom_factors)
        
        # Should use custom infrastructure, defaults for others
        assert factors['infrastructure_impact'] > 70  # 100 - (2.0 * 10) = 80
        assert factors['population_density_impact'] == pytest.approx((5000 / 10000) * 100, rel=0.01)

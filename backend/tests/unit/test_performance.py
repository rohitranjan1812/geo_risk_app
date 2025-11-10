"""Performance tests for risk calculation service."""
import pytest
import asyncio
from datetime import datetime, timedelta
import time

from app.services import RiskCalculationService
from app.models import Location, Hazard, HazardType, HistoricalData


@pytest.mark.asyncio
class TestRiskCalculationPerformance:
    """Test performance characteristics of risk calculations."""
    
    async def test_single_risk_calculation_performance(self, db_session, sample_hazards):
        """Test that single risk calculation completes quickly."""
        location = Location(
            name="Performance Test",
            latitude=37.7749,
            longitude=-122.4194,
            population_density=5000.0,
            building_code_rating=7.0,
            infrastructure_quality=6.5
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        earthquake = next(h for h in sample_hazards if h.hazard_type == HazardType.EARTHQUAKE)
        
        service = RiskCalculationService(db_session)
        
        start_time = time.time()
        risk_score, risk_level, confidence, factors, recommendations = \
            await service.calculate_risk(location, earthquake)
        elapsed = time.time() - start_time
        
        # Should complete in under 500ms
        assert elapsed < 0.5, f"Risk calculation took {elapsed*1000:.2f}ms, expected <500ms"
        assert risk_score > 0
    
    async def test_multiple_sequential_calculations_performance(self, db_session, sample_hazards):
        """Test performance of multiple sequential calculations."""
        location = Location(
            name="Sequential Test",
            latitude=40.7128,
            longitude=-74.0060,
            population_density=8000.0,
            building_code_rating=6.0,
            infrastructure_quality=5.5
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        service = RiskCalculationService(db_session)
        
        start_time = time.time()
        for hazard in sample_hazards:
            risk_score, risk_level, confidence, factors, recommendations = \
                await service.calculate_risk(location, hazard)
            assert 0 <= risk_score <= 100
        elapsed = time.time() - start_time
        
        # 4 hazards should complete in under 2 seconds
        assert elapsed < 2.0, f"4 calculations took {elapsed*1000:.2f}ms, expected <2000ms"
    
    async def test_parallel_calculations_performance(self, db_session, sample_hazards):
        """Test performance of parallel risk calculations."""
        # Create multiple locations
        locations = []
        for i in range(5):
            location = Location(
                name=f"Parallel Test {i}",
                latitude=35.0 + i,
                longitude=-95.0 + i,
                population_density=3000.0 + i * 500,
                building_code_rating=5.0 + i * 0.5,
                infrastructure_quality=5.0 + i * 0.5
            )
            db_session.add(location)
            locations.append(location)
        
        await db_session.commit()
        for loc in locations:
            await db_session.refresh(loc)
        
        service = RiskCalculationService(db_session)
        
        start_time = time.time()
        
        # Run calculations in parallel
        tasks = []
        for location in locations:
            for hazard in sample_hazards:
                tasks.append(service.calculate_risk(location, hazard))
        
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start_time
        
        # 20 parallel calculations (5 locations × 4 hazards) should complete reasonably fast
        assert len(results) == 20
        assert elapsed < 3.0, f"20 parallel calculations took {elapsed*1000:.2f}ms, expected <3000ms"
    
    async def test_calculation_with_large_historical_dataset(self, db_session, sample_hazards):
        """Test performance with large amount of historical data."""
        location = Location(
            name="Large History Test",
            latitude=29.7604,
            longitude=-95.3698,
            population_density=4500.0,
            building_code_rating=6.5,
            infrastructure_quality=6.0
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        flood = next(h for h in sample_hazards if h.hazard_type == HazardType.FLOOD)
        
        # Add 100 historical events
        for i in range(100):
            historical = HistoricalData(
                location_id=location.id,
                hazard_id=flood.id,
                event_date=datetime.utcnow() - timedelta(days=i * 30),
                severity=5.0 + (i % 5),
                casualties=10 * (i % 10),
                economic_damage=100000.0 * (i % 20)
            )
            db_session.add(historical)
        
        await db_session.commit()
        
        service = RiskCalculationService(db_session)
        
        start_time = time.time()
        risk_score, risk_level, confidence, factors, recommendations = \
            await service.calculate_risk(location, flood)
        elapsed = time.time() - start_time
        
        # Should still complete quickly even with 100 historical events
        assert elapsed < 0.5, f"Calculation with 100 events took {elapsed*1000:.2f}ms, expected <500ms"
        assert confidence > 0.8  # Should have high confidence with lots of data
    
    async def test_repeated_calculations_consistency(self, db_session, sample_hazards):
        """Test that repeated calculations maintain performance and consistency."""
        location = Location(
            name="Consistency Test",
            latitude=34.0522,
            longitude=-118.2437,
            population_density=6000.0,
            building_code_rating=7.5,
            infrastructure_quality=7.0
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        fire = next(h for h in sample_hazards if h.hazard_type == HazardType.FIRE)
        
        service = RiskCalculationService(db_session)
        
        # Run 10 times and track performance
        times = []
        scores = []
        
        for _ in range(10):
            start_time = time.time()
            risk_score, risk_level, confidence, factors, recommendations = \
                await service.calculate_risk(location, fire)
            elapsed = time.time() - start_time
            
            times.append(elapsed)
            scores.append(risk_score)
        
        # All times should be under 500ms
        assert max(times) < 0.5, f"Max time {max(times)*1000:.2f}ms exceeded 500ms"
        
        # All scores should be identical (deterministic)
        assert len(set(scores)) == 1, "Scores varied across repeated calculations"
    
    async def test_custom_factors_performance_impact(self, db_session, sample_hazards):
        """Test performance impact of using custom factors."""
        location = Location(
            name="Custom Factors Test",
            latitude=36.0,
            longitude=-115.0,
            population_density=4000.0,
            building_code_rating=6.0,
            infrastructure_quality=6.0
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        storm = next(h for h in sample_hazards if h.hazard_type == HazardType.STORM)
        
        service = RiskCalculationService(db_session)
        
        # Test without custom factors
        start_time = time.time()
        score1, _, _, _, _ = await service.calculate_risk(location, storm)
        time_without_custom = time.time() - start_time
        
        # Test with custom factors
        custom_factors = {
            'population_density': 8000.0,
            'building_code_rating': 4.0,
            'infrastructure_quality': 5.0
        }
        
        start_time = time.time()
        score2, _, _, _, _ = await service.calculate_risk(location, storm, custom_factors)
        time_with_custom = time.time() - start_time
        
        # Both should be fast
        assert time_without_custom < 0.5
        assert time_with_custom < 0.5
        
        # Custom factors should not significantly impact performance
        assert abs(time_with_custom - time_without_custom) < 0.1
    
    async def test_recommendation_generation_performance(self, db_session, sample_hazards):
        """Test that recommendation generation doesn't significantly impact performance."""
        # Location with many issues (will generate max recommendations)
        location = Location(
            name="Many Issues",
            latitude=39.0,
            longitude=-84.0,
            population_density=9500.0,
            building_code_rating=1.0,
            infrastructure_quality=1.0
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        earthquake = next(h for h in sample_hazards if h.hazard_type == HazardType.EARTHQUAKE)
        
        service = RiskCalculationService(db_session)
        
        start_time = time.time()
        risk_score, risk_level, confidence, factors, recommendations = \
            await service.calculate_risk(location, earthquake)
        elapsed = time.time() - start_time
        
        # Should still be fast even with max recommendations
        assert elapsed < 0.5
        assert len(recommendations) > 0
        assert len(recommendations) <= 5


@pytest.mark.asyncio
class TestDatabasePerformance:
    """Test database query performance."""
    
    async def test_historical_data_query_performance(self, db_session, sample_hazards):
        """Test performance of historical data queries."""
        location = Location(
            name="DB Query Test",
            latitude=32.0,
            longitude=-96.0,
            population_density=3500.0,
            building_code_rating=6.5,
            infrastructure_quality=6.5
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)
        
        earthquake = sample_hazards[0]
        
        # Add many historical events
        for i in range(50):
            historical = HistoricalData(
                location_id=location.id,
                hazard_id=earthquake.id,
                event_date=datetime.utcnow() - timedelta(days=i * 20),
                severity=5.0 + (i % 5),
                casualties=5 * i,
                economic_damage=50000.0 * i
            )
            db_session.add(historical)
        
        await db_session.commit()
        
        service = RiskCalculationService(db_session)
        
        start_time = time.time()
        # This will query historical data
        confidence = await service._calculate_confidence(location, earthquake)
        elapsed = time.time() - start_time
        
        # Query should be fast even with 50 records
        assert elapsed < 0.1, f"Historical query took {elapsed*1000:.2f}ms, expected <100ms"
        assert confidence > 0.5
    
    async def test_concurrent_database_access(self, db_session, sample_hazards):
        """Test concurrent database access performance."""
        # Create multiple locations
        locations = []
        for i in range(10):
            location = Location(
                name=f"Concurrent Test {i}",
                latitude=30.0 + i,
                longitude=-90.0 + i,
                population_density=2000.0 + i * 200,
                building_code_rating=5.0 + i * 0.2,
                infrastructure_quality=5.0 + i * 0.2
            )
            db_session.add(location)
            locations.append(location)
        
        await db_session.commit()
        for loc in locations:
            await db_session.refresh(loc)
        
        service = RiskCalculationService(db_session)
        hazard = sample_hazards[0]
        
        start_time = time.time()
        
        # Run concurrent calculations
        tasks = [service.calculate_risk(loc, hazard) for loc in locations]
        results = await asyncio.gather(*tasks)
        
        elapsed = time.time() - start_time
        
        # 10 concurrent calculations should complete reasonably
        assert len(results) == 10
        assert elapsed < 2.0, f"10 concurrent calculations took {elapsed*1000:.2f}ms"

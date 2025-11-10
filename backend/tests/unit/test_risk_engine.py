"""
Unit tests for risk assessment algorithms.

Tests cover:
- Geographic utility functions (distance calculation, proximity impact)
- Individual hazard algorithms (earthquake, flood, fire, storm)
- Composite risk aggregation
- Edge cases and boundary conditions
- Performance benchmarks
"""
import pytest
import time
from typing import List

from app.services.risk_engine import (
    RiskEngine,
    GeographicPoint,
    HazardSource,
    HistoricalEvent,
    AssessmentConfig,
    ProximityDecayModel
)
from app.models import HazardType, RiskLevel


class TestGeographicUtilities:
    """Test geographic calculation utilities."""
    
    def test_geographic_point_validation(self):
        """Test coordinate validation."""
        # Valid coordinates
        point = GeographicPoint(37.7749, -122.4194)
        assert point.latitude == 37.7749
        assert point.longitude == -122.4194
        
        # Invalid latitude
        with pytest.raises(ValueError, match="Invalid latitude"):
            GeographicPoint(91.0, -122.0)
        
        with pytest.raises(ValueError, match="Invalid latitude"):
            GeographicPoint(-91.0, -122.0)
        
        # Invalid longitude
        with pytest.raises(ValueError, match="Invalid longitude"):
            GeographicPoint(37.0, 181.0)
        
        with pytest.raises(ValueError, match="Invalid longitude"):
            GeographicPoint(37.0, -181.0)
    
    def test_distance_calculation_known_cities(self):
        """Test distance calculation with known city pairs."""
        engine = RiskEngine()
        
        # San Francisco to Los Angeles (~559 km)
        sf = GeographicPoint(37.7749, -122.4194)
        la = GeographicPoint(34.0522, -118.2437)
        distance = engine.calculate_distance_km(sf, la)
        assert 550 < distance < 570, f"Expected ~559km, got {distance}km"
        
        # New York to Boston (~306 km)
        ny = GeographicPoint(40.7128, -74.0060)
        boston = GeographicPoint(42.3601, -71.0589)
        distance = engine.calculate_distance_km(ny, boston)
        assert 300 < distance < 320, f"Expected ~306km, got {distance}km"
        
        # Same location (0 km)
        distance = engine.calculate_distance_km(sf, sf)
        assert distance == 0.0
    
    def test_distance_calculation_caching(self):
        """Test that distance calculations are cached."""
        engine = RiskEngine()
        
        p1 = GeographicPoint(37.7749, -122.4194)
        p2 = GeographicPoint(34.0522, -118.2437)
        
        # First calculation
        distance1 = engine.calculate_distance_km(p1, p2)
        
        # Second calculation (should use cache)
        distance2 = engine.calculate_distance_km(p1, p2)
        
        assert distance1 == distance2
        assert len(engine._distance_cache) == 1
        
        # Clear cache and verify
        engine.clear_cache()
        assert len(engine._distance_cache) == 0
    
    def test_proximity_impact_linear_decay(self):
        """Test linear proximity decay model."""
        engine = RiskEngine()
        
        # At source (0 km): maximum impact
        impact = engine.calculate_proximity_impact(0, 100, ProximityDecayModel.LINEAR)
        assert impact == 1.0
        
        # Halfway (50 km): 50% impact
        impact = engine.calculate_proximity_impact(50, 100, ProximityDecayModel.LINEAR)
        assert abs(impact - 0.5) < 0.01
        
        # At max distance (100 km): no impact
        impact = engine.calculate_proximity_impact(100, 100, ProximityDecayModel.LINEAR)
        assert impact == 0.0
        
        # Beyond max distance: no impact
        impact = engine.calculate_proximity_impact(150, 100, ProximityDecayModel.LINEAR)
        assert impact == 0.0
    
    def test_proximity_impact_exponential_decay(self):
        """Test exponential proximity decay model."""
        engine = RiskEngine()
        
        # At source: maximum impact
        impact = engine.calculate_proximity_impact(0, 100, ProximityDecayModel.EXPONENTIAL)
        assert impact == 1.0
        
        # Exponential decay (e^-3x) decays faster than linear
        impact_50km = engine.calculate_proximity_impact(50, 100, ProximityDecayModel.EXPONENTIAL)
        linear_50km = engine.calculate_proximity_impact(50, 100, ProximityDecayModel.LINEAR)
        assert impact_50km < linear_50km  # Exponential decays faster
        
        # At max distance: small but non-zero
        impact = engine.calculate_proximity_impact(100, 100, ProximityDecayModel.EXPONENTIAL)
        assert 0 <= impact < 0.1
    
    def test_proximity_impact_inverse_square_decay(self):
        """Test inverse square proximity decay model."""
        engine = RiskEngine()
        
        # At source: maximum impact
        impact = engine.calculate_proximity_impact(0, 100, ProximityDecayModel.INVERSE_SQUARE)
        assert impact == 1.0
        
        # Inverse square decay
        impact = engine.calculate_proximity_impact(50, 100, ProximityDecayModel.INVERSE_SQUARE)
        assert 0 < impact < 1.0
        
        # At max distance: no impact
        impact = engine.calculate_proximity_impact(100, 100, ProximityDecayModel.INVERSE_SQUARE)
        assert impact == 0.0


class TestSeismicRiskAlgorithm:
    """Test earthquake risk assessment algorithm."""
    
    def test_seismic_risk_basic_calculation(self):
        """Test basic seismic risk calculation."""
        engine = RiskEngine()
        
        # San Francisco near San Andreas Fault
        location = GeographicPoint(37.7749, -122.4194)
        fault = HazardSource(
            location=GeographicPoint(37.7, -122.5),  # ~10km away
            intensity=8.0,  # High magnitude potential
            influence_radius_km=100
        )
        
        score, breakdown = engine.calculate_seismic_risk(
            location=location,
            fault_lines=[fault],
            historical_events=[],
            soil_amplification=1.0,
            building_code_rating=5.0
        )
        
        # Verify score is within valid range
        assert 0 <= score <= 100
        
        # Verify breakdown contains expected components
        assert 'fault_proximity_score' in breakdown
        assert 'historical_score' in breakdown
        assert 'magnitude_score' in breakdown
        assert 'soil_amplification' in breakdown
        assert 'building_code_mitigation' in breakdown
        assert 'calculation_time_ms' in breakdown
        
        # Near major fault should have elevated risk
        assert score > 30
    
    def test_seismic_risk_with_historical_events(self):
        """Test seismic risk with historical earthquake data."""
        engine = RiskEngine()
        
        location = GeographicPoint(37.7749, -122.4194)
        fault = HazardSource(
            location=GeographicPoint(37.7, -122.5),
            intensity=8.0,
            influence_radius_km=100
        )
        
        # Add historical events
        events = [
            HistoricalEvent(severity=6.9, days_ago=365*30, impact_radius_km=50),  # 1989 Loma Prieta
            HistoricalEvent(severity=7.9, days_ago=365*115, impact_radius_km=100)  # 1906 SF
        ]
        
        score_with_history, _ = engine.calculate_seismic_risk(
            location, [fault], events, 1.0, 5.0
        )
        
        score_without_history, _ = engine.calculate_seismic_risk(
            location, [fault], [], 1.0, 5.0
        )
        
        # Historical events should increase risk
        assert score_with_history >= score_without_history
    
    def test_seismic_risk_soil_amplification(self):
        """Test soil amplification effect on seismic risk."""
        engine = RiskEngine()
        
        location = GeographicPoint(37.7749, -122.4194)
        fault = HazardSource(
            location=GeographicPoint(37.7, -122.5),
            intensity=8.0,
            influence_radius_km=100
        )
        
        # Rock soil (no amplification)
        score_rock, _ = engine.calculate_seismic_risk(
            location, [fault], [], soil_amplification=1.0, building_code_rating=5.0
        )
        
        # Soft soil (2x amplification)
        score_soft, _ = engine.calculate_seismic_risk(
            location, [fault], [], soil_amplification=2.0, building_code_rating=5.0
        )
        
        # Soft soil should increase risk
        assert score_soft > score_rock
    
    def test_seismic_risk_building_code_mitigation(self):
        """Test building code mitigation effect."""
        engine = RiskEngine()
        
        location = GeographicPoint(37.7749, -122.4194)
        fault = HazardSource(
            location=GeographicPoint(37.7, -122.5),
            intensity=8.0,
            influence_radius_km=100
        )
        
        # Poor building codes
        score_poor, _ = engine.calculate_seismic_risk(
            location, [fault], [], 1.0, building_code_rating=0.0
        )
        
        # Excellent building codes
        score_excellent, _ = engine.calculate_seismic_risk(
            location, [fault], [], 1.0, building_code_rating=10.0
        )
        
        # Better building codes should reduce risk
        assert score_excellent < score_poor
    
    def test_seismic_risk_edge_case_no_faults(self):
        """Test seismic risk with no fault lines."""
        engine = RiskEngine()
        
        location = GeographicPoint(37.7749, -122.4194)
        
        score, breakdown = engine.calculate_seismic_risk(
            location, fault_lines=[], historical_events=[], soil_amplification=1.0, building_code_rating=5.0
        )
        
        # Should return low risk but not crash
        assert score >= 0
        assert score < 50  # Should be relatively low without faults


class TestFloodRiskAlgorithm:
    """Test flood risk assessment algorithm."""
    
    def test_flood_risk_basic_calculation(self):
        """Test basic flood risk calculation."""
        engine = RiskEngine()
        
        # Houston (prone to flooding, low elevation)
        location = GeographicPoint(29.7604, -95.3698)
        water_body = HazardSource(
            location=GeographicPoint(29.76, -95.35),  # Buffalo Bayou
            intensity=7.0,
            influence_radius_km=10
        )
        
        score, breakdown = engine.calculate_flood_risk(
            location=location,
            elevation_meters=15,  # Low elevation
            water_bodies=[water_body],
            historical_events=[],
            drainage_quality=6.0,
            annual_rainfall_mm=1200
        )
        
        assert 0 <= score <= 100
        assert 'elevation_score' in breakdown
        assert 'water_proximity_score' in breakdown
        assert 'drainage_score' in breakdown
        assert 'rainfall_factor' in breakdown
    
    def test_flood_risk_elevation_impact(self):
        """Test elevation impact on flood risk."""
        engine = RiskEngine()
        
        location = GeographicPoint(29.7604, -95.3698)
        water_body = HazardSource(
            location=GeographicPoint(29.76, -95.35),
            intensity=7.0,
            influence_radius_km=10
        )
        
        # Sea level location
        score_low, _ = engine.calculate_flood_risk(
            location, elevation_meters=0, water_bodies=[water_body],
            historical_events=[], drainage_quality=5.0
        )
        
        # Elevated location
        score_high, _ = engine.calculate_flood_risk(
            location, elevation_meters=100, water_bodies=[water_body],
            historical_events=[], drainage_quality=5.0
        )
        
        # Higher elevation should reduce flood risk
        assert score_high < score_low
    
    def test_flood_risk_drainage_quality(self):
        """Test drainage quality impact."""
        engine = RiskEngine()
        
        location = GeographicPoint(29.7604, -95.3698)
        
        # Poor drainage
        score_poor, _ = engine.calculate_flood_risk(
            location, elevation_meters=15, water_bodies=[],
            historical_events=[], drainage_quality=0.0
        )
        
        # Excellent drainage
        score_excellent, _ = engine.calculate_flood_risk(
            location, elevation_meters=15, water_bodies=[],
            historical_events=[], drainage_quality=10.0
        )
        
        # Better drainage should reduce risk
        assert score_excellent < score_poor
    
    def test_flood_risk_rainfall_impact(self):
        """Test rainfall impact on flood risk."""
        engine = RiskEngine()
        
        location = GeographicPoint(29.7604, -95.3698)
        
        # Low rainfall
        score_low_rain, _ = engine.calculate_flood_risk(
            location, elevation_meters=15, water_bodies=[],
            historical_events=[], drainage_quality=5.0, annual_rainfall_mm=500
        )
        
        # High rainfall
        score_high_rain, _ = engine.calculate_flood_risk(
            location, elevation_meters=15, water_bodies=[],
            historical_events=[], drainage_quality=5.0, annual_rainfall_mm=3000
        )
        
        # Higher rainfall should increase risk
        assert score_high_rain > score_low_rain


class TestWildfireRiskAlgorithm:
    """Test wildfire risk assessment algorithm."""
    
    def test_wildfire_risk_basic_calculation(self):
        """Test basic wildfire risk calculation."""
        engine = RiskEngine()
        
        # Los Angeles area
        location = GeographicPoint(34.0522, -118.2437)
        
        score, breakdown = engine.calculate_wildfire_risk(
            location=location,
            vegetation_density=7.0,  # Dense chaparral
            climate_aridity_index=8.0,  # Dry climate
            historical_events=[],
            fire_sources=[],
            temperature_avg_c=22,
            wind_speed_kmh=15
        )
        
        assert 0 <= score <= 100
        assert 'vegetation_score' in breakdown
        assert 'climate_score' in breakdown
        assert 'temperature_factor' in breakdown
        assert 'wind_factor' in breakdown
    
    def test_wildfire_risk_vegetation_density(self):
        """Test vegetation density impact."""
        engine = RiskEngine()
        
        location = GeographicPoint(34.0522, -118.2437)
        
        # Low vegetation (desert)
        score_low_veg, _ = engine.calculate_wildfire_risk(
            location, vegetation_density=1.0, climate_aridity_index=5.0,
            historical_events=[], fire_sources=[]
        )
        
        # High vegetation (forest)
        score_high_veg, _ = engine.calculate_wildfire_risk(
            location, vegetation_density=10.0, climate_aridity_index=5.0,
            historical_events=[], fire_sources=[]
        )
        
        # Higher vegetation increases fire risk
        assert score_high_veg > score_low_veg
    
    def test_wildfire_risk_temperature_factor(self):
        """Test temperature impact on wildfire risk."""
        engine = RiskEngine()
        
        location = GeographicPoint(34.0522, -118.2437)
        
        # Cool temperature
        score_cool, _ = engine.calculate_wildfire_risk(
            location, vegetation_density=5.0, climate_aridity_index=5.0,
            historical_events=[], fire_sources=[],
            temperature_avg_c=15, wind_speed_kmh=10
        )
        
        # Hot temperature
        score_hot, _ = engine.calculate_wildfire_risk(
            location, vegetation_density=5.0, climate_aridity_index=5.0,
            historical_events=[], fire_sources=[],
            temperature_avg_c=35, wind_speed_kmh=10
        )
        
        # Higher temperature increases risk
        assert score_hot > score_cool
    
    def test_wildfire_risk_wind_factor(self):
        """Test wind speed impact."""
        engine = RiskEngine()
        
        location = GeographicPoint(34.0522, -118.2437)
        
        # Low wind
        score_low_wind, _ = engine.calculate_wildfire_risk(
            location, vegetation_density=5.0, climate_aridity_index=5.0,
            historical_events=[], fire_sources=[],
            temperature_avg_c=25, wind_speed_kmh=5
        )
        
        # High wind
        score_high_wind, _ = engine.calculate_wildfire_risk(
            location, vegetation_density=5.0, climate_aridity_index=5.0,
            historical_events=[], fire_sources=[],
            temperature_avg_c=25, wind_speed_kmh=50
        )
        
        # Higher wind increases risk
        assert score_high_wind > score_low_wind
    
    def test_wildfire_risk_active_fire_proximity(self):
        """Test proximity to active fires."""
        engine = RiskEngine()
        
        location = GeographicPoint(34.0522, -118.2437)
        
        # No nearby fires
        score_no_fires, _ = engine.calculate_wildfire_risk(
            location, vegetation_density=5.0, climate_aridity_index=5.0,
            historical_events=[], fire_sources=[]
        )
        
        # Nearby active fire
        active_fire = HazardSource(
            location=GeographicPoint(34.1, -118.3),
            intensity=8.0,
            influence_radius_km=20
        )
        score_with_fire, _ = engine.calculate_wildfire_risk(
            location, vegetation_density=5.0, climate_aridity_index=5.0,
            historical_events=[], fire_sources=[active_fire]
        )
        
        # Nearby fire should increase risk
        assert score_with_fire > score_no_fires


class TestStormRiskAlgorithm:
    """Test storm risk assessment algorithm."""
    
    def test_storm_risk_basic_calculation(self):
        """Test basic storm risk calculation."""
        engine = RiskEngine()
        
        # Miami (hurricane-prone)
        location = GeographicPoint(25.7617, -80.1918)
        
        events = [
            HistoricalEvent(severity=8.0, days_ago=365*5, impact_radius_km=200),
            HistoricalEvent(severity=6.0, days_ago=365*2, impact_radius_km=150)
        ]
        
        score, breakdown = engine.calculate_storm_risk(
            location=location,
            historical_events=events,
            coastal_distance_km=5,
            elevation_meters=2,
            current_season_index=8,  # September (peak hurricane season)
            geographic_exposure=9.0
        )
        
        assert 0 <= score <= 100
        assert 'historical_score' in breakdown
        assert 'exposure_score' in breakdown
        assert 'seasonal_factor' in breakdown
        assert 'coastal_factor' in breakdown
    
    def test_storm_risk_seasonal_variation(self):
        """Test seasonal factors in storm risk."""
        engine = RiskEngine()
        
        location = GeographicPoint(25.7617, -80.1918)
        events = [HistoricalEvent(severity=7.0, days_ago=365, impact_radius_km=150)]
        
        # Off-season (January)
        score_winter, breakdown_winter = engine.calculate_storm_risk(
            location, events, coastal_distance_km=5, elevation_meters=2,
            current_season_index=0, geographic_exposure=8.0
        )
        
        # Peak season (September)
        score_peak, breakdown_peak = engine.calculate_storm_risk(
            location, events, coastal_distance_km=5, elevation_meters=2,
            current_season_index=8, geographic_exposure=8.0
        )
        
        # Peak season should have higher risk
        assert breakdown_peak['seasonal_factor'] > breakdown_winter['seasonal_factor']
    
    def test_storm_risk_coastal_proximity(self):
        """Test coastal proximity impact."""
        engine = RiskEngine()
        
        location = GeographicPoint(25.7617, -80.1918)
        events = [HistoricalEvent(severity=7.0, days_ago=365, impact_radius_km=150)]
        
        # Coastal location
        score_coastal, breakdown_coastal = engine.calculate_storm_risk(
            location, events, coastal_distance_km=0, elevation_meters=5,
            current_season_index=8, geographic_exposure=8.0
        )
        
        # Inland location
        score_inland, breakdown_inland = engine.calculate_storm_risk(
            location, events, coastal_distance_km=100, elevation_meters=5,
            current_season_index=8, geographic_exposure=8.0
        )
        
        # Coastal should have higher factor
        assert breakdown_coastal['coastal_factor'] > breakdown_inland['coastal_factor']
    
    def test_storm_risk_historical_frequency(self):
        """Test historical event frequency impact."""
        engine = RiskEngine()
        
        location = GeographicPoint(25.7617, -80.1918)
        
        # Few historical events (old)
        few_events = [
            HistoricalEvent(severity=6.0, days_ago=365*10, impact_radius_km=150)
        ]
        score_few, _ = engine.calculate_storm_risk(
            location, few_events, coastal_distance_km=5, elevation_meters=2,
            current_season_index=8, geographic_exposure=8.0
        )
        
        # Many recent events
        many_events = [
            HistoricalEvent(severity=7.0, days_ago=365, impact_radius_km=150),
            HistoricalEvent(severity=6.5, days_ago=365*2, impact_radius_km=150),
            HistoricalEvent(severity=8.0, days_ago=365*3, impact_radius_km=200),
            HistoricalEvent(severity=6.0, days_ago=365*4, impact_radius_km=150)
        ]
        score_many, _ = engine.calculate_storm_risk(
            location, many_events, coastal_distance_km=5, elevation_meters=2,
            current_season_index=8, geographic_exposure=8.0
        )
        
        # More frequent events should increase or equal risk (might cap at 100)
        assert score_many >= score_few


class TestCompositeRiskCalculation:
    """Test composite risk aggregation."""
    
    def test_composite_weighted_average(self):
        """Test weighted average aggregation."""
        config = AssessmentConfig()
        config.composite_aggregation_method = "weighted_average"
        engine = RiskEngine(config)
        
        scores = {
            HazardType.EARTHQUAKE: 60.0,
            HazardType.FLOOD: 40.0,
            HazardType.FIRE: 30.0,
            HazardType.STORM: 50.0
        }
        
        composite, level, breakdown = engine.calculate_composite_risk(scores)
        
        # Should be average with equal weights
        expected = (60 + 40 + 30 + 50) / 4
        assert abs(composite - expected) < 0.01
        assert level == RiskLevel.MODERATE  # 45 is in moderate range (25-50)
    
    def test_composite_custom_weights(self):
        """Test composite with custom hazard weights."""
        engine = RiskEngine()
        
        scores = {
            HazardType.EARTHQUAKE: 80.0,
            HazardType.FLOOD: 20.0
        }
        
        # Equal weights
        composite_equal, _, _ = engine.calculate_composite_risk(scores)
        assert abs(composite_equal - 50.0) < 0.01
        
        # Weighted heavily toward earthquake
        weights = {
            HazardType.EARTHQUAKE: 0.9,
            HazardType.FLOOD: 0.1
        }
        composite_weighted, _, _ = engine.calculate_composite_risk(scores, weights)
        assert composite_weighted > 70  # Should be closer to 80
    
    def test_composite_max_aggregation(self):
        """Test max (worst-case) aggregation."""
        config = AssessmentConfig()
        config.composite_aggregation_method = "max"
        engine = RiskEngine(config)
        
        scores = {
            HazardType.EARTHQUAKE: 85.0,
            HazardType.FLOOD: 40.0,
            HazardType.FIRE: 30.0
        }
        
        composite, level, breakdown = engine.calculate_composite_risk(scores)
        
        # Should return maximum score
        assert composite == 85.0
        assert level == RiskLevel.CRITICAL
    
    def test_composite_probabilistic_aggregation(self):
        """Test probabilistic aggregation."""
        config = AssessmentConfig()
        config.composite_aggregation_method = "probabilistic"
        engine = RiskEngine(config)
        
        scores = {
            HazardType.EARTHQUAKE: 50.0,  # 0.5 probability
            HazardType.FLOOD: 50.0  # 0.5 probability
        }
        
        composite, level, breakdown = engine.calculate_composite_risk(scores)
        
        # Combined probability: 1 - (1-0.5)*(1-0.5) = 0.75 = 75%
        assert abs(composite - 75.0) < 0.01
        assert level == RiskLevel.CRITICAL
    
    def test_composite_risk_level_thresholds(self):
        """Test risk level classification."""
        engine = RiskEngine()
        
        # Low risk
        _, level, _ = engine.calculate_composite_risk({HazardType.EARTHQUAKE: 15.0})
        assert level == RiskLevel.LOW
        
        # Moderate risk
        _, level, _ = engine.calculate_composite_risk({HazardType.EARTHQUAKE: 40.0})
        assert level == RiskLevel.MODERATE
        
        # High risk
        _, level, _ = engine.calculate_composite_risk({HazardType.EARTHQUAKE: 60.0})
        assert level == RiskLevel.HIGH
        
        # Critical risk
        _, level, _ = engine.calculate_composite_risk({HazardType.EARTHQUAKE: 85.0})
        assert level == RiskLevel.CRITICAL
    
    def test_composite_empty_scores(self):
        """Test composite with no hazard scores."""
        engine = RiskEngine()
        
        composite, level, breakdown = engine.calculate_composite_risk({})
        
        assert composite == 0.0
        assert level == RiskLevel.LOW
        assert 'error' in breakdown


class TestHistoricalWeighting:
    """Test historical event weighting algorithm."""
    
    def test_historical_weighting_temporal_decay(self):
        """Test that temporal decay is applied correctly when mixing old and new events."""
        engine = RiskEngine()
        location = GeographicPoint(37.7749, -122.4194)
        
        # Mix of recent and old events - recent should dominate the average
        mixed_recent = [
            HistoricalEvent(severity=8.0, days_ago=365, impact_radius_km=50),  # Recent, high severity
            HistoricalEvent(severity=4.0, days_ago=365*30, impact_radius_km=50)  # Old, low severity
        ]
        score_recent_heavy = engine._calculate_historical_weighting(mixed_recent, location)
        
        # Mix with old event dominating
        mixed_old = [
            HistoricalEvent(severity=4.0, days_ago=365, impact_radius_km=50),  # Recent, low severity  
            HistoricalEvent(severity=8.0, days_ago=365*30, impact_radius_km=50)  # Old, high severity
        ]
        score_old_heavy = engine._calculate_historical_weighting(mixed_old, location)
        
        # Recent high-severity should score higher than old high-severity due to temporal weighting
        # Even though both have one 8.0 event, the temporal decay makes the recent one weighted more
        assert score_recent_heavy > score_old_heavy, \
            f"Recent-heavy: {score_recent_heavy}, Old-heavy: {score_old_heavy}"
    
    def test_historical_weighting_frequency_boost(self):
        """Test frequency boost for multiple events."""
        engine = RiskEngine()
        location = GeographicPoint(37.7749, -122.4194)
        
        # Single event
        single = [HistoricalEvent(severity=6.0, days_ago=365, impact_radius_km=50)]
        score_single = engine._calculate_historical_weighting(single, location)
        
        # Multiple events
        multiple = [
            HistoricalEvent(severity=6.0, days_ago=365, impact_radius_km=50),
            HistoricalEvent(severity=6.0, days_ago=365*2, impact_radius_km=50),
            HistoricalEvent(severity=6.0, days_ago=365*3, impact_radius_km=50)
        ]
        score_multiple = engine._calculate_historical_weighting(multiple, location)
        
        # Multiple events should have frequency boost
        assert score_multiple > score_single
    
    def test_historical_weighting_no_events(self):
        """Test with no historical events."""
        engine = RiskEngine()
        location = GeographicPoint(37.7749, -122.4194)
        
        score = engine._calculate_historical_weighting([], location)
        assert score == 0.0


class TestPerformanceBenchmarks:
    """Test performance requirements (<100ms per assessment)."""
    
    def test_seismic_risk_performance(self):
        """Test seismic risk calculation performance."""
        engine = RiskEngine()
        
        location = GeographicPoint(37.7749, -122.4194)
        faults = [
            HazardSource(GeographicPoint(37.7, -122.5), 8.0, 100),
            HazardSource(GeographicPoint(37.8, -122.3), 7.5, 80)
        ]
        events = [HistoricalEvent(6.5, 365*5, 50) for _ in range(10)]
        
        score, breakdown = engine.calculate_seismic_risk(
            location, faults, events, 1.5, 7.0
        )
        
        # Check performance
        assert breakdown['calculation_time_ms'] < 100, \
            f"Calculation took {breakdown['calculation_time_ms']}ms (target: <100ms)"
    
    def test_flood_risk_performance(self):
        """Test flood risk calculation performance."""
        engine = RiskEngine()
        
        location = GeographicPoint(29.7604, -95.3698)
        water_bodies = [
            HazardSource(GeographicPoint(29.76, -95.35), 7.0, 10),
            HazardSource(GeographicPoint(29.77, -95.36), 6.5, 8)
        ]
        events = [HistoricalEvent(7.0, 365*2, 20) for _ in range(10)]
        
        score, breakdown = engine.calculate_flood_risk(
            location, 15, water_bodies, events, 6.0, 1200
        )
        
        assert breakdown['calculation_time_ms'] < 100
    
    def test_wildfire_risk_performance(self):
        """Test wildfire risk calculation performance."""
        engine = RiskEngine()
        
        location = GeographicPoint(34.0522, -118.2437)
        fire_sources = [
            HazardSource(GeographicPoint(34.1, -118.3), 8.0, 20)
        ]
        events = [HistoricalEvent(7.5, 365, 15) for _ in range(10)]
        
        score, breakdown = engine.calculate_wildfire_risk(
            location, 7.0, 8.0, events, fire_sources, 28, 20
        )
        
        assert breakdown['calculation_time_ms'] < 100
    
    def test_storm_risk_performance(self):
        """Test storm risk calculation performance."""
        engine = RiskEngine()
        
        location = GeographicPoint(25.7617, -80.1918)
        events = [HistoricalEvent(7.0, 365*i, 150) for i in range(1, 11)]
        
        score, breakdown = engine.calculate_storm_risk(
            location, events, 5, 2, 8, 9.0
        )
        
        assert breakdown['calculation_time_ms'] < 100
    
    def test_composite_risk_performance(self):
        """Test composite risk aggregation performance."""
        engine = RiskEngine()
        
        scores = {
            HazardType.EARTHQUAKE: 65.0,
            HazardType.FLOOD: 45.0,
            HazardType.FIRE: 55.0,
            HazardType.STORM: 70.0
        }
        
        start = time.time()
        composite, level, breakdown = engine.calculate_composite_risk(scores)
        elapsed_ms = (time.time() - start) * 1000
        
        assert elapsed_ms < 10, f"Composite calculation took {elapsed_ms}ms (target: <10ms)"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_extreme_distances(self):
        """Test with extreme geographic distances."""
        engine = RiskEngine()
        
        # Opposite sides of Earth
        p1 = GeographicPoint(0, 0)
        p2 = GeographicPoint(0, 180)
        
        distance = engine.calculate_distance_km(p1, p2)
        assert distance > 0  # Should not crash
        assert distance < 50000  # Reasonable upper bound (Earth circumference ~40,000km)
    
    def test_boundary_coordinates(self):
        """Test with boundary coordinate values."""
        engine = RiskEngine()
        
        # North Pole
        north_pole = GeographicPoint(90, 0)
        # South Pole
        south_pole = GeographicPoint(-90, 0)
        # Equator corners
        eq1 = GeographicPoint(0, -180)
        eq2 = GeographicPoint(0, 180)
        
        # Should not crash
        distance = engine.calculate_distance_km(north_pole, south_pole)
        assert distance > 0
    
    def test_zero_and_extreme_values(self):
        """Test algorithms with zero and extreme input values."""
        engine = RiskEngine()
        
        location = GeographicPoint(0, 0)
        
        # All zero values
        score, _ = engine.calculate_seismic_risk(
            location, [], [], soil_amplification=0, building_code_rating=0
        )
        assert 0 <= score <= 100
        
        # Extreme values
        fault = HazardSource(location, 10.0, 1000)
        score, _ = engine.calculate_seismic_risk(
            location, [fault], [], soil_amplification=5.0, building_code_rating=10.0
        )
        assert 0 <= score <= 100
    
    def test_negative_and_invalid_inputs(self):
        """Test handling of negative/invalid inputs."""
        engine = RiskEngine()
        
        location = GeographicPoint(37.7749, -122.4194)
        
        # Negative elevation should work for below sea level
        score, _ = engine.calculate_flood_risk(
            location, elevation_meters=-10, water_bodies=[],
            historical_events=[], drainage_quality=5.0
        )
        assert score > 0  # Below sea level = high flood risk
    
    def test_cache_overflow_handling(self):
        """Test distance cache with overflow."""
        config = AssessmentConfig()
        config.proximity_cache_size = 5  # Small cache
        engine = RiskEngine(config)
        
        # Generate more distances than cache size
        points = [GeographicPoint(i, i) for i in range(10)]
        
        for i in range(len(points) - 1):
            engine.calculate_distance_km(points[i], points[i+1])
        
        # Cache should not exceed max size
        stats = engine.get_performance_stats()
        assert stats['cache_size'] <= config.proximity_cache_size


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

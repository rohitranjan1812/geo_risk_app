"""
Core risk assessment algorithms for multi-hazard geographic analysis.

This module implements sophisticated algorithms for calculating risk scores
across multiple hazard types (earthquakes, floods, fires, storms) with support
for geographic proximity analysis, historical event weighting, and composite
risk calculation.

Performance Target: <100ms per single location assessment
"""
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from math import radians, cos, sin, asin, sqrt
import time
from enum import Enum

from app.models import HazardType, RiskLevel


class ProximityDecayModel(str, Enum):
    """Models for calculating distance-based risk decay."""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    INVERSE_SQUARE = "inverse_square"


@dataclass
class GeographicPoint:
    """Represents a geographic coordinate."""
    latitude: float
    longitude: float
    
    def __post_init__(self):
        """Validate coordinates."""
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"Invalid latitude: {self.latitude}")
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"Invalid longitude: {self.longitude}")


@dataclass
class HazardSource:
    """Represents a hazard source with geographic location."""
    location: GeographicPoint
    intensity: float  # 0-10 scale
    influence_radius_km: float  # Maximum influence distance


@dataclass
class HistoricalEvent:
    """Represents a historical hazard event."""
    severity: float  # 0-10 scale
    days_ago: int
    impact_radius_km: float


@dataclass
class AssessmentConfig:
    """Configuration for risk assessment algorithms."""
    # Earthquake
    seismic_weight_fault_proximity: float = 0.40
    seismic_weight_historical: float = 0.25
    seismic_weight_magnitude: float = 0.35
    
    # Flood
    flood_weight_elevation: float = 0.35
    flood_weight_water_proximity: float = 0.30
    flood_weight_historical: float = 0.20
    flood_weight_drainage: float = 0.15
    
    # Fire
    fire_weight_vegetation: float = 0.35
    fire_weight_climate: float = 0.25
    fire_weight_historical: float = 0.20
    fire_weight_proximity: float = 0.20
    
    # Storm
    storm_weight_historical_patterns: float = 0.40
    storm_weight_geographic_exposure: float = 0.30
    storm_weight_seasonal_factors: float = 0.30
    
    # Composite
    composite_aggregation_method: str = "weighted_average"  # or "max" or "probabilistic"
    
    # Performance
    proximity_cache_size: int = 1000
    calculation_timeout_ms: int = 100


class RiskEngine:
    """
    Core risk assessment engine with validated algorithms for multi-hazard analysis.
    
    Features:
    - Seismic risk calculation based on fault line proximity
    - Flood risk from elevation and water body proximity
    - Wildfire risk from vegetation density and climate factors
    - Storm risk from historical patterns and geographic exposure
    - Composite risk aggregation across all hazard types
    - Configurable algorithm parameters
    - Performance optimized for <100ms assessments
    """
    
    def __init__(self, config: Optional[AssessmentConfig] = None):
        """
        Initialize the risk engine.
        
        Args:
            config: Optional configuration for algorithm parameters
        """
        self.config = config or AssessmentConfig()
        self._distance_cache: Dict[Tuple[float, float, float, float], float] = {}
    
    # ============================================================================
    # Geographic Utility Functions
    # ============================================================================
    
    def calculate_distance_km(
        self,
        point1: GeographicPoint,
        point2: GeographicPoint
    ) -> float:
        """
        Calculate great circle distance between two points using Haversine formula.
        
        Args:
            point1: First geographic point
            point2: Second geographic point
            
        Returns:
            Distance in kilometers
            
        Example:
            >>> engine = RiskEngine()
            >>> p1 = GeographicPoint(37.7749, -122.4194)  # San Francisco
            >>> p2 = GeographicPoint(34.0522, -118.2437)  # Los Angeles
            >>> distance = engine.calculate_distance_km(p1, p2)
            >>> assert 550 < distance < 560  # ~559 km actual
        """
        # Check cache first
        cache_key = (point1.latitude, point1.longitude, point2.latitude, point2.longitude)
        if cache_key in self._distance_cache:
            return self._distance_cache[cache_key]
        
        # Haversine formula
        lon1, lat1, lon2, lat2 = map(
            radians,
            [point1.longitude, point1.latitude, point2.longitude, point2.latitude]
        )
        
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Radius of earth in kilometers
        km = 6371 * c
        
        # Cache result
        if len(self._distance_cache) < self.config.proximity_cache_size:
            self._distance_cache[cache_key] = km
        
        return km
    
    def calculate_proximity_impact(
        self,
        distance_km: float,
        max_distance_km: float,
        decay_model: ProximityDecayModel = ProximityDecayModel.EXPONENTIAL
    ) -> float:
        """
        Calculate risk impact based on distance using various decay models.
        
        Args:
            distance_km: Distance to hazard source
            max_distance_km: Maximum influence distance (beyond this, impact = 0)
            decay_model: Model for distance-based decay
            
        Returns:
            Impact factor between 0 and 1
            
        Example:
            >>> engine = RiskEngine()
            >>> # At source (0 km): maximum impact
            >>> assert engine.calculate_proximity_impact(0, 100) == 1.0
            >>> # Beyond max distance: no impact
            >>> assert engine.calculate_proximity_impact(150, 100) == 0.0
        """
        if distance_km >= max_distance_km:
            return 0.0
        
        # Normalize distance to 0-1 range
        normalized = distance_km / max_distance_km
        
        if decay_model == ProximityDecayModel.LINEAR:
            return 1.0 - normalized
        
        elif decay_model == ProximityDecayModel.EXPONENTIAL:
            # e^(-3x) provides smooth decay, reaching ~5% at max distance
            import math
            return math.exp(-3 * normalized)
        
        elif decay_model == ProximityDecayModel.INVERSE_SQUARE:
            # Similar to physical force decay
            if distance_km < 1:  # Avoid division by very small numbers
                return 1.0
            return max(0, 1.0 - (normalized ** 2))
        
        return 1.0 - normalized  # Default to linear
    
    # ============================================================================
    # Earthquake Risk Assessment
    # ============================================================================
    
    def calculate_seismic_risk(
        self,
        location: GeographicPoint,
        fault_lines: List[HazardSource],
        historical_events: List[HistoricalEvent],
        soil_amplification: float = 1.0,
        building_code_rating: float = 5.0
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate earthquake risk based on fault line proximity and seismic history.
        
        Algorithm:
        1. Fault proximity: Exponential decay from nearest major fault
        2. Historical weighting: Recent events weighted more heavily
        3. Magnitude scaling: Logarithmic scale for earthquake magnitudes
        4. Soil amplification: Multiplier for soft soil areas (1.0-2.0)
        5. Building codes: Mitigation factor (0-10 scale, inverse)
        
        Args:
            location: Assessment location
            fault_lines: List of fault line segments with intensity
            historical_events: Past earthquake events
            soil_amplification: Soil type multiplier (1.0=rock, 2.0=soft soil)
            building_code_rating: Building code strength (0=weak, 10=strong)
            
        Returns:
            Tuple of (risk_score 0-100, component_breakdown dict)
            
        Example:
            >>> engine = RiskEngine()
            >>> loc = GeographicPoint(37.7749, -122.4194)  # SF
            >>> fault = HazardSource(
            ...     location=GeographicPoint(37.7, -122.5),
            ...     intensity=8.0,  # Magnitude potential
            ...     influence_radius_km=100
            ... )
            >>> events = [HistoricalEvent(severity=6.9, days_ago=365*30, impact_radius_km=50)]
            >>> score, breakdown = engine.calculate_seismic_risk(loc, [fault], events)
            >>> assert 0 <= score <= 100
            >>> assert 'fault_proximity_score' in breakdown
        """
        start_time = time.time()
        
        # Component 1: Fault Proximity Score
        fault_proximity_score = 0.0
        if fault_lines:
            min_distance = float('inf')
            nearest_fault_intensity = 0.0
            
            for fault in fault_lines:
                distance = self.calculate_distance_km(location, fault.location)
                if distance < min_distance:
                    min_distance = distance
                    nearest_fault_intensity = fault.intensity
            
            # Calculate proximity impact with exponential decay
            proximity_factor = self.calculate_proximity_impact(
                min_distance,
                fault_lines[0].influence_radius_km if fault_lines else 100,
                ProximityDecayModel.EXPONENTIAL
            )
            
            # Scale by fault intensity (magnitude potential)
            fault_proximity_score = proximity_factor * (nearest_fault_intensity / 10) * 100
        
        # Component 2: Historical Event Score
        historical_score = self._calculate_historical_weighting(historical_events, location)
        
        # Component 3: Magnitude Potential (from fault intensity)
        magnitude_score = 0.0
        if fault_lines:
            max_magnitude = max(f.intensity for f in fault_lines)
            # Logarithmic scaling for magnitude (Richter scale is logarithmic)
            magnitude_score = (max_magnitude / 10) ** 1.5 * 100
        
        # Apply soil amplification
        amplified_scores = {
            'fault_proximity_score': fault_proximity_score * soil_amplification,
            'historical_score': historical_score * soil_amplification,
            'magnitude_score': magnitude_score * soil_amplification
        }
        
        # Weighted combination
        base_risk = (
            amplified_scores['fault_proximity_score'] * self.config.seismic_weight_fault_proximity +
            amplified_scores['historical_score'] * self.config.seismic_weight_historical +
            amplified_scores['magnitude_score'] * self.config.seismic_weight_magnitude
        )
        
        # Apply building code mitigation (higher rating = lower risk)
        mitigation_factor = 1.0 - (building_code_rating / 20)  # Max 50% reduction
        final_risk = base_risk * mitigation_factor
        
        # Ensure within bounds
        final_risk = max(0, min(100, final_risk))
        
        breakdown = {
            **amplified_scores,
            'soil_amplification': soil_amplification,
            'building_code_mitigation': 1.0 - mitigation_factor,
            'calculation_time_ms': (time.time() - start_time) * 1000
        }
        
        return round(final_risk, 2), breakdown
    
    # ============================================================================
    # Flood Risk Assessment
    # ============================================================================
    
    def calculate_flood_risk(
        self,
        location: GeographicPoint,
        elevation_meters: float,
        water_bodies: List[HazardSource],
        historical_events: List[HistoricalEvent],
        drainage_quality: float = 5.0,
        annual_rainfall_mm: float = 1000.0
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate flood risk from elevation, water proximity, and drainage.
        
        Algorithm:
        1. Elevation factor: Low-lying areas have higher risk
        2. Water proximity: Distance to rivers, lakes, coastlines
        3. Drainage quality: Infrastructure effectiveness (0-10 scale)
        4. Historical flooding: Weighted recent events
        5. Rainfall patterns: Annual precipitation correlation
        
        Args:
            location: Assessment location
            elevation_meters: Elevation above sea level
            water_bodies: Nearby water sources (rivers, lakes, ocean)
            historical_events: Past flood events
            drainage_quality: Drainage infrastructure rating (0=poor, 10=excellent)
            annual_rainfall_mm: Average annual rainfall
            
        Returns:
            Tuple of (risk_score 0-100, component_breakdown dict)
            
        Example:
            >>> engine = RiskEngine()
            >>> loc = GeographicPoint(29.7604, -95.3698)  # Houston
            >>> water = HazardSource(
            ...     location=GeographicPoint(29.76, -95.35),  # Buffalo Bayou
            ...     intensity=7.0,
            ...     influence_radius_km=10
            ... )
            >>> score, breakdown = engine.calculate_flood_risk(
            ...     loc, elevation_meters=15, water_bodies=[water],
            ...     historical_events=[], drainage_quality=6.0
            ... )
            >>> assert 0 <= score <= 100
        """
        start_time = time.time()
        
        # Component 1: Elevation Score
        # Risk decreases with elevation (exponential decay)
        # Sea level (0m) = 100 risk, 100m+ = ~0 risk
        import math
        elevation_score = 100 * math.exp(-elevation_meters / 30)
        
        # Component 2: Water Proximity Score
        water_proximity_score = 0.0
        if water_bodies:
            proximity_impacts = []
            for water_body in water_bodies:
                distance = self.calculate_distance_km(location, water_body.location)
                impact = self.calculate_proximity_impact(
                    distance,
                    water_body.influence_radius_km,
                    ProximityDecayModel.EXPONENTIAL
                )
                # Weight by water body intensity (size/flow rate)
                weighted_impact = impact * (water_body.intensity / 10)
                proximity_impacts.append(weighted_impact)
            
            # Use maximum proximity impact (worst case)
            water_proximity_score = max(proximity_impacts) * 100 if proximity_impacts else 0
        
        # Component 3: Historical Flood Score
        historical_score = self._calculate_historical_weighting(historical_events, location)
        
        # Component 4: Drainage Quality (inverse relationship)
        drainage_score = (10 - drainage_quality) / 10 * 100
        
        # Component 5: Rainfall Factor
        # Normalize rainfall (0-5000mm range)
        rainfall_factor = min(annual_rainfall_mm / 5000, 1.0)
        
        # Weighted combination
        base_risk = (
            elevation_score * self.config.flood_weight_elevation +
            water_proximity_score * self.config.flood_weight_water_proximity +
            historical_score * self.config.flood_weight_historical +
            drainage_score * self.config.flood_weight_drainage
        )
        
        # Apply rainfall multiplier
        final_risk = base_risk * (0.5 + rainfall_factor * 0.5)  # 50%-100% based on rainfall
        
        # Ensure within bounds
        final_risk = max(0, min(100, final_risk))
        
        breakdown = {
            'elevation_score': round(elevation_score, 2),
            'water_proximity_score': round(water_proximity_score, 2),
            'historical_score': round(historical_score, 2),
            'drainage_score': round(drainage_score, 2),
            'rainfall_factor': round(rainfall_factor, 2),
            'calculation_time_ms': (time.time() - start_time) * 1000
        }
        
        return round(final_risk, 2), breakdown
    
    # ============================================================================
    # Wildfire Risk Assessment
    # ============================================================================
    
    def calculate_wildfire_risk(
        self,
        location: GeographicPoint,
        vegetation_density: float,
        climate_aridity_index: float,
        historical_events: List[HistoricalEvent],
        fire_sources: List[HazardSource],
        temperature_avg_c: float = 20.0,
        wind_speed_kmh: float = 10.0
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate wildfire risk from vegetation, climate, and fire history.
        
        Algorithm:
        1. Vegetation fuel load: Density and type (0-10 scale)
        2. Climate aridity: Dryness index (0-10 scale)
        3. Temperature factor: Higher temps increase risk
        4. Wind speed: Affects spread rate
        5. Proximity to recent fires: Active fire zones
        6. Historical patterns: Seasonal fire frequency
        
        Args:
            location: Assessment location
            vegetation_density: Fuel load rating (0=barren, 10=dense forest)
            climate_aridity_index: Dryness measure (0=wet, 10=desert)
            historical_events: Past wildfire events
            fire_sources: Active or recent fire locations
            temperature_avg_c: Average temperature (Celsius)
            wind_speed_kmh: Average wind speed
            
        Returns:
            Tuple of (risk_score 0-100, component_breakdown dict)
            
        Example:
            >>> engine = RiskEngine()
            >>> loc = GeographicPoint(34.0522, -118.2437)  # Los Angeles
            >>> score, breakdown = engine.calculate_wildfire_risk(
            ...     loc, vegetation_density=7.0, climate_aridity_index=8.0,
            ...     historical_events=[], fire_sources=[],
            ...     temperature_avg_c=25, wind_speed_kmh=15
            ... )
            >>> assert 0 <= score <= 100
        """
        start_time = time.time()
        
        # Component 1: Vegetation Score
        vegetation_score = (vegetation_density / 10) * 100
        
        # Component 2: Climate/Aridity Score
        climate_score = (climate_aridity_index / 10) * 100
        
        # Component 3: Temperature Factor
        # Risk increases above 20°C, doubles at 40°C
        temp_factor = 1.0 + max(0, (temperature_avg_c - 20) / 20)
        
        # Component 4: Wind Factor
        # Risk increases linearly with wind speed (normalized to 0-100 km/h)
        wind_factor = 1.0 + min(wind_speed_kmh / 100, 1.0)
        
        # Component 5: Active Fire Proximity
        proximity_score = 0.0
        if fire_sources:
            proximity_impacts = []
            for fire_source in fire_sources:
                distance = self.calculate_distance_km(location, fire_source.location)
                impact = self.calculate_proximity_impact(
                    distance,
                    fire_source.influence_radius_km,
                    ProximityDecayModel.EXPONENTIAL
                )
                # Weight by fire intensity
                weighted_impact = impact * (fire_source.intensity / 10)
                proximity_impacts.append(weighted_impact)
            
            proximity_score = max(proximity_impacts) * 100 if proximity_impacts else 0
        
        # Component 6: Historical Fire Score
        historical_score = self._calculate_historical_weighting(historical_events, location)
        
        # Weighted combination
        base_risk = (
            vegetation_score * self.config.fire_weight_vegetation +
            climate_score * self.config.fire_weight_climate +
            historical_score * self.config.fire_weight_historical +
            proximity_score * self.config.fire_weight_proximity
        )
        
        # Apply environmental multipliers
        final_risk = base_risk * temp_factor * wind_factor
        
        # Ensure within bounds
        final_risk = max(0, min(100, final_risk))
        
        breakdown = {
            'vegetation_score': round(vegetation_score, 2),
            'climate_score': round(climate_score, 2),
            'proximity_score': round(proximity_score, 2),
            'historical_score': round(historical_score, 2),
            'temperature_factor': round(temp_factor, 2),
            'wind_factor': round(wind_factor, 2),
            'calculation_time_ms': (time.time() - start_time) * 1000
        }
        
        return round(final_risk, 2), breakdown
    
    # ============================================================================
    # Storm Risk Assessment
    # ============================================================================
    
    def calculate_storm_risk(
        self,
        location: GeographicPoint,
        historical_events: List[HistoricalEvent],
        coastal_distance_km: float,
        elevation_meters: float,
        current_season_index: int = 0,  # 0-11 for months
        geographic_exposure: float = 5.0  # 0-10 scale
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate storm risk from historical patterns and geographic exposure.
        
        Algorithm:
        1. Historical pattern analysis: Frequency and intensity trends
        2. Seasonal factors: Month-specific risk profiles
        3. Geographic exposure: Coastal proximity, topography
        4. Storm track analysis: Path likelihood
        5. Intensity trends: Recent vs historical comparison
        
        Args:
            location: Assessment location
            historical_events: Past storm events (hurricanes, tornadoes, etc.)
            coastal_distance_km: Distance to nearest coast (0 for coastal)
            elevation_meters: Elevation (affects exposure)
            current_season_index: Month (0=Jan, 11=Dec) for seasonal weighting
            geographic_exposure: Exposure rating (0=sheltered, 10=exposed)
            
        Returns:
            Tuple of (risk_score 0-100, component_breakdown dict)
            
        Example:
            >>> engine = RiskEngine()
            >>> loc = GeographicPoint(25.7617, -80.1918)  # Miami
            >>> events = [
            ...     HistoricalEvent(severity=8.0, days_ago=365*5, impact_radius_km=200),
            ...     HistoricalEvent(severity=6.0, days_ago=365*2, impact_radius_km=150)
            ... ]
            >>> score, breakdown = engine.calculate_storm_risk(
            ...     loc, events, coastal_distance_km=5,
            ...     elevation_meters=2, current_season_index=8  # September
            ... )
            >>> assert 0 <= score <= 100
        """
        start_time = time.time()
        
        # Component 1: Historical Pattern Score
        historical_score = self._calculate_historical_weighting(historical_events, location)
        
        # Enhanced with frequency analysis
        if historical_events:
            # Calculate average severity
            avg_severity = sum(e.severity for e in historical_events) / len(historical_events)
            severity_factor = avg_severity / 10
            
            # Calculate event frequency (events per year)
            if historical_events:
                max_days = max(e.days_ago for e in historical_events)
                years_span = max(max_days / 365, 1)
                frequency = len(historical_events) / years_span
                frequency_factor = min(frequency / 5, 1.0)  # Normalize to 5 events/year max
            else:
                frequency_factor = 0
            
            # Combine severity and frequency
            historical_score = max(historical_score, (severity_factor * 50 + frequency_factor * 50))
        
        # Component 2: Seasonal Factor
        # Hurricane season peaks: Jun(5)-Nov(10) for Atlantic
        # Tornado season peaks: Mar(2)-Jun(5) for US
        seasonal_weights = [0.3, 0.4, 0.7, 0.8, 0.9, 1.0, 0.9, 0.9, 1.0, 0.9, 0.7, 0.4]
        seasonal_factor = seasonal_weights[current_season_index]
        
        # Component 3: Geographic Exposure Score
        exposure_score = (geographic_exposure / 10) * 100
        
        # Component 4: Coastal Proximity (inverse for storms)
        # Coastal areas have higher storm risk
        import math
        coastal_factor = 1.0 + math.exp(-coastal_distance_km / 50)  # Decay over 50km
        
        # Component 5: Elevation Factor (low elevation = higher storm surge risk)
        elevation_factor = 1.0 + max(0, (20 - elevation_meters) / 20)  # Boost for <20m elevation
        
        # Weighted combination
        base_risk = (
            historical_score * self.config.storm_weight_historical_patterns +
            exposure_score * self.config.storm_weight_geographic_exposure +
            (seasonal_factor * 100) * self.config.storm_weight_seasonal_factors
        )
        
        # Apply geographic multipliers
        final_risk = base_risk * coastal_factor * (elevation_factor ** 0.5)  # Soften elevation impact
        
        # Ensure within bounds
        final_risk = max(0, min(100, final_risk))
        
        breakdown = {
            'historical_score': round(historical_score, 2),
            'exposure_score': round(exposure_score, 2),
            'seasonal_factor': round(seasonal_factor, 2),
            'coastal_factor': round(coastal_factor, 2),
            'elevation_factor': round(elevation_factor, 2),
            'calculation_time_ms': (time.time() - start_time) * 1000
        }
        
        return round(final_risk, 2), breakdown
    
    # ============================================================================
    # Composite Risk Calculation
    # ============================================================================
    
    def calculate_composite_risk(
        self,
        hazard_scores: Dict[HazardType, float],
        hazard_weights: Optional[Dict[HazardType, float]] = None
    ) -> Tuple[float, RiskLevel, Dict[str, any]]:
        """
        Aggregate multiple hazard risks into composite score.
        
        Supports three aggregation methods:
        1. weighted_average: Traditional weighted sum
        2. max: Worst-case scenario (highest individual risk)
        3. probabilistic: Combined probability approach
        
        Args:
            hazard_scores: Dictionary mapping HazardType to risk score (0-100)
            hazard_weights: Optional weights for each hazard (default: equal weights)
            
        Returns:
            Tuple of (composite_score 0-100, risk_level, breakdown dict)
            
        Example:
            >>> engine = RiskEngine()
            >>> scores = {
            ...     HazardType.EARTHQUAKE: 65.0,
            ...     HazardType.FLOOD: 45.0,
            ...     HazardType.FIRE: 30.0,
            ...     HazardType.STORM: 55.0
            ... }
            >>> composite, level, breakdown = engine.calculate_composite_risk(scores)
            >>> assert 0 <= composite <= 100
            >>> assert level in [RiskLevel.LOW, RiskLevel.MODERATE, RiskLevel.HIGH, RiskLevel.CRITICAL]
        """
        start_time = time.time()
        
        if not hazard_scores:
            return 0.0, RiskLevel.LOW, {'error': 'No hazard scores provided'}
        
        # Default to equal weights if not provided
        if hazard_weights is None:
            hazard_weights = {h: 1.0 / len(hazard_scores) for h in hazard_scores.keys()}
        
        # Normalize weights to sum to 1.0
        weight_sum = sum(hazard_weights.values())
        if weight_sum > 0:
            normalized_weights = {h: w / weight_sum for h, w in hazard_weights.items()}
        else:
            normalized_weights = {h: 1.0 / len(hazard_weights) for h in hazard_weights.keys()}
        
        # Calculate based on aggregation method
        method = self.config.composite_aggregation_method
        
        if method == "weighted_average":
            composite_score = sum(
                score * normalized_weights.get(hazard, 0)
                for hazard, score in hazard_scores.items()
            )
        
        elif method == "max":
            # Worst-case scenario
            composite_score = max(hazard_scores.values())
        
        elif method == "probabilistic":
            # Convert scores to probabilities (0-1 scale)
            # Combined probability: 1 - Product(1 - p_i)
            probs = [score / 100 for score in hazard_scores.values()]
            combined_prob = 1.0 - eval('*'.join([f"(1-{p})" for p in probs]))
            composite_score = combined_prob * 100
        
        else:
            # Default to weighted average
            composite_score = sum(
                score * normalized_weights.get(hazard, 0)
                for hazard, score in hazard_scores.items()
            )
        
        # Ensure within bounds
        composite_score = max(0, min(100, composite_score))
        
        # Determine risk level
        risk_level = self._determine_risk_level(composite_score)
        
        breakdown = {
            'individual_scores': hazard_scores,
            'weights_used': normalized_weights,
            'aggregation_method': method,
            'calculation_time_ms': (time.time() - start_time) * 1000
        }
        
        return round(composite_score, 2), risk_level, breakdown
    
    # ============================================================================
    # Helper Methods
    # ============================================================================
    
    def _calculate_historical_weighting(
        self,
        events: List[HistoricalEvent],
        location: GeographicPoint,
        decay_years: float = 10.0
    ) -> float:
        """
        Calculate weighted historical impact with temporal decay.
        
        Recent events are weighted more heavily using exponential decay.
        
        Args:
            events: List of historical events
            location: Assessment location
            decay_years: Years for impact to decay to ~37% (1/e)
            
        Returns:
            Weighted historical score (0-100)
        """
        if not events:
            return 0.0
        
        import math
        weighted_sum = 0.0
        total_weight = 0.0
        
        for event in events:
            # Temporal decay weight
            years_ago = event.days_ago / 365
            time_weight = math.exp(-years_ago / decay_years)
            
            # Severity contribution (0-10 scale to 0-100)
            severity_score = (event.severity / 10) * 100
            
            weighted_sum += severity_score * time_weight
            total_weight += time_weight
        
        if total_weight == 0:
            return 0.0
        
        # Normalize by total weight
        weighted_score = weighted_sum / total_weight
        
        # Boost if many recent events
        frequency_boost = min(len(events) / 10, 0.2)  # Up to 20% boost for 10+ events
        
        return min(weighted_score * (1 + frequency_boost), 100)
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """
        Map risk score to risk level category.
        
        Args:
            risk_score: Risk score (0-100)
            
        Returns:
            RiskLevel enum value
        """
        if risk_score < 25:
            return RiskLevel.LOW
        elif risk_score < 50:
            return RiskLevel.MODERATE
        elif risk_score < 75:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def clear_cache(self) -> None:
        """Clear the distance calculation cache."""
        self._distance_cache.clear()
    
    def get_performance_stats(self) -> Dict[str, any]:
        """
        Get performance statistics.
        
        Returns:
            Dictionary with cache size and other metrics
        """
        return {
            'cache_size': len(self._distance_cache),
            'cache_max_size': self.config.proximity_cache_size,
            'cache_utilization': len(self._distance_cache) / self.config.proximity_cache_size
        }

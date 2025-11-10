"""Risk calculation service with algorithms for different hazard types."""
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models import Location, Hazard, HazardType, RiskLevel, HistoricalData


class RiskCalculationService:
    """Service for calculating risk scores based on various factors."""
    
    # Risk level thresholds
    RISK_THRESHOLDS = {
        RiskLevel.LOW: (0, 25),
        RiskLevel.MODERATE: (25, 50),
        RiskLevel.HIGH: (50, 75),
        RiskLevel.CRITICAL: (75, 100)
    }
    
    def __init__(self, db: AsyncSession):
        """Initialize risk calculation service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def calculate_risk(
        self,
        location: Location,
        hazard: Hazard,
        custom_factors: Dict[str, float] | None = None
    ) -> Tuple[float, RiskLevel, float, Dict[str, float], List[str]]:
        """Calculate comprehensive risk score for a location-hazard combination.
        
        Args:
            location: Location object
            hazard: Hazard object
            custom_factors: Optional custom risk factors to override location defaults
            
        Returns:
            Tuple of (risk_score, risk_level, confidence, factors_analysis, recommendations)
        """
        # Use custom factors if provided, otherwise use location defaults
        pop_density = custom_factors.get('population_density', location.population_density) if custom_factors else location.population_density
        building_code = custom_factors.get('building_code_rating', location.building_code_rating) if custom_factors else location.building_code_rating
        infrastructure = custom_factors.get('infrastructure_quality', location.infrastructure_quality) if custom_factors else location.infrastructure_quality
        
        # Calculate individual factor impacts
        factors_analysis = await self._analyze_factors(
            location, hazard, pop_density, building_code, infrastructure
        )
        
        # Calculate final risk score using hazard-specific algorithm
        risk_score = await self._calculate_hazard_specific_risk(
            hazard.hazard_type,
            factors_analysis,
            hazard.base_severity
        )
        
        # Determine risk level
        risk_level = self._determine_risk_level(risk_score)
        
        # Calculate confidence level based on historical data availability
        confidence = await self._calculate_confidence(location, hazard)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            risk_score, risk_level, hazard.hazard_type, factors_analysis
        )
        
        return risk_score, risk_level, confidence, factors_analysis, recommendations
    
    async def _analyze_factors(
        self,
        location: Location,
        hazard: Hazard,
        pop_density: float,
        building_code: float,
        infrastructure: float
    ) -> Dict[str, float]:
        """Analyze individual risk factors and their impacts.
        
        Args:
            location: Location object
            hazard: Hazard object
            pop_density: Population density
            building_code: Building code rating (0-10)
            infrastructure: Infrastructure quality (0-10)
            
        Returns:
            Dictionary of factor impacts (0-100 scale)
        """
        # Normalize population density (assuming max 10,000 per sq km)
        pop_impact = min((pop_density / 10000) * 100, 100)
        
        # Building codes - inverse relationship (higher rating = lower risk)
        building_impact = max(0, 100 - (building_code * 10))
        
        # Infrastructure - inverse relationship
        infra_impact = max(0, 100 - (infrastructure * 10))
        
        # Hazard base severity impact
        hazard_impact = (hazard.base_severity / 10) * 100
        
        # Historical frequency impact
        historical_impact = await self._calculate_historical_frequency_impact(location, hazard)
        
        return {
            'population_density_impact': round(pop_impact, 2),
            'building_code_impact': round(building_impact, 2),
            'infrastructure_impact': round(infra_impact, 2),
            'hazard_severity_impact': round(hazard_impact, 2),
            'historical_frequency_impact': round(historical_impact, 2)
        }
    
    async def _calculate_historical_frequency_impact(
        self,
        location: Location,
        hazard: Hazard
    ) -> float:
        """Calculate impact based on historical event frequency.
        
        Args:
            location: Location object
            hazard: Hazard object
            
        Returns:
            Impact score (0-100)
        """
        # Count events in last 10 years
        ten_years_ago = datetime.utcnow() - timedelta(days=3650)
        
        result = await self.db.execute(
            select(func.count(HistoricalData.id))
            .where(
                HistoricalData.location_id == location.id,
                HistoricalData.hazard_id == hazard.id,
                HistoricalData.event_date >= ten_years_ago
            )
        )
        event_count = result.scalar() or 0
        
        # Calculate impact based on frequency (0-10+ events)
        frequency_impact = min((event_count / 10) * 100, 100)
        
        return frequency_impact
    
    async def _calculate_hazard_specific_risk(
        self,
        hazard_type: HazardType,
        factors: Dict[str, float],
        base_severity: float
    ) -> float:
        """Calculate risk using hazard-specific algorithms.
        
        Args:
            hazard_type: Type of hazard
            factors: Factor analysis dictionary
            base_severity: Base severity of hazard (0-10)
            
        Returns:
            Final risk score (0-100)
        """
        if hazard_type == HazardType.EARTHQUAKE:
            return self._calculate_earthquake_risk(factors)
        elif hazard_type == HazardType.FLOOD:
            return self._calculate_flood_risk(factors)
        elif hazard_type == HazardType.FIRE:
            return self._calculate_fire_risk(factors)
        elif hazard_type == HazardType.STORM:
            return self._calculate_storm_risk(factors)
        else:
            # Default weighted average
            return self._calculate_default_risk(factors)
    
    def _calculate_earthquake_risk(self, factors: Dict[str, float]) -> float:
        """Calculate earthquake-specific risk score.
        
        Building codes and infrastructure are critical for earthquakes.
        """
        weights = {
            'population_density_impact': 0.15,
            'building_code_impact': 0.35,  # Critical for earthquakes
            'infrastructure_impact': 0.25,
            'hazard_severity_impact': 0.15,
            'historical_frequency_impact': 0.10
        }
        
        score = sum(factors[key] * weight for key, weight in weights.items())
        return round(min(max(score, 0), 100), 2)
    
    def _calculate_flood_risk(self, factors: Dict[str, float]) -> float:
        """Calculate flood-specific risk score.
        
        Infrastructure (drainage) is critical for floods.
        """
        weights = {
            'population_density_impact': 0.20,
            'building_code_impact': 0.15,
            'infrastructure_impact': 0.35,  # Drainage systems critical
            'hazard_severity_impact': 0.20,
            'historical_frequency_impact': 0.10
        }
        
        score = sum(factors[key] * weight for key, weight in weights.items())
        return round(min(max(score, 0), 100), 2)
    
    def _calculate_fire_risk(self, factors: Dict[str, float]) -> float:
        """Calculate fire-specific risk score.
        
        Population density and building codes matter most.
        """
        weights = {
            'population_density_impact': 0.30,  # Dense areas = faster spread
            'building_code_impact': 0.30,  # Fire safety standards
            'infrastructure_impact': 0.15,
            'hazard_severity_impact': 0.15,
            'historical_frequency_impact': 0.10
        }
        
        score = sum(factors[key] * weight for key, weight in weights.items())
        return round(min(max(score, 0), 100), 2)
    
    def _calculate_storm_risk(self, factors: Dict[str, float]) -> float:
        """Calculate storm-specific risk score.
        
        Infrastructure resilience is key.
        """
        weights = {
            'population_density_impact': 0.20,
            'building_code_impact': 0.25,
            'infrastructure_impact': 0.30,  # Power, communication lines
            'hazard_severity_impact': 0.15,
            'historical_frequency_impact': 0.10
        }
        
        score = sum(factors[key] * weight for key, weight in weights.items())
        return round(min(max(score, 0), 100), 2)
    
    def _calculate_default_risk(self, factors: Dict[str, float]) -> float:
        """Calculate default risk score with equal weights."""
        weights = {
            'population_density_impact': 0.20,
            'building_code_impact': 0.20,
            'infrastructure_impact': 0.20,
            'hazard_severity_impact': 0.20,
            'historical_frequency_impact': 0.20
        }
        
        score = sum(factors[key] * weight for key, weight in weights.items())
        return round(min(max(score, 0), 100), 2)
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level from score.
        
        Args:
            risk_score: Risk score (0-100)
            
        Returns:
            RiskLevel enum
        """
        for level, (min_score, max_score) in self.RISK_THRESHOLDS.items():
            if min_score <= risk_score < max_score:
                return level
        return RiskLevel.CRITICAL  # >= 75
    
    async def _calculate_confidence(
        self,
        location: Location,
        hazard: Hazard
    ) -> float:
        """Calculate confidence level based on data availability.
        
        Args:
            location: Location object
            hazard: Hazard object
            
        Returns:
            Confidence level (0-1)
        """
        base_confidence = 0.5
        
        # Increase confidence if we have historical data
        result = await self.db.execute(
            select(func.count(HistoricalData.id))
            .where(
                HistoricalData.location_id == location.id,
                HistoricalData.hazard_id == hazard.id
            )
        )
        historical_count = result.scalar() or 0
        
        # Add up to 0.4 based on historical data (capped at 10+ events)
        historical_boost = min((historical_count / 10) * 0.4, 0.4)
        
        # Add 0.1 if location has detailed extra_data
        metadata_boost = 0.1 if location.extra_data else 0
        
        confidence = min(base_confidence + historical_boost + metadata_boost, 1.0)
        return round(confidence, 2)
    
    def _generate_recommendations(
        self,
        risk_score: float,
        risk_level: RiskLevel,
        hazard_type: HazardType,
        factors: Dict[str, float]
    ) -> List[str]:
        """Generate mitigation recommendations based on risk assessment.
        
        Args:
            risk_score: Calculated risk score
            risk_level: Determined risk level
            hazard_type: Type of hazard
            factors: Factor analysis
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # General recommendations based on risk level
        if risk_level == RiskLevel.CRITICAL:
            recommendations.append("CRITICAL: Immediate evacuation planning required")
            recommendations.append("Establish emergency response protocols")
        elif risk_level == RiskLevel.HIGH:
            recommendations.append("HIGH RISK: Develop comprehensive mitigation strategies")
            recommendations.append("Conduct regular safety drills")
        
        # Hazard-specific recommendations
        hazard_recommendations = {
            HazardType.EARTHQUAKE: [
                "Retrofit buildings to meet seismic standards",
                "Establish earthquake early warning systems",
                "Conduct structural assessments of critical infrastructure"
            ],
            HazardType.FLOOD: [
                "Improve drainage systems and flood barriers",
                "Implement flood warning systems",
                "Review and update flood zone mapping"
            ],
            HazardType.FIRE: [
                "Enhance fire detection and suppression systems",
                "Create firebreaks and defensible spaces",
                "Improve emergency access routes"
            ],
            HazardType.STORM: [
                "Strengthen building codes for wind resistance",
                "Improve power grid resilience",
                "Establish storm shelters"
            ]
        }
        
        if hazard_type in hazard_recommendations:
            recommendations.extend(hazard_recommendations[hazard_type][:2])
        
        # Factor-specific recommendations
        if factors['building_code_impact'] > 60:
            recommendations.append("Upgrade building codes and enforcement")
        
        if factors['infrastructure_impact'] > 60:
            recommendations.append("Invest in infrastructure modernization")
        
        if factors['population_density_impact'] > 70:
            recommendations.append("Develop density-specific emergency response plans")
        
        return recommendations[:5]  # Limit to top 5 recommendations

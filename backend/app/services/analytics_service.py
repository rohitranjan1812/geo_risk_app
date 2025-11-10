"""Advanced analytics service for comprehensive risk assessment."""
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
import statistics

from app.models import Location, Hazard, HazardType, RiskLevel, HistoricalData, RiskAssessment


class AdvancedAnalyticsService:
    """Service for advanced risk analysis including trends, patterns, and predictions."""
    
    def __init__(self, db: AsyncSession):
        """Initialize analytics service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def analyze_historical_trends(
        self,
        location: Location,
        hazard: Hazard,
        years: int = 10
    ) -> Dict[str, any]:
        """Analyze historical trends for a location-hazard pair.
        
        Args:
            location: Location object
            hazard: Hazard object
            years: Number of years to analyze
            
        Returns:
            Dictionary with trend analysis including frequency, severity, and patterns
        """
        start_date = datetime.utcnow() - timedelta(days=years*365)
        
        result = await self.db.execute(
            select(HistoricalData)
            .where(
                and_(
                    HistoricalData.location_id == location.id,
                    HistoricalData.hazard_id == hazard.id,
                    HistoricalData.event_date >= start_date
                )
            )
            .order_by(HistoricalData.event_date)
        )
        events = result.scalars().all()
        
        if not events:
            return {
                'event_count': 0,
                'trend': 'insufficient_data',
                'average_severity': 0.0,
                'max_severity': 0.0,
                'min_severity': 0.0,
                'std_deviation': 0.0,
                'frequency_per_year': 0.0,
                'total_casualties': 0,
                'total_economic_damage': 0.0
            }
        
        severities = [e.severity for e in events]
        casualties = [e.casualties or 0 for e in events]
        damages = [e.economic_damage or 0.0 for e in events]
        
        # Calculate trend direction (increasing, decreasing, stable)
        if len(events) > 1:
            first_half_avg = statistics.mean(severities[:len(severities)//2])
            second_half_avg = statistics.mean(severities[len(severities)//2:])
            
            if second_half_avg > first_half_avg * 1.2:
                trend = 'increasing'
            elif second_half_avg < first_half_avg * 0.8:
                trend = 'decreasing'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'event_count': len(events),
            'trend': trend,
            'average_severity': round(statistics.mean(severities), 2),
            'max_severity': max(severities),
            'min_severity': min(severities),
            'std_deviation': round(statistics.stdev(severities) if len(severities) > 1 else 0.0, 2),
            'frequency_per_year': round(len(events) / years, 2),
            'total_casualties': sum(casualties),
            'total_economic_damage': round(sum(damages), 2)
        }
    
    async def calculate_risk_hotspots(
        self,
        hazard: Hazard,
        limit: int = 20
    ) -> List[Dict[str, any]]:
        """Identify high-risk locations for a specific hazard.
        
        Args:
            hazard: Hazard object
            limit: Maximum number of hotspots to return
            
        Returns:
            List of locations sorted by risk score
        """
        result = await self.db.execute(
            select(
                RiskAssessment.location_id,
                Location.name,
                Location.latitude,
                Location.longitude,
                func.avg(RiskAssessment.risk_score).label('avg_risk')
            )
            .join(Location)
            .where(RiskAssessment.hazard_id == hazard.id)
            .group_by(RiskAssessment.location_id, Location.id)
            .order_by(func.avg(RiskAssessment.risk_score).desc())
            .limit(limit)
        )
        
        hotspots = []
        for row in result:
            hotspots.append({
                'location_id': row[0],
                'location_name': row[1],
                'latitude': row[2],
                'longitude': row[3],
                'risk_score': round(row[4], 2)
            })
        
        return hotspots
    
    async def compare_locations(
        self,
        location_ids: List[int],
        hazard_id: int
    ) -> Dict[int, Dict[str, any]]:
        """Compare risk profiles across multiple locations.
        
        Args:
            location_ids: List of location IDs
            hazard_id: Hazard ID to compare
            
        Returns:
            Dictionary mapping location IDs to their risk profiles
        """
        result = await self.db.execute(
            select(Location).where(Location.id.in_(location_ids))
        )
        locations = {l.id: l for l in result.scalars().all()}
        
        hazard_result = await self.db.execute(
            select(Hazard).where(Hazard.id == hazard_id)
        )
        hazard = hazard_result.scalar_one_or_none()
        
        comparison = {}
        for loc_id in location_ids:
            if loc_id not in locations:
                continue
            
            location = locations[loc_id]
            
            # Get latest risk assessment
            assess_result = await self.db.execute(
                select(RiskAssessment)
                .where(
                    and_(
                        RiskAssessment.location_id == loc_id,
                        RiskAssessment.hazard_id == hazard_id
                    )
                )
                .order_by(RiskAssessment.assessed_at.desc())
                .limit(1)
            )
            latest_assessment = assess_result.scalar_one_or_none()
            
            # Get historical trends
            trends = await self.analyze_historical_trends(location, hazard)
            
            comparison[loc_id] = {
                'location_name': location.name,
                'coordinates': {
                    'latitude': location.latitude,
                    'longitude': location.longitude
                },
                'infrastructure_factors': {
                    'population_density': location.population_density,
                    'building_code_rating': location.building_code_rating,
                    'infrastructure_quality': location.infrastructure_quality
                },
                'current_risk': {
                    'risk_score': latest_assessment.risk_score if latest_assessment else 0.0,
                    'risk_level': latest_assessment.risk_level if latest_assessment else 'unknown',
                    'confidence': latest_assessment.confidence_level if latest_assessment else 0.0,
                    'assessed_at': latest_assessment.assessed_at.isoformat() if latest_assessment else None
                },
                'historical_trends': trends
            }
        
        return comparison
    
    async def calculate_regional_risk_index(
        self,
        min_latitude: float,
        max_latitude: float,
        min_longitude: float,
        max_longitude: float,
        hazard_id: int | None = None
    ) -> Dict[str, any]:
        """Calculate aggregate risk for a geographic region.
        
        Args:
            min_latitude: Minimum latitude boundary
            max_latitude: Maximum latitude boundary
            min_longitude: Minimum longitude boundary
            max_longitude: Maximum longitude boundary
            hazard_id: Optional hazard ID to filter
            
        Returns:
            Regional risk index with statistics
        """
        query = select(RiskAssessment).join(Location).where(
            and_(
                Location.latitude >= min_latitude,
                Location.latitude <= max_latitude,
                Location.longitude >= min_longitude,
                Location.longitude <= max_longitude
            )
        )
        
        if hazard_id:
            query = query.where(RiskAssessment.hazard_id == hazard_id)
        
        result = await self.db.execute(query)
        assessments = result.scalars().all()
        
        if not assessments:
            return {
                'region': {
                    'bounds': {
                        'latitude': [min_latitude, max_latitude],
                        'longitude': [min_longitude, max_longitude]
                    }
                },
                'assessment_count': 0,
                'risk_statistics': {}
            }
        
        scores = [a.risk_score for a in assessments]
        
        risk_level_counts = {}
        for level in RiskLevel:
            count = sum(1 for a in assessments if a.risk_level == level)
            risk_level_counts[level.value] = count
        
        return {
            'region': {
                'bounds': {
                    'latitude': [min_latitude, max_latitude],
                    'longitude': [min_longitude, max_longitude]
                }
            },
            'assessment_count': len(assessments),
            'risk_statistics': {
                'average_risk_score': round(statistics.mean(scores), 2),
                'median_risk_score': round(statistics.median(scores), 2),
                'std_deviation': round(statistics.stdev(scores) if len(scores) > 1 else 0.0, 2),
                'min_risk_score': min(scores),
                'max_risk_score': max(scores),
                'risk_level_distribution': risk_level_counts
            }
        }
    
    async def forecast_risk_evolution(
        self,
        location: Location,
        hazard: Hazard,
        months_ahead: int = 12
    ) -> Dict[str, any]:
        """Forecast risk evolution over time using historical patterns.
        
        Args:
            location: Location object
            hazard: Hazard object
            months_ahead: Number of months to forecast
            
        Returns:
            Forecast data with confidence intervals
        """
        # Analyze historical trends
        trends = await self.analyze_historical_trends(location, hazard, years=5)
        
        # Simple trend-based forecast
        current_result = await self.db.execute(
            select(RiskAssessment)
            .where(
                and_(
                    RiskAssessment.location_id == location.id,
                    RiskAssessment.hazard_id == hazard.id
                )
            )
            .order_by(RiskAssessment.assessed_at.desc())
            .limit(1)
        )
        current_assessment = current_result.scalar_one_or_none()
        
        if not current_assessment:
            return {
                'location_id': location.id,
                'hazard_type': hazard.hazard_type.value,
                'forecast_period_months': months_ahead,
                'forecast': []
            }
        
        base_risk = current_assessment.risk_score
        trend_factor = 1.0
        
        if trends['trend'] == 'increasing':
            trend_factor = 1.02
        elif trends['trend'] == 'decreasing':
            trend_factor = 0.98
        
        forecast = []
        for month in range(1, months_ahead + 1):
            projected_risk = base_risk * (trend_factor ** month)
            projected_risk = min(max(projected_risk, 0), 100)
            
            forecast.append({
                'month_ahead': month,
                'projected_risk_score': round(projected_risk, 2),
                'confidence_interval': {
                    'lower': round(max(0, projected_risk - 5), 2),
                    'upper': round(min(100, projected_risk + 5), 2)
                }
            })
        
        return {
            'location_id': location.id,
            'location_name': location.name,
            'hazard_type': hazard.hazard_type.value,
            'forecast_period_months': months_ahead,
            'current_risk_score': base_risk,
            'trend': trends['trend'],
            'forecast': forecast
        }
    
    async def identify_critical_risk_factors(
        self,
        location: Location,
        hazard: Hazard
    ) -> List[Dict[str, any]]:
        """Identify and rank the most critical risk factors for a location-hazard pair.
        
        Args:
            location: Location object
            hazard: Hazard object
            
        Returns:
            List of risk factors ranked by impact
        """
        result = await self.db.execute(
            select(RiskAssessment)
            .where(
                and_(
                    RiskAssessment.location_id == location.id,
                    RiskAssessment.hazard_id == hazard.id
                )
            )
            .order_by(RiskAssessment.assessed_at.desc())
            .limit(1)
        )
        assessment = result.scalar_one_or_none()
        
        if not assessment or not assessment.factors_analysis:
            return []
        
        factors = assessment.factors_analysis
        ranked_factors = sorted(
            [
                {
                    'factor_name': name,
                    'impact_score': value,
                    'impact_percentage': round((value / 100) * 100, 1)
                }
                for name, value in factors.items()
            ],
            key=lambda x: x['impact_score'],
            reverse=True
        )
        
        return ranked_factors

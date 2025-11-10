"""Data export service for generating CSV reports and batch processing."""
import csv
import io
from typing import List, Dict, Any, Optional, AsyncGenerator, Tuple
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.models import (
    Location, RiskAssessment, Hazard, HistoricalData, 
    HazardType, RiskLevel
)
from app.services.risk_engine import RiskEngine


class DataTransformationPipeline:
    """Pipeline for transforming raw geographic data into risk assessment inputs."""
    
    @staticmethod
    def transform_coordinates(
        raw_coords: List[Dict[str, Any]]
    ) -> List[Dict[str, float]]:
        """Transform raw coordinate data into standardized format.
        
        Args:
            raw_coords: List of dictionaries with coordinate data
            
        Returns:
            List of standardized coordinate dictionaries
            
        Example:
            >>> raw = [{"lat": "37.7749", "lon": "-122.4194", "name": "SF"}]
            >>> transform_coordinates(raw)
            [{"latitude": 37.7749, "longitude": -122.4194, "name": "SF"}]
        """
        transformed = []
        for coord in raw_coords:
            try:
                # Handle various key formats
                lat = float(coord.get('lat') or coord.get('latitude') or coord.get('y'))
                lon = float(coord.get('lon') or coord.get('longitude') or coord.get('x'))
                
                # Validate ranges
                if not (-90 <= lat <= 90):
                    raise ValueError(f"Latitude {lat} out of range [-90, 90]")
                if not (-180 <= lon <= 180):
                    raise ValueError(f"Longitude {lon} out of range [-180, 180]")
                
                transformed.append({
                    'latitude': lat,
                    'longitude': lon,
                    'name': coord.get('name', f"Location_{lat}_{lon}"),
                    'population_density': float(coord.get('population_density', 0)),
                    'building_code_rating': float(coord.get('building_code_rating', 5.0)),
                    'infrastructure_quality': float(coord.get('infrastructure_quality', 5.0))
                })
            except (KeyError, TypeError, ValueError) as e:
                # Skip invalid entries but log them
                continue
                
        return transformed
    
    @staticmethod
    def enrich_with_defaults(
        location_data: Dict[str, Any],
        defaults: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Enrich location data with default values.
        
        Args:
            location_data: Raw location dictionary
            defaults: Optional default values to apply
            
        Returns:
            Enriched location dictionary
        """
        default_values = defaults or {
            'population_density': 0.0,
            'building_code_rating': 5.0,
            'infrastructure_quality': 5.0,
            'extra_data': {}
        }
        
        enriched = location_data.copy()
        for key, value in default_values.items():
            if key not in enriched or enriched[key] is None:
                enriched[key] = value
                
        return enriched
    
    @staticmethod
    def normalize_hazard_types(
        hazard_input: List[str]
    ) -> List[HazardType]:
        """Normalize hazard type strings to enum values.
        
        Args:
            hazard_input: List of hazard type strings
            
        Returns:
            List of HazardType enum values
        """
        normalized = []
        valid_types = {ht.value: ht for ht in HazardType}
        
        for hazard_str in hazard_input:
            hazard_lower = hazard_str.lower().strip()
            if hazard_lower in valid_types:
                normalized.append(valid_types[hazard_lower])
            elif hazard_lower == 'wildfire':
                normalized.append(HazardType.FIRE)
            elif hazard_lower in ['hurricane', 'tornado', 'cyclone']:
                normalized.append(HazardType.STORM)
                
        return normalized or [HazardType.EARTHQUAKE, HazardType.FLOOD, HazardType.FIRE, HazardType.STORM]


class ExportService:
    """Service for exporting risk assessment data to CSV and other formats."""
    
    # CSV column definitions
    RISK_REPORT_COLUMNS = [
        'assessment_id',
        'location_id',
        'location_name',
        'latitude',
        'longitude',
        'hazard_type',
        'risk_score',
        'risk_level',
        'confidence_level',
        'population_density',
        'building_code_rating',
        'infrastructure_quality',
        'assessed_at',
        'recommendations'
    ]
    
    BATCH_SIZE = 500  # Number of records to process at once for memory efficiency
    
    def __init__(self, db: AsyncSession):
        """Initialize export service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.transformer = DataTransformationPipeline()
        self.risk_engine = RiskEngine()
    
    async def generate_risk_report_csv(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        location_bounds: Optional[Dict[str, float]] = None,
        hazard_types: Optional[List[HazardType]] = None,
        min_risk_score: Optional[float] = None,
        risk_levels: Optional[List[RiskLevel]] = None,
        location_ids: Optional[List[int]] = None
    ) -> str:
        """Generate CSV report of risk assessments with filters.
        
        Args:
            start_date: Filter by assessments after this date
            end_date: Filter by assessments before this date
            location_bounds: Geographic bounding box {min_lat, max_lat, min_lon, max_lon}
            hazard_types: Filter by specific hazard types
            min_risk_score: Minimum risk score threshold
            risk_levels: Filter by risk levels
            location_ids: Specific location IDs to include
            
        Returns:
            CSV string with risk assessment data
        """
        # Build query with filters
        query = (
            select(RiskAssessment)
            .options(
                selectinload(RiskAssessment.location),
                selectinload(RiskAssessment.hazard)
            )
        )
        
        filters = []
        
        if start_date:
            filters.append(RiskAssessment.assessed_at >= start_date)
        if end_date:
            filters.append(RiskAssessment.assessed_at <= end_date)
        if min_risk_score is not None:
            filters.append(RiskAssessment.risk_score >= min_risk_score)
        if risk_levels:
            filters.append(RiskAssessment.risk_level.in_(risk_levels))
        if location_ids:
            filters.append(RiskAssessment.location_id.in_(location_ids))
            
        if filters:
            query = query.where(and_(*filters))
        
        # Join with Location for geographic filtering
        if location_bounds:
            query = query.join(Location).where(
                and_(
                    Location.latitude >= location_bounds.get('min_lat', -90),
                    Location.latitude <= location_bounds.get('max_lat', 90),
                    Location.longitude >= location_bounds.get('min_lon', -180),
                    Location.longitude <= location_bounds.get('max_lon', 180)
                )
            )
        
        # Join with Hazard for hazard type filtering
        if hazard_types:
            query = query.join(Hazard).where(Hazard.hazard_type.in_(hazard_types))
        
        query = query.order_by(RiskAssessment.assessed_at.desc())
        
        # Execute query
        result = await self.db.execute(query)
        assessments = result.scalars().all()
        
        # Generate CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=self.RISK_REPORT_COLUMNS)
        writer.writeheader()
        
        for assessment in assessments:
            writer.writerow(self._assessment_to_csv_row(assessment))
        
        return output.getvalue()
    
    async def stream_risk_report_csv(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        location_bounds: Optional[Dict[str, float]] = None,
        hazard_types: Optional[List[HazardType]] = None,
        min_risk_score: Optional[float] = None,
        risk_levels: Optional[List[RiskLevel]] = None,
        location_ids: Optional[List[int]] = None
    ) -> AsyncGenerator[str, None]:
        """Stream CSV report in chunks for large datasets.
        
        This method uses pagination to handle datasets exceeding memory limits.
        It yields CSV data in batches for streaming responses.
        
        Args:
            Same as generate_risk_report_csv
            
        Yields:
            CSV chunks as strings
        """
        # Build base query
        query = (
            select(RiskAssessment)
            .options(
                selectinload(RiskAssessment.location),
                selectinload(RiskAssessment.hazard)
            )
        )
        
        filters = []
        
        if start_date:
            filters.append(RiskAssessment.assessed_at >= start_date)
        if end_date:
            filters.append(RiskAssessment.assessed_at <= end_date)
        if min_risk_score is not None:
            filters.append(RiskAssessment.risk_score >= min_risk_score)
        if risk_levels:
            filters.append(RiskAssessment.risk_level.in_(risk_levels))
        if location_ids:
            filters.append(RiskAssessment.location_id.in_(location_ids))
            
        if filters:
            query = query.where(and_(*filters))
        
        if location_bounds:
            query = query.join(Location).where(
                and_(
                    Location.latitude >= location_bounds.get('min_lat', -90),
                    Location.latitude <= location_bounds.get('max_lat', 90),
                    Location.longitude >= location_bounds.get('min_lon', -180),
                    Location.longitude <= location_bounds.get('max_lon', 180)
                )
            )
        
        if hazard_types:
            query = query.join(Hazard).where(Hazard.hazard_type.in_(hazard_types))
        
        query = query.order_by(RiskAssessment.id)
        
        # Yield header first
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=self.RISK_REPORT_COLUMNS)
        writer.writeheader()
        yield output.getvalue()
        
        # Stream data in batches
        offset = 0
        while True:
            batch_query = query.limit(self.BATCH_SIZE).offset(offset)
            result = await self.db.execute(batch_query)
            batch = result.scalars().all()
            
            if not batch:
                break
            
            # Generate CSV for this batch
            batch_output = io.StringIO()
            batch_writer = csv.DictWriter(batch_output, fieldnames=self.RISK_REPORT_COLUMNS)
            
            for assessment in batch:
                batch_writer.writerow(self._assessment_to_csv_row(assessment))
            
            yield batch_output.getvalue()
            
            offset += self.BATCH_SIZE
            
            # Stop if batch was smaller than BATCH_SIZE (last batch)
            if len(batch) < self.BATCH_SIZE:
                break
    
    async def batch_process_locations(
        self,
        coordinates: List[Dict[str, Any]],
        hazard_types: Optional[List[HazardType]] = None,
        save_to_db: bool = True
    ) -> List[Dict[str, Any]]:
        """Batch process multiple locations for risk assessment.
        
        Args:
            coordinates: List of coordinate dictionaries
            hazard_types: Hazard types to assess (default: all)
            save_to_db: Whether to save results to database
            
        Returns:
            List of assessment results
        """
        # Transform and validate coordinates
        transformed = self.transformer.transform_coordinates(coordinates)
        
        if not transformed:
            return []
        
        # Default to all hazard types if not specified
        if not hazard_types:
            hazard_types = [HazardType.EARTHQUAKE, HazardType.FLOOD, HazardType.FIRE, HazardType.STORM]
        
        # Get or create hazards
        hazards_query = select(Hazard).where(Hazard.hazard_type.in_(hazard_types))
        result = await self.db.execute(hazards_query)
        hazards = {h.hazard_type: h for h in result.scalars().all()}
        
        results = []
        
        # Process in batches to avoid memory issues
        for i in range(0, len(transformed), self.BATCH_SIZE):
            batch = transformed[i:i + self.BATCH_SIZE]
            
            for loc_data in batch:
                # Create or get location
                location = Location(
                    name=loc_data['name'],
                    latitude=loc_data['latitude'],
                    longitude=loc_data['longitude'],
                    population_density=loc_data['population_density'],
                    building_code_rating=loc_data['building_code_rating'],
                    infrastructure_quality=loc_data['infrastructure_quality']
                )
                
                if save_to_db:
                    self.db.add(location)
                    await self.db.flush()  # Get ID without committing
                
                # Assess risk for each hazard type
                location_results = {
                    'location': {
                        'name': location.name,
                        'latitude': location.latitude,
                        'longitude': location.longitude,
                        'id': location.id if save_to_db else None
                    },
                    'assessments': []
                }
                
                for hazard_type in hazard_types:
                    hazard = hazards.get(hazard_type)
                    if not hazard:
                        continue
                    
                    # Calculate risk using engine
                    risk_score, risk_level, confidence = await self._calculate_risk_for_location(
                        location, hazard
                    )
                    
                    assessment_data = {
                        'hazard_type': hazard_type.value,
                        'risk_score': round(risk_score, 2),
                        'risk_level': risk_level.value,
                        'confidence_level': round(confidence, 2)
                    }
                    
                    if save_to_db:
                        assessment = RiskAssessment(
                            location_id=location.id,
                            hazard_id=hazard.id,
                            risk_score=risk_score,
                            risk_level=risk_level,
                            confidence_level=confidence,
                            assessed_at=datetime.utcnow()
                        )
                        self.db.add(assessment)
                        assessment_data['id'] = assessment.id
                    
                    location_results['assessments'].append(assessment_data)
                
                # Calculate overall risk
                if location_results['assessments']:
                    avg_score = sum(a['risk_score'] for a in location_results['assessments']) / len(location_results['assessments'])
                    location_results['overall_risk_score'] = round(avg_score, 2)
                    location_results['overall_risk_level'] = self._determine_risk_level(avg_score).value
                
                results.append(location_results)
            
            if save_to_db:
                await self.db.commit()
        
        return results
    
    async def export_historical_trends(
        self,
        location_id: int,
        hazard_type: HazardType,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> str:
        """Export historical trend data for a location and hazard type.
        
        Args:
            location_id: Location ID
            hazard_type: Hazard type to analyze
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            CSV string with historical trend data
        """
        # Get historical events
        query = (
            select(HistoricalData)
            .join(Hazard)
            .where(
                and_(
                    HistoricalData.location_id == location_id,
                    Hazard.hazard_type == hazard_type
                )
            )
        )
        
        if start_date:
            query = query.where(HistoricalData.event_date >= start_date)
        if end_date:
            query = query.where(HistoricalData.event_date <= end_date)
        
        query = query.order_by(HistoricalData.event_date)
        
        result = await self.db.execute(query)
        events = result.scalars().all()
        
        # Generate CSV
        columns = [
            'event_id', 'event_date', 'severity', 'casualties',
            'economic_damage', 'impact_description'
        ]
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        
        for event in events:
            writer.writerow({
                'event_id': event.id,
                'event_date': event.event_date.isoformat(),
                'severity': event.severity,
                'casualties': event.casualties or 0,
                'economic_damage': event.economic_damage or 0.0,
                'impact_description': event.impact_description or ''
            })
        
        return output.getvalue()
    
    async def _calculate_risk_for_location(
        self,
        location: Location,
        hazard: Hazard
    ) -> Tuple[float, RiskLevel, float]:
        """Calculate risk score for a location-hazard pair.
        
        Args:
            location: Location object
            hazard: Hazard object
            
        Returns:
            Tuple of (risk_score, risk_level, confidence)
        """
        # Simplified risk calculation for export service
        # Uses location characteristics and hazard severity
        
        base_score = hazard.base_severity * 10  # Scale to 0-100
        
        # Adjust based on location factors
        pop_factor = min(location.population_density / 10000, 1.0) * 15
        building_factor = (10 - location.building_code_rating) * 5  # Inverse relationship
        infra_factor = (10 - location.infrastructure_quality) * 3  # Inverse relationship
        
        # Calculate final score
        risk_score = base_score + pop_factor + building_factor + infra_factor
        risk_score = min(max(risk_score, 0), 100)  # Clamp to 0-100
        
        # Base confidence on data availability
        confidence = 0.7
        if location.population_density > 0:
            confidence += 0.1
        if location.building_code_rating != 5.0:  # Non-default value
            confidence += 0.1
        confidence = min(confidence, 1.0)
        
        risk_level = self._determine_risk_level(risk_score)
        
        return risk_score, risk_level, confidence
    
    def _assessment_to_csv_row(self, assessment: RiskAssessment) -> Dict[str, Any]:
        """Convert risk assessment to CSV row dictionary.
        
        Args:
            assessment: RiskAssessment object with loaded relationships
            
        Returns:
            Dictionary with CSV row data
        """
        location = assessment.location
        hazard = assessment.hazard
        
        # Format recommendations
        recommendations = ''
        if assessment.recommendations:
            if isinstance(assessment.recommendations, list):
                recommendations = '; '.join(assessment.recommendations)
            else:
                recommendations = str(assessment.recommendations)
        
        return {
            'assessment_id': assessment.id,
            'location_id': location.id,
            'location_name': location.name,
            'latitude': location.latitude,
            'longitude': location.longitude,
            'hazard_type': hazard.hazard_type.value,
            'risk_score': round(assessment.risk_score, 2),
            'risk_level': assessment.risk_level.value,
            'confidence_level': round(assessment.confidence_level, 2),
            'population_density': location.population_density,
            'building_code_rating': location.building_code_rating,
            'infrastructure_quality': location.infrastructure_quality,
            'assessed_at': assessment.assessed_at.isoformat(),
            'recommendations': recommendations
        }
    
    @staticmethod
    def _determine_risk_level(risk_score: float) -> RiskLevel:
        """Determine risk level from numeric score.
        
        Args:
            risk_score: Numeric risk score (0-100)
            
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

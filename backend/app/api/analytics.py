"""API endpoints for advanced risk analytics."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db
from app.models import Location, Hazard
from app.services import AdvancedAnalyticsService
from app.schemas import LocationResponse

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/hotspots/{hazard_id}", status_code=status.HTTP_200_OK)
async def get_risk_hotspots(
    hazard_id: int,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Get high-risk locations for a specific hazard.
    
    Args:
        hazard_id: Hazard ID
        limit: Maximum number of hotspots to return
        db: Database session
        
    Returns:
        List of high-risk locations sorted by risk score
        
    Raises:
        HTTPException: If hazard not found
    """
    result = await db.execute(
        select(Hazard).where(Hazard.id == hazard_id)
    )
    hazard = result.scalar_one_or_none()
    
    if not hazard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hazard with id {hazard_id} not found"
        )
    
    analytics = AdvancedAnalyticsService(db)
    hotspots = await analytics.calculate_risk_hotspots(hazard, limit)
    
    return {
        'hazard_type': hazard.hazard_type.value,
        'hotspot_count': len(hotspots),
        'hotspots': hotspots
    }


@router.get("/trends/{location_id}/{hazard_id}", status_code=status.HTTP_200_OK)
async def get_historical_trends(
    location_id: int,
    hazard_id: int,
    years: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Get historical trends for a location-hazard pair.
    
    Args:
        location_id: Location ID
        hazard_id: Hazard ID
        years: Number of years to analyze
        db: Database session
        
    Returns:
        Trend analysis with frequency, severity, and patterns
        
    Raises:
        HTTPException: If location or hazard not found
    """
    result = await db.execute(
        select(Location).where(Location.id == location_id)
    )
    location = result.scalar_one_or_none()
    
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with id {location_id} not found"
        )
    
    result = await db.execute(
        select(Hazard).where(Hazard.id == hazard_id)
    )
    hazard = result.scalar_one_or_none()
    
    if not hazard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hazard with id {hazard_id} not found"
        )
    
    analytics = AdvancedAnalyticsService(db)
    trends = await analytics.analyze_historical_trends(location, hazard, years)
    
    return {
        'location': LocationResponse.model_validate(location),
        'hazard_type': hazard.hazard_type.value,
        'analysis_years': years,
        'trends': trends
    }


@router.post("/compare-locations", status_code=status.HTTP_200_OK)
async def compare_locations(
    location_ids: List[int] = Query(...),
    hazard_id: int = Query(...),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Compare risk profiles across multiple locations.
    
    Args:
        location_ids: List of location IDs to compare
        hazard_id: Hazard ID for comparison
        db: Database session
        
    Returns:
        Comparative risk profiles
        
    Raises:
        HTTPException: If invalid locations or hazard
    """
    result = await db.execute(
        select(Hazard).where(Hazard.id == hazard_id)
    )
    hazard = result.scalar_one_or_none()
    
    if not hazard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hazard with id {hazard_id} not found"
        )
    
    analytics = AdvancedAnalyticsService(db)
    comparison = await analytics.compare_locations(location_ids, hazard_id)
    
    return {
        'hazard_type': hazard.hazard_type.value,
        'locations_compared': len(comparison),
        'comparison': comparison
    }


@router.get("/regional-risk", status_code=status.HTTP_200_OK)
async def get_regional_risk_index(
    min_latitude: float = Query(...),
    max_latitude: float = Query(...),
    min_longitude: float = Query(...),
    max_longitude: float = Query(...),
    hazard_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Calculate aggregate risk for a geographic region.
    
    Args:
        min_latitude: Minimum latitude boundary
        max_latitude: Maximum latitude boundary
        min_longitude: Minimum longitude boundary
        max_longitude: Maximum longitude boundary
        hazard_id: Optional hazard ID to filter
        db: Database session
        
    Returns:
        Regional risk statistics
        
    Raises:
        HTTPException: If invalid coordinates or hazard
    """
    if min_latitude >= max_latitude or min_longitude >= max_longitude:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid coordinate boundaries"
        )
    
    if hazard_id:
        result = await db.execute(
            select(Hazard).where(Hazard.id == hazard_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Hazard with id {hazard_id} not found"
            )
    
    analytics = AdvancedAnalyticsService(db)
    regional_risk = await analytics.calculate_regional_risk_index(
        min_latitude, max_latitude, min_longitude, max_longitude, hazard_id
    )
    
    return regional_risk


@router.get("/forecast/{location_id}/{hazard_id}", status_code=status.HTTP_200_OK)
async def get_risk_forecast(
    location_id: int,
    hazard_id: int,
    months_ahead: int = Query(12, ge=1, le=60),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Forecast risk evolution over time.
    
    Args:
        location_id: Location ID
        hazard_id: Hazard ID
        months_ahead: Number of months to forecast
        db: Database session
        
    Returns:
        Risk forecast with projections
        
    Raises:
        HTTPException: If location or hazard not found
    """
    result = await db.execute(
        select(Location).where(Location.id == location_id)
    )
    location = result.scalar_one_or_none()
    
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with id {location_id} not found"
        )
    
    result = await db.execute(
        select(Hazard).where(Hazard.id == hazard_id)
    )
    hazard = result.scalar_one_or_none()
    
    if not hazard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hazard with id {hazard_id} not found"
        )
    
    analytics = AdvancedAnalyticsService(db)
    forecast = await analytics.forecast_risk_evolution(location, hazard, months_ahead)
    
    return forecast


@router.get("/critical-factors/{location_id}/{hazard_id}", status_code=status.HTTP_200_OK)
async def get_critical_risk_factors(
    location_id: int,
    hazard_id: int,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Identify critical risk factors for a location-hazard pair.
    
    Args:
        location_id: Location ID
        hazard_id: Hazard ID
        db: Database session
        
    Returns:
        List of critical factors ranked by impact
        
    Raises:
        HTTPException: If location or hazard not found
    """
    result = await db.execute(
        select(Location).where(Location.id == location_id)
    )
    location = result.scalar_one_or_none()
    
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with id {location_id} not found"
        )
    
    result = await db.execute(
        select(Hazard).where(Hazard.id == hazard_id)
    )
    hazard = result.scalar_one_or_none()
    
    if not hazard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hazard with id {hazard_id} not found"
        )
    
    analytics = AdvancedAnalyticsService(db)
    factors = await analytics.identify_critical_risk_factors(location, hazard)
    
    return {
        'location_name': location.name,
        'hazard_type': hazard.hazard_type.value,
        'critical_factors_count': len(factors),
        'critical_factors': factors
    }

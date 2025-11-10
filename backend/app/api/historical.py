"""API endpoints for historical data."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db import get_db
from app.models import HistoricalData, Location, Hazard
from app.schemas import HistoricalDataCreate, HistoricalDataResponse

router = APIRouter(prefix="/historical-data", tags=["Historical Data"])


@router.post("", response_model=HistoricalDataResponse, status_code=status.HTTP_201_CREATED)
async def create_historical_data(
    data: HistoricalDataCreate,
    db: AsyncSession = Depends(get_db)
) -> HistoricalDataResponse:
    """Create a new historical event record.
    
    Args:
        data: Historical data creation payload
        db: Database session
        
    Returns:
        Created historical data record
        
    Raises:
        HTTPException: If location or hazard not found
    """
    # Verify location exists
    result = await db.execute(
        select(Location).where(Location.id == data.location_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with id {data.location_id} not found"
        )
    
    # Verify hazard exists
    result = await db.execute(
        select(Hazard).where(Hazard.id == data.hazard_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hazard with id {data.hazard_id} not found"
        )
    
    historical = HistoricalData(**data.model_dump())
    db.add(historical)
    await db.commit()
    await db.refresh(historical)
    
    return HistoricalDataResponse.model_validate(historical)


@router.get("/{location_id}", response_model=List[HistoricalDataResponse])
async def get_historical_data_by_location(
    location_id: int,
    hazard_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
) -> List[HistoricalDataResponse]:
    """Get historical data for a specific location.
    
    Args:
        location_id: Location ID
        hazard_id: Optional hazard ID to filter by
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of historical data records
        
    Raises:
        HTTPException: If location not found
    """
    # Verify location exists
    result = await db.execute(
        select(Location).where(Location.id == location_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with id {location_id} not found"
        )
    
    # Build query
    query = select(HistoricalData).where(HistoricalData.location_id == location_id)
    
    if hazard_id is not None:
        query = query.where(HistoricalData.hazard_id == hazard_id)
    
    query = query.order_by(HistoricalData.event_date.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    historical_data = result.scalars().all()
    
    return [HistoricalDataResponse.model_validate(h) for h in historical_data]


@router.get("", response_model=List[HistoricalDataResponse])
async def get_all_historical_data(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
) -> List[HistoricalDataResponse]:
    """Get all historical data records.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of historical data records
    """
    result = await db.execute(
        select(HistoricalData)
        .order_by(HistoricalData.event_date.desc())
        .offset(skip)
        .limit(limit)
    )
    historical_data = result.scalars().all()
    
    return [HistoricalDataResponse.model_validate(h) for h in historical_data]

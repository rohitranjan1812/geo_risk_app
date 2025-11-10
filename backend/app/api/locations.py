"""API endpoints for locations."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db
from app.models import Location
from app.schemas import LocationCreate, LocationUpdate, LocationResponse, MessageResponse

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.post("", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_location(
    location_data: LocationCreate,
    db: AsyncSession = Depends(get_db)
) -> LocationResponse:
    """Create a new location.
    
    Args:
        location_data: Location creation data
        db: Database session
        
    Returns:
        Created location
    """
    location = Location(**location_data.model_dump())
    db.add(location)
    await db.commit()
    await db.refresh(location)
    
    return LocationResponse.model_validate(location)


@router.get("", response_model=List[LocationResponse])
async def get_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
) -> List[LocationResponse]:
    """Get all locations with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of locations
    """
    result = await db.execute(
        select(Location).offset(skip).limit(limit)
    )
    locations = result.scalars().all()
    
    return [LocationResponse.model_validate(loc) for loc in locations]


@router.get("/{location_id}", response_model=LocationResponse)
async def get_location(
    location_id: int,
    db: AsyncSession = Depends(get_db)
) -> LocationResponse:
    """Get a specific location by ID.
    
    Args:
        location_id: Location ID
        db: Database session
        
    Returns:
        Location details
        
    Raises:
        HTTPException: If location not found
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
    
    return LocationResponse.model_validate(location)


@router.put("/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: int,
    location_data: LocationUpdate,
    db: AsyncSession = Depends(get_db)
) -> LocationResponse:
    """Update a location.
    
    Args:
        location_id: Location ID
        location_data: Updated location data
        db: Database session
        
    Returns:
        Updated location
        
    Raises:
        HTTPException: If location not found
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
    
    # Update fields
    update_data = location_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(location, field, value)
    
    await db.commit()
    await db.refresh(location)
    
    return LocationResponse.model_validate(location)


@router.delete("/{location_id}", response_model=MessageResponse)
async def delete_location(
    location_id: int,
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """Delete a location.
    
    Args:
        location_id: Location ID
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If location not found
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
    
    await db.delete(location)
    await db.commit()
    
    return MessageResponse(message=f"Location {location_id} deleted successfully")

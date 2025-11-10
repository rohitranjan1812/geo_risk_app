"""API endpoints for hazards."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db
from app.models import Hazard
from app.schemas import HazardCreate, HazardResponse

router = APIRouter(prefix="/hazards", tags=["Hazards"])


@router.post("", response_model=HazardResponse, status_code=status.HTTP_201_CREATED)
async def create_hazard(
    hazard_data: HazardCreate,
    db: AsyncSession = Depends(get_db)
) -> HazardResponse:
    """Create a new hazard type configuration.
    
    Args:
        hazard_data: Hazard creation data
        db: Database session
        
    Returns:
        Created hazard
        
    Raises:
        HTTPException: If hazard type already exists
    """
    # Check if hazard type already exists
    result = await db.execute(
        select(Hazard).where(Hazard.hazard_type == hazard_data.hazard_type)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Hazard type {hazard_data.hazard_type} already exists"
        )
    
    hazard = Hazard(**hazard_data.model_dump())
    db.add(hazard)
    await db.commit()
    await db.refresh(hazard)
    
    return HazardResponse.model_validate(hazard)


@router.get("", response_model=List[HazardResponse])
async def get_hazards(
    db: AsyncSession = Depends(get_db)
) -> List[HazardResponse]:
    """Get all configured hazard types.
    
    Args:
        db: Database session
        
    Returns:
        List of hazards
    """
    result = await db.execute(select(Hazard))
    hazards = result.scalars().all()
    
    return [HazardResponse.model_validate(h) for h in hazards]


@router.get("/{hazard_id}", response_model=HazardResponse)
async def get_hazard(
    hazard_id: int,
    db: AsyncSession = Depends(get_db)
) -> HazardResponse:
    """Get a specific hazard by ID.
    
    Args:
        hazard_id: Hazard ID
        db: Database session
        
    Returns:
        Hazard details
        
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
    
    return HazardResponse.model_validate(hazard)

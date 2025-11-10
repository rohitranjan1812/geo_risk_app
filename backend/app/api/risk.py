"""API endpoints for risk assessment."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db
from app.models import Location, Hazard, RiskAssessment, HazardType, RiskLevel
from app.schemas import (
    RiskAssessmentRequest,
    RiskAssessmentResponse,
    RiskAssessmentBatchResponse,
    LocationResponse,
    LocationCreate
)
from app.services import RiskCalculationService

router = APIRouter(prefix="/assess-risk", tags=["Risk Assessment"])


@router.post("", response_model=RiskAssessmentBatchResponse, status_code=status.HTTP_200_OK)
async def assess_risk(
    request: RiskAssessmentRequest,
    db: AsyncSession = Depends(get_db)
) -> RiskAssessmentBatchResponse:
    """Assess risk for a location across multiple hazard types.
    
    Args:
        request: Risk assessment request with location and hazard types
        db: Database session
        
    Returns:
        Batch risk assessment with individual assessments for each hazard
        
    Raises:
        HTTPException: If location not found or hazard types invalid
    """
    # Get or create location
    if request.location_id:
        result = await db.execute(
            select(Location).where(Location.id == request.location_id)
        )
        location = result.scalar_one_or_none()
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location with id {request.location_id} not found"
            )
    elif request.location:
        # Create new location
        location = Location(**request.location.model_dump())
        db.add(location)
        await db.flush()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either location_id or location data must be provided"
        )
    
    # Override location factors if provided in request
    custom_factors = None
    if request.risk_factors:
        custom_factors = {
            'population_density': request.risk_factors.population_density,
            'building_code_rating': request.risk_factors.building_code_rating,
            'infrastructure_quality': request.risk_factors.infrastructure_quality
        }
        # Remove None values
        custom_factors = {k: v for k, v in custom_factors.items() if v is not None}
    
    # Get hazard objects
    result = await db.execute(
        select(Hazard).where(Hazard.hazard_type.in_(request.hazard_types))
    )
    hazards = result.scalars().all()
    
    if len(hazards) != len(request.hazard_types):
        found_types = {h.hazard_type for h in hazards}
        missing_types = set(request.hazard_types) - found_types
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hazard types not found: {missing_types}"
        )
    
    # Calculate risk for each hazard
    risk_service = RiskCalculationService(db)
    assessments = []
    total_risk_score = 0
    
    for hazard in hazards:
        risk_score, risk_level, confidence, factors_analysis, recommendations = \
            await risk_service.calculate_risk(location, hazard, custom_factors)
        
        # Create risk assessment record
        assessment = RiskAssessment(
            location_id=location.id,
            hazard_id=hazard.id,
            risk_score=risk_score,
            risk_level=risk_level,
            confidence_level=confidence,
            factors_analysis=factors_analysis,
            recommendations=recommendations
        )
        db.add(assessment)
        await db.flush()
        
        # Add to response
        assessments.append(
            RiskAssessmentResponse(
                id=assessment.id,
                location_id=location.id,
                hazard_id=hazard.id,
                hazard_type=hazard.hazard_type,
                risk_score=risk_score,
                risk_level=risk_level,
                confidence_level=confidence,
                factors_analysis=factors_analysis,
                recommendations=recommendations,
                assessed_at=assessment.assessed_at
            )
        )
        total_risk_score += risk_score
    
    # Calculate overall risk
    overall_risk_score = round(total_risk_score / len(assessments), 2)
    overall_risk_level = risk_service._determine_risk_level(overall_risk_score)
    
    await db.commit()
    
    return RiskAssessmentBatchResponse(
        location=LocationResponse.model_validate(location),
        assessments=assessments,
        overall_risk_score=overall_risk_score,
        overall_risk_level=overall_risk_level
    )

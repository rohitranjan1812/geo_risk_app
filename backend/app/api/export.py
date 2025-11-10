"""API endpoints for data export functionality."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.db import get_db
from app.models import HazardType, RiskLevel
from app.services.export_service import ExportService


router = APIRouter(prefix="/export", tags=["Export"])


# Request/Response Schemas
class LocationBounds(BaseModel):
    """Geographic bounding box for filtering."""
    min_lat: float = Field(..., ge=-90, le=90, description="Minimum latitude")
    max_lat: float = Field(..., ge=-90, le=90, description="Maximum latitude")
    min_lon: float = Field(..., ge=-180, le=180, description="Minimum longitude")
    max_lon: float = Field(..., ge=-180, le=180, description="Maximum longitude")


class RiskReportRequest(BaseModel):
    """Request schema for risk report export."""
    start_date: Optional[datetime] = Field(None, description="Filter assessments after this date")
    end_date: Optional[datetime] = Field(None, description="Filter assessments before this date")
    location_bounds: Optional[LocationBounds] = Field(None, description="Geographic bounding box")
    hazard_types: Optional[List[HazardType]] = Field(None, description="Filter by hazard types")
    min_risk_score: Optional[float] = Field(None, ge=0, le=100, description="Minimum risk score")
    risk_levels: Optional[List[RiskLevel]] = Field(None, description="Filter by risk levels")
    location_ids: Optional[List[int]] = Field(None, description="Specific location IDs")
    stream: bool = Field(default=False, description="Use streaming for large datasets")


class BatchLocationRequest(BaseModel):
    """Request schema for batch location processing."""
    coordinates: List[Dict[str, Any]] = Field(
        ...,
        min_length=1,
        description="List of coordinate dictionaries with lat/lon and optional metadata"
    )
    hazard_types: Optional[List[HazardType]] = Field(
        None,
        description="Hazard types to assess (default: all)"
    )
    save_to_db: bool = Field(
        default=True,
        description="Whether to save results to database"
    )


class BatchProcessingResponse(BaseModel):
    """Response schema for batch processing."""
    total_processed: int
    successful: int
    failed: int
    results: List[Dict[str, Any]]


class HistoricalTrendsRequest(BaseModel):
    """Request schema for historical trends export."""
    location_id: int
    hazard_type: HazardType
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


@router.post("/risk-report", status_code=status.HTTP_200_OK)
async def export_risk_report(
    request: RiskReportRequest,
    db: AsyncSession = Depends(get_db)
):
    """Export risk assessment report as CSV.
    
    This endpoint generates a CSV report of risk assessments with various filters.
    Use stream=true for large datasets to avoid memory issues.
    
    Args:
        request: Export parameters including filters and streaming option
        db: Database session
        
    Returns:
        CSV file as streaming response or direct download
        
    Example:
        POST /api/export/risk-report
        {
            "start_date": "2024-01-01T00:00:00",
            "hazard_types": ["earthquake", "flood"],
            "min_risk_score": 50,
            "stream": true
        }
    """
    export_service = ExportService(db)
    
    # Convert location bounds to dict if provided
    location_bounds = None
    if request.location_bounds:
        location_bounds = {
            'min_lat': request.location_bounds.min_lat,
            'max_lat': request.location_bounds.max_lat,
            'min_lon': request.location_bounds.min_lon,
            'max_lon': request.location_bounds.max_lon
        }
    
    try:
        if request.stream:
            # Use streaming for large datasets
            async def csv_generator():
                async for chunk in export_service.stream_risk_report_csv(
                    start_date=request.start_date,
                    end_date=request.end_date,
                    location_bounds=location_bounds,
                    hazard_types=request.hazard_types,
                    min_risk_score=request.min_risk_score,
                    risk_levels=request.risk_levels,
                    location_ids=request.location_ids
                ):
                    yield chunk
            
            return StreamingResponse(
                csv_generator(),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=risk_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
                }
            )
        else:
            # Generate complete CSV in memory
            csv_data = await export_service.generate_risk_report_csv(
                start_date=request.start_date,
                end_date=request.end_date,
                location_bounds=location_bounds,
                hazard_types=request.hazard_types,
                min_risk_score=request.min_risk_score,
                risk_levels=request.risk_levels,
                location_ids=request.location_ids
            )
            
            return StreamingResponse(
                iter([csv_data]),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=risk_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
                }
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.post("/batch-process", response_model=BatchProcessingResponse, status_code=status.HTTP_200_OK)
async def batch_process_locations(
    request: BatchLocationRequest,
    db: AsyncSession = Depends(get_db)
) -> BatchProcessingResponse:
    """Batch process multiple locations for risk assessment.
    
    This endpoint accepts a list of coordinates and processes them in batches,
    calculating risk scores for specified hazard types.
    
    Args:
        request: Batch processing parameters with coordinates and options
        db: Database session
        
    Returns:
        Processing results with success/failure counts
        
    Example:
        POST /api/export/batch-process
        {
            "coordinates": [
                {"lat": 37.7749, "lon": -122.4194, "name": "San Francisco"},
                {"lat": 34.0522, "lon": -118.2437, "name": "Los Angeles"}
            ],
            "hazard_types": ["earthquake", "fire"],
            "save_to_db": true
        }
    """
    export_service = ExportService(db)
    
    try:
        results = await export_service.batch_process_locations(
            coordinates=request.coordinates,
            hazard_types=request.hazard_types,
            save_to_db=request.save_to_db
        )
        
        # Count successes and failures
        successful = sum(1 for r in results if r.get('assessments'))
        failed = len(results) - successful
        
        return BatchProcessingResponse(
            total_processed=len(request.coordinates),
            successful=successful,
            failed=failed,
            results=results
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch processing failed: {str(e)}"
        )


@router.post("/historical-trends", status_code=status.HTTP_200_OK)
async def export_historical_trends(
    request: HistoricalTrendsRequest,
    db: AsyncSession = Depends(get_db)
):
    """Export historical trend data for a location and hazard type.
    
    Args:
        request: Historical trends parameters
        db: Database session
        
    Returns:
        CSV file with historical event data
        
    Example:
        POST /api/export/historical-trends
        {
            "location_id": 1,
            "hazard_type": "earthquake",
            "start_date": "2020-01-01T00:00:00",
            "end_date": "2024-12-31T23:59:59"
        }
    """
    export_service = ExportService(db)
    
    try:
        csv_data = await export_service.export_historical_trends(
            location_id=request.location_id,
            hazard_type=request.hazard_type,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        filename = f"historical_trends_loc{request.location_id}_{request.hazard_type.value}_{datetime.utcnow().strftime('%Y%m%d')}.csv"
        
        return StreamingResponse(
            iter([csv_data]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export historical trends: {str(e)}"
        )


@router.get("/formats", status_code=status.HTTP_200_OK)
async def get_supported_formats() -> Dict[str, Any]:
    """Get information about supported export formats and their schemas.
    
    Returns:
        Dictionary with format specifications
    """
    return {
        "formats": {
            "csv": {
                "mime_type": "text/csv",
                "description": "Comma-separated values format",
                "supports_streaming": True,
                "max_recommended_records": 10000
            }
        },
        "risk_report_schema": {
            "columns": ExportService.RISK_REPORT_COLUMNS,
            "description": "Risk assessment report with location and hazard details"
        },
        "batch_size": ExportService.BATCH_SIZE,
        "streaming_recommendation": "Use streaming for datasets with >1000 records"
    }

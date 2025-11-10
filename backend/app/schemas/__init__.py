"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class HazardType(str, Enum):
    """Types of natural hazards."""
    EARTHQUAKE = "earthquake"
    FLOOD = "flood"
    FIRE = "fire"
    STORM = "storm"


class RiskLevel(str, Enum):
    """Risk assessment levels."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


# Location Schemas
class LocationBase(BaseModel):
    """Base location schema."""
    name: str = Field(..., min_length=1, max_length=255)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    population_density: float = Field(default=0.0, ge=0)
    building_code_rating: float = Field(default=5.0, ge=0, le=10)
    infrastructure_quality: float = Field(default=5.0, ge=0, le=10)
    extra_data: Optional[Dict[str, Any]] = None


class LocationCreate(LocationBase):
    """Schema for creating a location."""
    pass


class LocationUpdate(BaseModel):
    """Schema for updating a location."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    population_density: Optional[float] = Field(None, ge=0)
    building_code_rating: Optional[float] = Field(None, ge=0, le=10)
    infrastructure_quality: Optional[float] = Field(None, ge=0, le=10)
    extra_data: Optional[Dict[str, Any]] = None


class LocationResponse(LocationBase):
    """Schema for location response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


# Hazard Schemas
class HazardBase(BaseModel):
    """Base hazard schema."""
    hazard_type: HazardType
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    base_severity: float = Field(default=5.0, ge=0, le=10)
    weight_factors: Optional[Dict[str, float]] = None


class HazardCreate(HazardBase):
    """Schema for creating a hazard."""
    pass


class HazardResponse(HazardBase):
    """Schema for hazard response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


# Risk Assessment Schemas
class RiskFactors(BaseModel):
    """Risk factors input for assessment."""
    population_density: Optional[float] = Field(None, ge=0)
    building_code_rating: Optional[float] = Field(None, ge=0, le=10)
    infrastructure_quality: Optional[float] = Field(None, ge=0, le=10)


class RiskAssessmentRequest(BaseModel):
    """Schema for risk assessment request."""
    location_id: Optional[int] = None
    location: Optional[LocationCreate] = None
    hazard_types: List[HazardType] = Field(..., min_length=1)
    risk_factors: Optional[RiskFactors] = None


class FactorsAnalysis(BaseModel):
    """Detailed factors contributing to risk score."""
    population_density_impact: float
    building_code_impact: float
    infrastructure_impact: float
    hazard_severity_impact: float
    historical_frequency_impact: float


class RiskAssessmentResponse(BaseModel):
    """Schema for risk assessment response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    location_id: int
    hazard_id: int
    hazard_type: HazardType
    risk_score: float = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    confidence_level: float = Field(..., ge=0, le=1)
    factors_analysis: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    assessed_at: datetime


class RiskAssessmentBatchResponse(BaseModel):
    """Schema for batch risk assessment response."""
    location: LocationResponse
    assessments: List[RiskAssessmentResponse]
    overall_risk_score: float = Field(..., ge=0, le=100)
    overall_risk_level: RiskLevel


# Historical Data Schemas
class HistoricalDataBase(BaseModel):
    """Base historical data schema."""
    location_id: int
    hazard_id: int
    event_date: datetime
    severity: float = Field(..., ge=0, le=10)
    impact_description: Optional[str] = Field(None, max_length=1000)
    casualties: Optional[int] = Field(default=0, ge=0)
    economic_damage: Optional[float] = Field(default=0.0, ge=0)
    extra_data: Optional[Dict[str, Any]] = None


class HistoricalDataCreate(HistoricalDataBase):
    """Schema for creating historical data."""
    pass


class HistoricalDataResponse(HistoricalDataBase):
    """Schema for historical data response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime


# Generic Response Schemas
class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str
    error_code: Optional[str] = None

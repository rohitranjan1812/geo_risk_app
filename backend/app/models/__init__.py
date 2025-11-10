"""SQLAlchemy database models."""
from datetime import datetime
from typing import List
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class HazardType(str, enum.Enum):
    """Types of natural hazards."""
    EARTHQUAKE = "earthquake"
    FLOOD = "flood"
    FIRE = "fire"
    STORM = "storm"


class RiskLevel(str, enum.Enum):
    """Risk assessment levels."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class Location(Base):
    """Geographic location model."""
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    population_density = Column(Float, nullable=False, default=0.0)
    building_code_rating = Column(Float, nullable=False, default=5.0)  # 0-10 scale
    infrastructure_quality = Column(Float, nullable=False, default=5.0)  # 0-10 scale
    extra_data = Column(JSON, nullable=True)  # Renamed from metadata to avoid SQLAlchemy conflict
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    risk_assessments = relationship("RiskAssessment", back_populates="location", cascade="all, delete-orphan")
    historical_data = relationship("HistoricalData", back_populates="location", cascade="all, delete-orphan")


class Hazard(Base):
    """Hazard type configuration model."""
    __tablename__ = "hazards"
    
    id = Column(Integer, primary_key=True, index=True)
    hazard_type = Column(SQLEnum(HazardType), nullable=False, unique=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    base_severity = Column(Float, nullable=False, default=5.0)  # 0-10 scale
    weight_factors = Column(JSON, nullable=True)  # Weights for different risk factors
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    risk_assessments = relationship("RiskAssessment", back_populates="hazard")
    historical_data = relationship("HistoricalData", back_populates="hazard")


class RiskAssessment(Base):
    """Risk assessment result model."""
    __tablename__ = "risk_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False, index=True)
    hazard_id = Column(Integer, ForeignKey("hazards.id"), nullable=False, index=True)
    risk_score = Column(Float, nullable=False)  # 0-100 scale
    risk_level = Column(SQLEnum(RiskLevel), nullable=False)
    confidence_level = Column(Float, nullable=False, default=0.0)  # 0-1 scale
    factors_analysis = Column(JSON, nullable=True)  # Detailed breakdown of contributing factors
    recommendations = Column(JSON, nullable=True)  # List of mitigation recommendations
    assessed_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    location = relationship("Location", back_populates="risk_assessments")
    hazard = relationship("Hazard", back_populates="risk_assessments")


class HistoricalData(Base):
    """Historical hazard event data model."""
    __tablename__ = "historical_data"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False, index=True)
    hazard_id = Column(Integer, ForeignKey("hazards.id"), nullable=False, index=True)
    event_date = Column(DateTime, nullable=False, index=True)
    severity = Column(Float, nullable=False)  # 0-10 scale
    impact_description = Column(String(1000), nullable=True)
    casualties = Column(Integer, nullable=True, default=0)
    economic_damage = Column(Float, nullable=True, default=0.0)  # In USD
    extra_data = Column(JSON, nullable=True)  # Renamed from metadata to avoid SQLAlchemy conflict
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    location = relationship("Location", back_populates="historical_data")
    hazard = relationship("Hazard", back_populates="historical_data")

"""
Hazard Models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from datetime import datetime
from enum import Enum

from app.database import Base


class HazardType(str, Enum):
    """Types of natural hazards"""
    EARTHQUAKE = "earthquake"
    FLOOD = "flood"
    FIRE = "fire"
    STORM = "storm"
    TORNADO = "tornado"
    HURRICANE = "hurricane"
    TSUNAMI = "tsunami"


class Hazard(Base):
    """Hazard event model"""
    
    __tablename__ = "hazards"
    
    id = Column(Integer, primary_key=True, index=True)
    hazard_type = Column(SQLEnum(HazardType), nullable=False)
    name = Column(String(255))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    magnitude = Column(Float)  # Severity measure (e.g., Richter scale, category)
    radius_km = Column(Float)  # Affected radius in kilometers
    occurred_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Additional metadata
    description = Column(String(1000))
    source = Column(String(100))  # Data source (USGS, NOAA, etc.)

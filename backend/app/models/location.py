"""
Location Model
"""

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Location(Base):
    """Geographic location model"""
    
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(500))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    population_density = Column(Float)
    building_code_level = Column(Integer)  # 1-5 scale
    infrastructure_quality = Column(Integer)  # 1-5 scale
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    risk_assessments = relationship("RiskAssessment", back_populates="location")

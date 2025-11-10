"""
Risk Assessment Model
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class RiskAssessment(Base):
    """Risk assessment results model"""
    
    __tablename__ = "risk_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    
    # Overall risk score (0-100)
    overall_risk_score = Column(Float, nullable=False)
    
    # Individual hazard risk scores
    earthquake_risk = Column(Float, default=0.0)
    flood_risk = Column(Float, default=0.0)
    fire_risk = Column(Float, default=0.0)
    storm_risk = Column(Float, default=0.0)
    
    # Assessment metadata
    assessment_date = Column(DateTime, default=datetime.utcnow)
    algorithm_version = Column(String(50))
    confidence_level = Column(Float)  # 0-1 scale
    
    # Factors considered (JSON)
    risk_factors = Column(JSON)
    
    # Recommendations
    recommendations = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    location = relationship("Location", back_populates="risk_assessments")

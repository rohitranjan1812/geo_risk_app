"""
Database Models
"""

from app.models.location import Location
from app.models.hazard import Hazard, HazardType
from app.models.risk_assessment import RiskAssessment

__all__ = ["Location", "Hazard", "HazardType", "RiskAssessment"]

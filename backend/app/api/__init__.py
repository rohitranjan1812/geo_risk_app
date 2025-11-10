"""API router configuration."""
from fastapi import APIRouter
from app.api import risk, locations, hazards, historical, analytics, export

api_router = APIRouter()

api_router.include_router(risk.router)
api_router.include_router(locations.router)
api_router.include_router(hazards.router)
api_router.include_router(historical.router)
api_router.include_router(analytics.router)
api_router.include_router(export.router)

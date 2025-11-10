"""
Health Check Routes
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime

from app.database import get_db

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "georisk-api"
    }


@router.get("/health/db")
async def database_health(db: AsyncSession = Depends(get_db)) -> dict:
    """Database connectivity health check"""
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar_one()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

"""
Risk Assessment Routes
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/risk/placeholder")
async def risk_placeholder() -> dict:
    """Placeholder endpoint for risk assessment"""
    return {
        "message": "Risk assessment endpoints will be implemented here",
        "endpoints": [
            "/risk/calculate",
            "/risk/location/{location_id}",
            "/risk/history"
        ]
    }

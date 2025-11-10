"""Main FastAPI application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db import init_db
from app.api import api_router
from app.ws import stream_location_risk_updates, stream_regional_risk_visualization, stream_hazard_risk_heatmap


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.api_prefix)


# WebSocket endpoints for real-time visualization
@app.websocket(f"{settings.api_prefix}/ws/location/{{location_id}}")
async def websocket_location_updates(location_id: int, websocket):
    """WebSocket endpoint for location-specific risk updates."""
    from app.db import async_session
    async with async_session() as db:
        await stream_location_risk_updates(location_id, websocket, db)


@app.websocket(f"{settings.api_prefix}/ws/region")
async def websocket_region_visualization(
    min_latitude: float,
    max_latitude: float,
    min_longitude: float,
    max_longitude: float,
    websocket
):
    """WebSocket endpoint for regional risk visualization."""
    from app.db import async_session
    async with async_session() as db:
        await stream_regional_risk_visualization(
            min_latitude, max_latitude, min_longitude, max_longitude, websocket, db
        )


@app.websocket(f"{settings.api_prefix}/ws/hazard/{{hazard_id}}")
async def websocket_hazard_heatmap(hazard_id: int, websocket):
    """WebSocket endpoint for hazard risk heatmap updates."""
    from app.db import async_session
    async with async_session() as db:
        await stream_hazard_risk_heatmap(hazard_id, websocket, db)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

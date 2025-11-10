"""
FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator

from app.config import settings
from app.database import engine, Base
from app.routes import health, risk_assessment

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan events"""
    logger.info("Starting GeoRisk API...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created/verified")
    yield
    
    logger.info("Shutting down GeoRisk API...")
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Geographic Risk Assessment API for analyzing natural hazard risks",
    lifespan=lifespan,
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# Include routers
app.include_router(health.router, prefix=settings.API_V1_PREFIX, tags=["health"])
app.include_router(risk_assessment.router, prefix=settings.API_V1_PREFIX, tags=["risk"])


@app.get("/")
async def root() -> dict:
    """Root endpoint"""
    return {
        "message": "GeoRisk API",
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs"
    }

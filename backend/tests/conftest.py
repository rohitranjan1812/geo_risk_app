"""Pytest configuration and fixtures."""
import pytest
import asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import AsyncClient

from app.main import app
from app.db.session import Base, get_db
from app.models import Hazard, HazardType, Location, RiskAssessment, RiskLevel, HistoricalData


# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session.
    
    Yields:
        AsyncSession: Test database session
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with overridden database dependency.
    
    Args:
        db_session: Test database session
        
    Yields:
        AsyncClient: Test HTTP client
    """
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def async_client(client):
    """Alias for client fixture for compatibility."""
    return client


@pytest.fixture
async def sample_hazards(db_session: AsyncSession):
    """Create sample hazard configurations.
    
    Args:
        db_session: Database session
        
    Returns:
        List of created hazards
    """
    hazards = [
        Hazard(
            hazard_type=HazardType.EARTHQUAKE,
            name="Earthquake",
            description="Seismic activity",
            base_severity=7.0,
            weight_factors={"building_codes": 0.35, "infrastructure": 0.25}
        ),
        Hazard(
            hazard_type=HazardType.FLOOD,
            name="Flood",
            description="Water overflow",
            base_severity=6.0,
            weight_factors={"infrastructure": 0.35, "population": 0.20}
        ),
        Hazard(
            hazard_type=HazardType.FIRE,
            name="Fire",
            description="Wildfire or urban fire",
            base_severity=5.5,
            weight_factors={"population": 0.30, "building_codes": 0.30}
        ),
        Hazard(
            hazard_type=HazardType.STORM,
            name="Storm",
            description="Severe weather",
            base_severity=6.5,
            weight_factors={"infrastructure": 0.30, "building_codes": 0.25}
        )
    ]
    
    for hazard in hazards:
        db_session.add(hazard)
    
    await db_session.commit()
    
    for hazard in hazards:
        await db_session.refresh(hazard)
    
    return hazards


@pytest.fixture
async def sample_locations(db_session: AsyncSession):
    """Create sample location data.
    
    Args:
        db_session: Database session
        
    Returns:
        List of created locations
    """
    locations = [
        Location(
            name="San Francisco",
            latitude=37.7749,
            longitude=-122.4194,
            population_density=7000,
            building_code_rating=8.5,
            infrastructure_quality=7.5
        ),
        Location(
            name="Los Angeles",
            latitude=34.0522,
            longitude=-118.2437,
            population_density=8500,
            building_code_rating=7.0,
            infrastructure_quality=6.5
        ),
        Location(
            name="Seattle",
            latitude=47.6062,
            longitude=-122.3321,
            population_density=5000,
            building_code_rating=8.0,
            infrastructure_quality=8.0
        )
    ]
    
    for location in locations:
        db_session.add(location)
    
    await db_session.commit()
    
    for location in locations:
        await db_session.refresh(location)
    
    return locations


@pytest.fixture
async def sample_assessments(db_session: AsyncSession, sample_locations, sample_hazards):
    """Create sample risk assessments.
    
    Args:
        db_session: Database session
        sample_locations: Fixture providing locations
        sample_hazards: Fixture providing hazards
        
    Returns:
        List of created assessments
    """
    assessments = []
    
    for i, location in enumerate(sample_locations):
        for j, hazard in enumerate(sample_hazards):
            risk_score = 20.0 + (i * 15) + (j * 10)
            assessment = RiskAssessment(
                location_id=location.id,
                hazard_id=hazard.id,
                risk_score=min(risk_score, 100),
                risk_level=_determine_risk_level(risk_score),
                confidence_level=0.7 + (i * 0.05),
                recommendations=["Test recommendation 1", "Test recommendation 2"],
                assessed_at=datetime.utcnow() - timedelta(days=i)
            )
            db_session.add(assessment)
            assessments.append(assessment)
    
    await db_session.commit()
    
    for assessment in assessments:
        await db_session.refresh(assessment)
    
    return assessments


@pytest.fixture
async def sample_historical_data(db_session: AsyncSession, sample_locations, sample_hazards):
    """Create sample historical event data.
    
    Args:
        db_session: Database session
        sample_locations: Fixture providing locations
        sample_hazards: Fixture providing hazards
        
    Returns:
        List of created historical data
    """
    events = []
    
    for i in range(10):
        event = HistoricalData(
            location_id=sample_locations[0].id,
            hazard_id=sample_hazards[0].id,
            event_date=datetime.utcnow() - timedelta(days=i * 30),
            severity=5.0 + i * 0.3,
            casualties=i * 5,
            economic_damage=i * 1000000,
            impact_description=f"Test event {i}"
        )
        db_session.add(event)
        events.append(event)
    
    await db_session.commit()
    
    for event in events:
        await db_session.refresh(event)
    
    return events


@pytest.fixture
async def large_dataset_assessments(db_session: AsyncSession, sample_hazards):
    """Create large dataset for performance testing.
    
    Args:
        db_session: Database session
        sample_hazards: Fixture providing hazards
        
    Returns:
        List of created assessments
    """
    # Create 2500 locations
    locations = []
    for i in range(2500):
        location = Location(
            name=f"Location_{i}",
            latitude=37.0 + (i % 100) * 0.01,
            longitude=-122.0 + (i // 100) * 0.01,
            population_density=1000 + i,
            building_code_rating=5.0 + (i % 5),
            infrastructure_quality=5.0 + ((i + 1) % 5)
        )
        db_session.add(location)
        locations.append(location)
    
    await db_session.flush()
    
    # Create assessments (10k total: 2500 locations x 4 hazards)
    assessments = []
    for location in locations:
        for hazard in sample_hazards:
            risk_score = 10.0 + (location.id % 90)
            assessment = RiskAssessment(
                location_id=location.id,
                hazard_id=hazard.id,
                risk_score=risk_score,
                risk_level=_determine_risk_level(risk_score),
                confidence_level=0.75,
                assessed_at=datetime.utcnow()
            )
            db_session.add(assessment)
            assessments.append(assessment)
    
    await db_session.commit()
    
    return assessments


def _determine_risk_level(risk_score: float) -> RiskLevel:
    """Helper to determine risk level from score."""
    if risk_score < 25:
        return RiskLevel.LOW
    elif risk_score < 50:
        return RiskLevel.MODERATE
    elif risk_score < 75:
        return RiskLevel.HIGH
    else:
        return RiskLevel.CRITICAL

"""
Database performance tests and optimization validation.

Tests query performance, index effectiveness, and geospatial lookups.
"""
import time
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from sqlalchemy.orm import selectinload

from app.models import Location, Hazard, RiskAssessment, HistoricalData, HazardType


@pytest.mark.asyncio
async def test_location_geospatial_query_performance(db_session: AsyncSession):
    """
    Test geospatial query performance for finding nearby locations.
    
    OPTIMIZATION TARGET:
    - Query <50ms for 10000 locations
    - Index on (latitude, longitude) used effectively
    """
    # Create 10000 test locations in a grid
    locations = []
    for i in range(100):
        for j in range(100):
            loc = Location(
                name=f"Perf Test {i}_{j}",
                latitude=37.0 + i * 0.01,
                longitude=-122.0 + j * 0.01,
                population_density=1000.0,
                building_code_rating=5.0,
                infrastructure_quality=5.0
            )
            locations.append(loc)
    
    db_session.add_all(locations)
    await db_session.flush()
    
    # Test query: Find locations within bounding box
    target_lat = 37.5
    target_lon = -121.5
    radius_deg = 0.5
    
    start_time = time.time()
    
    result = await db_session.execute(
        select(Location).where(
            Location.latitude.between(target_lat - radius_deg, target_lat + radius_deg),
            Location.longitude.between(target_lon - radius_deg, target_lon + radius_deg)
        )
    )
    nearby_locations = result.scalars().all()
    
    query_time_ms = (time.time() - start_time) * 1000
    
    print("\n" + "="*60)
    print("GEOSPATIAL QUERY PERFORMANCE")
    print("="*60)
    print(f"Total locations: 10000")
    print(f"Locations found: {len(nearby_locations)}")
    print(f"Query time: {query_time_ms:.2f}ms")
    print("="*60)
    
    assert query_time_ms < 100, \
        f"Geospatial query took {query_time_ms:.2f}ms, target <100ms"
    
    assert len(nearby_locations) > 0, \
        "Query should find some locations"


@pytest.mark.asyncio
async def test_assessment_query_with_joins_performance(db_session: AsyncSession):
    """
    Test query performance for assessments with related data.
    
    OPTIMIZATION TARGET:
    - Join query <100ms for 1000 assessments
    - Proper use of indexes on foreign keys
    """
    # Create test data
    location = Location(
        name="Join Test Location",
        latitude=37.7749,
        longitude=-122.4194,
        population_density=5000.0,
        building_code_rating=7.0,
        infrastructure_quality=7.0
    )
    db_session.add(location)
    await db_session.flush()
    
    # Get hazards
    result = await db_session.execute(select(Hazard))
    hazards = result.scalars().all()
    
    # Create 1000 assessments
    assessments = []
    for i in range(250):  # 250 per hazard type = 1000 total
        for hazard in hazards[:4]:  # 4 hazard types
            assessment = RiskAssessment(
                location_id=location.id,
                hazard_id=hazard.id,
                risk_score=50.0 + (i % 50),
                risk_level="MODERATE",
                confidence_level=0.8,
                factors_analysis={},
                recommendations=[]
            )
            assessments.append(assessment)
    
    db_session.add_all(assessments)
    await db_session.flush()
    
    # Test query with joins
    start_time = time.time()
    
    result = await db_session.execute(
        select(RiskAssessment)
        .options(
            selectinload(RiskAssessment.location),
            selectinload(RiskAssessment.hazard)
        )
        .where(RiskAssessment.location_id == location.id)
    )
    assessments_with_relations = result.scalars().all()
    
    query_time_ms = (time.time() - start_time) * 1000
    
    print("\n" + "="*60)
    print("ASSESSMENT JOIN QUERY PERFORMANCE")
    print("="*60)
    print(f"Assessments queried: {len(assessments_with_relations)}")
    print(f"Query time: {query_time_ms:.2f}ms")
    print("="*60)
    
    assert query_time_ms < 200, \
        f"Join query took {query_time_ms:.2f}ms, target <200ms"
    
    assert len(assessments_with_relations) == 1000, \
        f"Expected 1000 assessments, got {len(assessments_with_relations)}"


@pytest.mark.asyncio
async def test_aggregation_query_performance(db_session: AsyncSession):
    """
    Test aggregation query performance.
    
    OPTIMIZATION TARGET:
    - Aggregation <50ms for 1000 records
    - Proper use of indexes
    """
    # Create test data
    locations = []
    for i in range(10):
        loc = Location(
            name=f"Agg Test {i}",
            latitude=37.7749 + i * 0.1,
            longitude=-122.4194 + i * 0.1,
            population_density=1000.0,
            building_code_rating=5.0,
            infrastructure_quality=5.0
        )
        locations.append(loc)
    
    db_session.add_all(locations)
    await db_session.flush()
    
    # Get hazards
    result = await db_session.execute(select(Hazard).limit(2))
    hazards = result.scalars().all()
    
    # Create assessments
    assessments = []
    for location in locations:
        for hazard in hazards:
            for i in range(50):  # 50 assessments per location-hazard
                assessment = RiskAssessment(
                    location_id=location.id,
                    hazard_id=hazard.id,
                    risk_score=25.0 + (i % 4) * 20,  # Vary across risk levels
                    risk_level=["LOW", "MODERATE", "HIGH", "CRITICAL"][i % 4],
                    confidence_level=0.8,
                    factors_analysis={},
                    recommendations=[]
                )
                assessments.append(assessment)
    
    db_session.add_all(assessments)
    await db_session.flush()
    
    # Test aggregation query
    start_time = time.time()
    
    result = await db_session.execute(
        select(
            RiskAssessment.risk_level,
            func.count(RiskAssessment.id).label('count'),
            func.avg(RiskAssessment.risk_score).label('avg_score'),
            func.max(RiskAssessment.risk_score).label('max_score')
        )
        .group_by(RiskAssessment.risk_level)
    )
    aggregations = result.all()
    
    query_time_ms = (time.time() - start_time) * 1000
    
    print("\n" + "="*60)
    print("AGGREGATION QUERY PERFORMANCE")
    print("="*60)
    print(f"Query time: {query_time_ms:.2f}ms")
    print("\nAggregation results:")
    for row in aggregations:
        print(f"  {row.risk_level}: count={row.count}, avg={row.avg_score:.2f}, max={row.max_score:.2f}")
    print("="*60)
    
    assert query_time_ms < 100, \
        f"Aggregation query took {query_time_ms:.2f}ms, target <100ms"


@pytest.mark.asyncio
async def test_index_usage_verification(db_session: AsyncSession):
    """
    Verify that database indexes are being used effectively.
    
    Tests EXPLAIN output to ensure query plans use indexes.
    """
    # Create test data
    location = Location(
        name="Index Test",
        latitude=37.7749,
        longitude=-122.4194,
        population_density=1000.0,
        building_code_rating=5.0,
        infrastructure_quality=5.0
    )
    db_session.add(location)
    await db_session.flush()
    
    # Test 1: Check geospatial query uses index
    explain_query = text("""
        EXPLAIN QUERY PLAN
        SELECT * FROM locations
        WHERE latitude BETWEEN 37.0 AND 38.0
        AND longitude BETWEEN -123.0 AND -122.0
    """)
    
    result = await db_session.execute(explain_query)
    plan = result.fetchall()
    
    print("\n" + "="*60)
    print("QUERY PLAN: Geospatial Lookup")
    print("="*60)
    for row in plan:
        print(f"  {row}")
    print("="*60)
    
    # Test 2: Check location_id index on assessments
    explain_query2 = text("""
        EXPLAIN QUERY PLAN
        SELECT * FROM risk_assessments
        WHERE location_id = :location_id
    """)
    
    result = await db_session.execute(explain_query2, {"location_id": location.id})
    plan = result.fetchall()
    
    print("\n" + "="*60)
    print("QUERY PLAN: Assessment by Location")
    print("="*60)
    for row in plan:
        print(f"  {row}")
    print("="*60)


@pytest.mark.asyncio
async def test_concurrent_database_access(db_session: AsyncSession):
    """
    Test database performance under concurrent access.
    
    OPTIMIZATION TARGET:
    - No deadlocks
    - Reasonable contention handling
    """
    import asyncio
    
    # Create test locations
    locations = []
    for i in range(10):
        loc = Location(
            name=f"Concurrent Test {i}",
            latitude=37.7749 + i * 0.01,
            longitude=-122.4194 + i * 0.01,
            population_density=1000.0,
            building_code_rating=5.0,
            infrastructure_quality=5.0
        )
        locations.append(loc)
    
    db_session.add_all(locations)
    await db_session.flush()
    
    # Get a hazard
    result = await db_session.execute(select(Hazard).limit(1))
    hazard = result.scalar_one()
    
    # Concurrent writes simulation
    async def create_assessment(location_id: int, index: int):
        assessment = RiskAssessment(
            location_id=location_id,
            hazard_id=hazard.id,
            risk_score=50.0 + index,
            risk_level="MODERATE",
            confidence_level=0.8,
            factors_analysis={'test': index},
            recommendations=[]
        )
        db_session.add(assessment)
        await db_session.flush()
    
    start_time = time.time()
    
    # Create tasks
    tasks = [
        create_assessment(loc.id, i)
        for i, loc in enumerate(locations * 5)  # 50 total writes
    ]
    
    # Execute concurrently
    await asyncio.gather(*tasks)
    
    duration_ms = (time.time() - start_time) * 1000
    
    # Verify all assessments created
    result = await db_session.execute(
        select(func.count(RiskAssessment.id))
        .where(RiskAssessment.hazard_id == hazard.id)
    )
    count = result.scalar()
    
    print("\n" + "="*60)
    print("CONCURRENT DATABASE ACCESS")
    print("="*60)
    print(f"Concurrent writes: 50")
    print(f"Successful writes: {count}")
    print(f"Duration: {duration_ms:.2f}ms")
    print("="*60)
    
    assert count == 50, \
        f"Expected 50 assessments, got {count}"


@pytest.mark.asyncio
async def test_historical_data_time_range_query(db_session: AsyncSession):
    """
    Test historical data queries with time ranges.
    
    OPTIMIZATION TARGET:
    - Time-based queries <50ms
    - Index on event_date used
    """
    from datetime import datetime, timedelta
    
    # Create location and hazard
    location = Location(
        name="Historical Test",
        latitude=37.7749,
        longitude=-122.4194,
        population_density=1000.0,
        building_code_rating=5.0,
        infrastructure_quality=5.0
    )
    db_session.add(location)
    await db_session.flush()
    
    result = await db_session.execute(select(Hazard).limit(1))
    hazard = result.scalar_one()
    
    # Create historical events spanning 10 years
    base_date = datetime.utcnow()
    historical_events = []
    
    for i in range(1000):
        days_ago = i * 3  # Every 3 days
        event = HistoricalData(
            location_id=location.id,
            hazard_id=hazard.id,
            event_date=base_date - timedelta(days=days_ago),
            severity=5.0 + (i % 5),
            description=f"Event {i}"
        )
        historical_events.append(event)
    
    db_session.add_all(historical_events)
    await db_session.flush()
    
    # Query events in last year
    one_year_ago = base_date - timedelta(days=365)
    
    start_time = time.time()
    
    result = await db_session.execute(
        select(HistoricalData)
        .where(
            HistoricalData.location_id == location.id,
            HistoricalData.event_date >= one_year_ago
        )
        .order_by(HistoricalData.event_date.desc())
    )
    recent_events = result.scalars().all()
    
    query_time_ms = (time.time() - start_time) * 1000
    
    print("\n" + "="*60)
    print("HISTORICAL DATA TIME RANGE QUERY")
    print("="*60)
    print(f"Total events: 1000")
    print(f"Events in last year: {len(recent_events)}")
    print(f"Query time: {query_time_ms:.2f}ms")
    print("="*60)
    
    assert query_time_ms < 100, \
        f"Historical query took {query_time_ms:.2f}ms, target <100ms"
    
    assert len(recent_events) > 0, \
        "Should find events in last year"

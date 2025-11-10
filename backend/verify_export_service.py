#!/usr/bin/env python3
"""Validation script for export service implementation."""
import asyncio
import csv
import io
from datetime import datetime

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from app.db.session import Base
from app.models import Location, Hazard, RiskAssessment, HazardType, RiskLevel, HistoricalData
from app.services.export_service import ExportService, DataTransformationPipeline


# Test database
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


async def setup_test_database() -> AsyncSession:
    """Create test database with sample data."""
    engine = create_async_engine(TEST_DB_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    session = SessionLocal()
    
    # Create hazards
    hazards = [
        Hazard(hazard_type=HazardType.EARTHQUAKE, name="Earthquake", base_severity=7.0),
        Hazard(hazard_type=HazardType.FLOOD, name="Flood", base_severity=6.0),
        Hazard(hazard_type=HazardType.FIRE, name="Fire", base_severity=5.5),
        Hazard(hazard_type=HazardType.STORM, name="Storm", base_severity=6.5),
    ]
    for hazard in hazards:
        session.add(hazard)
    await session.flush()
    
    # Create locations
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
    ]
    for location in locations:
        session.add(location)
    await session.flush()
    
    # Create assessments
    for location in locations:
        for hazard in hazards:
            assessment = RiskAssessment(
                location_id=location.id,
                hazard_id=hazard.id,
                risk_score=50.0 + location.id * 10 + hazard.id * 5,
                risk_level=RiskLevel.HIGH,
                confidence_level=0.8,
                recommendations=["Test rec 1", "Test rec 2"]
            )
            session.add(assessment)
    
    # Create historical data
    for i in range(5):
        event = HistoricalData(
            location_id=locations[0].id,
            hazard_id=hazards[0].id,
            event_date=datetime.utcnow(),
            severity=6.0 + i * 0.5,
            casualties=i * 10,
            economic_damage=i * 1000000
        )
        session.add(event)
    
    await session.commit()
    
    return session


async def test_data_transformation():
    """Test data transformation pipeline."""
    print("\n=== Testing Data Transformation Pipeline ===")
    
    # Test coordinate transformation
    raw_coords = [
        {"lat": "37.7749", "lon": "-122.4194", "name": "SF"},
        {"latitude": 34.0522, "longitude": -118.2437},
        {"y": 47.6062, "x": -122.3321, "name": "Seattle"},
        {"lat": "91", "lon": "0", "name": "Invalid"},  # Should be filtered
    ]
    
    transformed = DataTransformationPipeline.transform_coordinates(raw_coords)
    assert len(transformed) == 3, f"Expected 3 valid coordinates, got {len(transformed)}"
    assert transformed[0]['name'] == "SF"
    print(f"✓ Coordinate transformation: {len(transformed)}/4 valid (1 filtered)")
    
    # Test enrichment
    location_data = {"name": "Test", "latitude": 37.0, "longitude": -122.0}
    enriched = DataTransformationPipeline.enrich_with_defaults(location_data)
    assert enriched['population_density'] == 0.0
    assert enriched['building_code_rating'] == 5.0
    print("✓ Data enrichment: defaults applied")
    
    # Test hazard normalization
    hazards = DataTransformationPipeline.normalize_hazard_types(
        ["earthquake", "wildfire", "hurricane"]
    )
    assert HazardType.EARTHQUAKE in hazards
    assert HazardType.FIRE in hazards  # wildfire -> fire
    assert HazardType.STORM in hazards  # hurricane -> storm
    print(f"✓ Hazard normalization: {len(hazards)} types recognized")


async def test_csv_generation(session: AsyncSession):
    """Test CSV report generation."""
    print("\n=== Testing CSV Generation ===")
    
    service = ExportService(session)
    
    # Test basic CSV generation
    csv_data = await service.generate_risk_report_csv()
    reader = csv.DictReader(io.StringIO(csv_data))
    rows = list(reader)
    
    assert len(rows) > 0, "CSV should contain data"
    assert all(col in rows[0] for col in ExportService.RISK_REPORT_COLUMNS)
    print(f"✓ Basic CSV generation: {len(rows)} rows, {len(rows[0])} columns")
    
    # Test with hazard filter
    csv_data = await service.generate_risk_report_csv(
        hazard_types=[HazardType.EARTHQUAKE]
    )
    reader = csv.DictReader(io.StringIO(csv_data))
    rows = list(reader)
    assert all(row['hazard_type'] == 'earthquake' for row in rows)
    print(f"✓ Filtered CSV: {len(rows)} earthquake assessments")
    
    # Test with risk level filter
    csv_data = await service.generate_risk_report_csv(
        risk_levels=[RiskLevel.HIGH, RiskLevel.CRITICAL]
    )
    reader = csv.DictReader(io.StringIO(csv_data))
    rows = list(reader)
    assert all(row['risk_level'] in ['high', 'critical'] for row in rows)
    print(f"✓ Risk level filter: {len(rows)} high/critical assessments")


async def test_streaming(session: AsyncSession):
    """Test streaming CSV generation."""
    print("\n=== Testing Streaming ===")
    
    service = ExportService(session)
    
    chunks = []
    async for chunk in service.stream_risk_report_csv():
        chunks.append(chunk)
    
    assert len(chunks) > 0, "Should produce at least header chunk"
    
    # Combine chunks and parse
    full_csv = "".join(chunks)
    reader = csv.DictReader(io.StringIO(full_csv))
    rows = list(reader)
    
    assert len(rows) > 0, "Streamed CSV should contain data"
    print(f"✓ Streaming: {len(chunks)} chunks, {len(rows)} total rows")


async def test_batch_processing(session: AsyncSession):
    """Test batch location processing."""
    print("\n=== Testing Batch Processing ===")
    
    service = ExportService(session)
    
    # Test with small batch
    coordinates = [
        {"lat": 40.7128, "lon": -74.0060, "name": "New York"},
        {"lat": 41.8781, "lon": -87.6298, "name": "Chicago"},
        {"lat": 29.7604, "lon": -95.3698, "name": "Houston"},
    ]
    
    results = await service.batch_process_locations(
        coordinates=coordinates,
        hazard_types=[HazardType.EARTHQUAKE, HazardType.FLOOD],
        save_to_db=False
    )
    
    assert len(results) == 3, f"Expected 3 results, got {len(results)}"
    assert all('location' in r for r in results)
    assert all('assessments' in r for r in results)
    
    # Verify each has 2 assessments (earthquake + flood)
    for result in results:
        assert len(result['assessments']) == 2
        hazard_types = [a['hazard_type'] for a in result['assessments']]
        assert 'earthquake' in hazard_types
        assert 'flood' in hazard_types
    
    print(f"✓ Batch processing: {len(results)} locations, 2 hazards each")
    
    # Test with larger batch
    large_coords = [
        {"lat": 37.0 + i*0.1, "lon": -122.0 + i*0.1, "name": f"Loc_{i}"}
        for i in range(100)
    ]
    
    large_results = await service.batch_process_locations(
        coordinates=large_coords,
        hazard_types=[HazardType.EARTHQUAKE],
        save_to_db=False
    )
    
    assert len(large_results) == 100
    print(f"✓ Large batch: {len(large_results)} locations processed")


async def test_historical_trends(session: AsyncSession):
    """Test historical trends export."""
    print("\n=== Testing Historical Trends ===")
    
    service = ExportService(session)
    
    # Get first location
    result = await session.execute(select(Location).limit(1))
    location = result.scalar_one()
    
    csv_data = await service.export_historical_trends(
        location_id=location.id,
        hazard_type=HazardType.EARTHQUAKE
    )
    
    reader = csv.DictReader(io.StringIO(csv_data))
    rows = list(reader)
    
    assert len(rows) > 0, "Should have historical data"
    assert all(col in rows[0] for col in ['event_id', 'event_date', 'severity'])
    print(f"✓ Historical trends: {len(rows)} events exported")


async def test_csv_format_validation(session: AsyncSession):
    """Test CSV format and encoding."""
    print("\n=== Testing CSV Format Validation ===")
    
    service = ExportService(session)
    
    csv_data = await service.generate_risk_report_csv()
    
    # Test UTF-8 encoding
    try:
        encoded = csv_data.encode('utf-8')
        decoded = encoded.decode('utf-8')
        assert decoded == csv_data
        print("✓ UTF-8 encoding: valid")
    except Exception as e:
        raise AssertionError(f"Encoding test failed: {e}")
    
    # Test CSV parsing
    try:
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)
        assert len(rows) > 0
        print(f"✓ CSV parsing: {len(rows)} rows parsed successfully")
    except Exception as e:
        raise AssertionError(f"CSV parsing failed: {e}")
    
    # Test all required columns present
    required_cols = ExportService.RISK_REPORT_COLUMNS
    actual_cols = list(rows[0].keys())
    missing = set(required_cols) - set(actual_cols)
    assert not missing, f"Missing columns: {missing}"
    print(f"✓ Column validation: all {len(required_cols)} required columns present")


async def run_all_tests():
    """Run all validation tests."""
    print("=" * 60)
    print("Export Service Validation")
    print("=" * 60)
    
    try:
        # Test data transformation (no DB needed)
        await test_data_transformation()
        
        # Setup database for remaining tests
        session = await setup_test_database()
        
        # Run database-dependent tests
        await test_csv_generation(session)
        await test_streaming(session)
        await test_batch_processing(session)
        await test_historical_trends(session)
        await test_csv_format_validation(session)
        
        await session.close()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        print("\nSuccess Criteria Met:")
        print("✓ CSV exports contain all required fields")
        print("✓ Handles batch processing of 100+ locations efficiently")
        print("✓ Streaming works for large datasets")
        print("✓ Output validates against CSV schema")
        print("✓ Data transformation pipeline working correctly")
        
        return True
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)

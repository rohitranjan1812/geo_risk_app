"""Unit tests for export service functionality."""
import pytest
import csv
import io
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.services.export_service import ExportService, DataTransformationPipeline
from app.models import (
    Location, RiskAssessment, Hazard, HistoricalData,
    HazardType, RiskLevel
)


class TestDataTransformationPipeline:
    """Tests for data transformation pipeline."""
    
    def test_transform_coordinates_basic(self):
        """Test basic coordinate transformation."""
        raw_coords = [
            {"lat": "37.7749", "lon": "-122.4194", "name": "San Francisco"}
        ]
        
        result = DataTransformationPipeline.transform_coordinates(raw_coords)
        
        assert len(result) == 1
        assert result[0]['latitude'] == 37.7749
        assert result[0]['longitude'] == -122.4194
        assert result[0]['name'] == "San Francisco"
        assert result[0]['population_density'] == 0
        assert result[0]['building_code_rating'] == 5.0
    
    def test_transform_coordinates_various_formats(self):
        """Test coordinate transformation with different key formats."""
        raw_coords = [
            {"latitude": 40.7128, "longitude": -74.0060, "name": "NYC"},
            {"y": 34.0522, "x": -118.2437, "name": "LA"},
            {"lat": 41.8781, "lon": -87.6298, "name": "Chicago"}
        ]
        
        result = DataTransformationPipeline.transform_coordinates(raw_coords)
        
        assert len(result) == 3
        assert result[0]['latitude'] == 40.7128
        assert result[1]['latitude'] == 34.0522
        assert result[2]['latitude'] == 41.8781
    
    def test_transform_coordinates_with_metadata(self):
        """Test coordinate transformation with additional metadata."""
        raw_coords = [
            {
                "lat": 37.7749,
                "lon": -122.4194,
                "name": "San Francisco",
                "population_density": 7000,
                "building_code_rating": 8.5,
                "infrastructure_quality": 7.5
            }
        ]
        
        result = DataTransformationPipeline.transform_coordinates(raw_coords)
        
        assert result[0]['population_density'] == 7000
        assert result[0]['building_code_rating'] == 8.5
        assert result[0]['infrastructure_quality'] == 7.5
    
    def test_transform_coordinates_invalid_ranges(self):
        """Test that invalid coordinates are filtered out."""
        raw_coords = [
            {"lat": "91", "lon": "0", "name": "Invalid1"},  # Lat > 90
            {"lat": "0", "lon": "181", "name": "Invalid2"},  # Lon > 180
            {"lat": "37.7749", "lon": "-122.4194", "name": "Valid"}
        ]
        
        result = DataTransformationPipeline.transform_coordinates(raw_coords)
        
        # Only valid coordinate should be returned
        assert len(result) == 1
        assert result[0]['name'] == "Valid"
    
    def test_transform_coordinates_missing_fields(self):
        """Test handling of missing required fields."""
        raw_coords = [
            {"lat": "37.7749", "name": "Missing lon"},  # Missing lon
            {"lon": "-122.4194", "name": "Missing lat"},  # Missing lat
            {"lat": "37.7749", "lon": "-122.4194"}  # Missing name
        ]
        
        result = DataTransformationPipeline.transform_coordinates(raw_coords)
        
        # Only last one should succeed (name gets default)
        assert len(result) == 1
        assert "Location_37.7749_-122.4194" in result[0]['name']
    
    def test_enrich_with_defaults(self):
        """Test enrichment with default values."""
        location_data = {
            "name": "Test Location",
            "latitude": 37.7749,
            "longitude": -122.4194
        }
        
        result = DataTransformationPipeline.enrich_with_defaults(location_data)
        
        assert result['name'] == "Test Location"
        assert result['latitude'] == 37.7749
        assert result['population_density'] == 0.0
        assert result['building_code_rating'] == 5.0
        assert result['infrastructure_quality'] == 5.0
    
    def test_enrich_with_custom_defaults(self):
        """Test enrichment with custom default values."""
        location_data = {"name": "Test"}
        custom_defaults = {
            "population_density": 5000,
            "building_code_rating": 7.0
        }
        
        result = DataTransformationPipeline.enrich_with_defaults(
            location_data, custom_defaults
        )
        
        assert result['population_density'] == 5000
        assert result['building_code_rating'] == 7.0
    
    def test_normalize_hazard_types(self):
        """Test hazard type normalization."""
        hazard_input = ["earthquake", "FLOOD", "Fire", "Storm"]
        
        result = DataTransformationPipeline.normalize_hazard_types(hazard_input)
        
        assert len(result) == 4
        assert HazardType.EARTHQUAKE in result
        assert HazardType.FLOOD in result
        assert HazardType.FIRE in result
        assert HazardType.STORM in result
    
    def test_normalize_hazard_types_aliases(self):
        """Test hazard type aliases are handled."""
        hazard_input = ["wildfire", "hurricane", "tornado"]
        
        result = DataTransformationPipeline.normalize_hazard_types(hazard_input)
        
        assert HazardType.FIRE in result  # wildfire -> fire
        assert HazardType.STORM in result  # hurricane -> storm
    
    def test_normalize_hazard_types_default(self):
        """Test default hazard types when input is empty or invalid."""
        result = DataTransformationPipeline.normalize_hazard_types([])
        
        # Should return all hazard types as default
        assert len(result) == 4
        assert all(ht in result for ht in HazardType)


class TestExportServiceCSVGeneration:
    """Tests for CSV generation functionality."""
    
    @pytest.mark.asyncio
    async def test_assessment_to_csv_row(self, db_session):
        """Test conversion of assessment to CSV row."""
        # Create test data
        location = Location(
            id=1,
            name="Test City",
            latitude=37.7749,
            longitude=-122.4194,
            population_density=7000,
            building_code_rating=8.5,
            infrastructure_quality=7.5
        )
        
        hazard = Hazard(
            id=1,
            hazard_type=HazardType.EARTHQUAKE,
            name="Earthquake Risk",
            base_severity=7.0
        )
        
        assessment = RiskAssessment(
            id=1,
            location_id=1,
            hazard_id=1,
            risk_score=75.5,
            risk_level=RiskLevel.CRITICAL,
            confidence_level=0.85,
            recommendations=["Retrofit buildings", "Emergency plan"],
            assessed_at=datetime(2024, 1, 15, 12, 0, 0)
        )
        assessment.location = location
        assessment.hazard = hazard
        
        service = ExportService(db_session)
        row = service._assessment_to_csv_row(assessment)
        
        assert row['assessment_id'] == 1
        assert row['location_id'] == 1
        assert row['location_name'] == "Test City"
        assert row['latitude'] == 37.7749
        assert row['longitude'] == -122.4194
        assert row['hazard_type'] == 'earthquake'
        assert row['risk_score'] == 75.5
        assert row['risk_level'] == 'critical'
        assert row['confidence_level'] == 0.85
        assert 'Retrofit buildings' in row['recommendations']
    
    @pytest.mark.asyncio
    async def test_generate_risk_report_csv_basic(self, db_session, sample_assessments):
        """Test basic CSV report generation."""
        service = ExportService(db_session)
        
        csv_data = await service.generate_risk_report_csv()
        
        # Parse CSV
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)
        
        assert len(rows) > 0
        assert all(col in rows[0] for col in ExportService.RISK_REPORT_COLUMNS)
    
    @pytest.mark.asyncio
    async def test_generate_risk_report_csv_with_date_filter(
        self, db_session, sample_assessments
    ):
        """Test CSV generation with date range filter."""
        service = ExportService(db_session)
        
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()
        
        csv_data = await service.generate_risk_report_csv(
            start_date=start_date,
            end_date=end_date
        )
        
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)
        
        # Verify all dates are within range
        for row in rows:
            assessed_at = datetime.fromisoformat(row['assessed_at'])
            assert start_date <= assessed_at <= end_date
    
    @pytest.mark.asyncio
    async def test_generate_risk_report_csv_with_hazard_filter(
        self, db_session, sample_assessments
    ):
        """Test CSV generation with hazard type filter."""
        service = ExportService(db_session)
        
        csv_data = await service.generate_risk_report_csv(
            hazard_types=[HazardType.EARTHQUAKE]
        )
        
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)
        
        # Verify all rows are earthquake assessments
        for row in rows:
            assert row['hazard_type'] == 'earthquake'
    
    @pytest.mark.asyncio
    async def test_generate_risk_report_csv_with_risk_level_filter(
        self, db_session, sample_assessments
    ):
        """Test CSV generation with risk level filter."""
        service = ExportService(db_session)
        
        csv_data = await service.generate_risk_report_csv(
            risk_levels=[RiskLevel.HIGH, RiskLevel.CRITICAL]
        )
        
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)
        
        # Verify all rows have high or critical risk
        for row in rows:
            assert row['risk_level'] in ['high', 'critical']
    
    @pytest.mark.asyncio
    async def test_generate_risk_report_csv_with_min_score(
        self, db_session, sample_assessments
    ):
        """Test CSV generation with minimum risk score filter."""
        service = ExportService(db_session)
        
        min_score = 50.0
        csv_data = await service.generate_risk_report_csv(
            min_risk_score=min_score
        )
        
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)
        
        # Verify all scores are above minimum
        for row in rows:
            assert float(row['risk_score']) >= min_score


class TestExportServiceStreaming:
    """Tests for streaming functionality."""
    
    @pytest.mark.asyncio
    async def test_stream_risk_report_csv_header(self, db_session, sample_assessments):
        """Test that streaming yields proper CSV header."""
        service = ExportService(db_session)
        
        chunks = []
        async for chunk in service.stream_risk_report_csv():
            chunks.append(chunk)
            break  # Just get first chunk (header)
        
        # First chunk should contain header
        assert len(chunks) > 0
        header_line = chunks[0].strip().split('\n')[0]
        assert all(col in header_line for col in ['assessment_id', 'location_name', 'hazard_type'])
    
    @pytest.mark.asyncio
    async def test_stream_risk_report_csv_complete(self, db_session, sample_assessments):
        """Test complete streaming of CSV report."""
        service = ExportService(db_session)
        
        # Collect all chunks
        full_csv = ""
        async for chunk in service.stream_risk_report_csv():
            full_csv += chunk
        
        # Parse complete CSV
        reader = csv.DictReader(io.StringIO(full_csv))
        rows = list(reader)
        
        assert len(rows) > 0
        assert all(col in rows[0] for col in ExportService.RISK_REPORT_COLUMNS)
    
    @pytest.mark.asyncio
    async def test_stream_risk_report_csv_batching(
        self, db_session, large_dataset_assessments
    ):
        """Test that streaming processes data in batches."""
        service = ExportService(db_session)
        
        chunk_count = 0
        async for chunk in service.stream_risk_report_csv():
            chunk_count += 1
        
        # Should have multiple chunks for large dataset
        # (1 header + ceil(records / BATCH_SIZE))
        assert chunk_count > 1


class TestBatchProcessing:
    """Tests for batch location processing."""
    
    @pytest.mark.asyncio
    async def test_batch_process_locations_basic(self, db_session, sample_hazards):
        """Test basic batch processing of locations."""
        service = ExportService(db_session)
        
        coordinates = [
            {"lat": 37.7749, "lon": -122.4194, "name": "San Francisco"},
            {"lat": 34.0522, "lon": -118.2437, "name": "Los Angeles"}
        ]
        
        results = await service.batch_process_locations(
            coordinates=coordinates,
            save_to_db=False
        )
        
        assert len(results) == 2
        assert results[0]['location']['name'] == "San Francisco"
        assert results[1]['location']['name'] == "Los Angeles"
        assert all('assessments' in r for r in results)
    
    @pytest.mark.asyncio
    async def test_batch_process_locations_with_hazard_filter(
        self, db_session, sample_hazards
    ):
        """Test batch processing with specific hazard types."""
        service = ExportService(db_session)
        
        coordinates = [
            {"lat": 37.7749, "lon": -122.4194, "name": "San Francisco"}
        ]
        
        results = await service.batch_process_locations(
            coordinates=coordinates,
            hazard_types=[HazardType.EARTHQUAKE],
            save_to_db=False
        )
        
        assert len(results) == 1
        # Should only have earthquake assessment
        assessments = results[0]['assessments']
        assert all(a['hazard_type'] == 'earthquake' for a in assessments)
    
    @pytest.mark.asyncio
    async def test_batch_process_locations_save_to_db(
        self, db_session, sample_hazards
    ):
        """Test batch processing with database saving."""
        service = ExportService(db_session)
        
        coordinates = [
            {"lat": 37.7749, "lon": -122.4194, "name": "Test City"}
        ]
        
        results = await service.batch_process_locations(
            coordinates=coordinates,
            save_to_db=True
        )
        
        assert len(results) == 1
        assert results[0]['location']['id'] is not None  # Should have DB ID
        assert all('id' in a for a in results[0]['assessments'])
    
    @pytest.mark.asyncio
    async def test_batch_process_large_dataset(
        self, db_session, sample_hazards
    ):
        """Test batch processing with 1000+ locations."""
        service = ExportService(db_session)
        
        # Generate 1500 test coordinates
        coordinates = [
            {
                "lat": 37.0 + (i % 10) * 0.1,
                "lon": -122.0 + (i // 10) * 0.1,
                "name": f"Location_{i}"
            }
            for i in range(1500)
        ]
        
        results = await service.batch_process_locations(
            coordinates=coordinates,
            hazard_types=[HazardType.EARTHQUAKE],
            save_to_db=False
        )
        
        # Should process all locations
        assert len(results) == 1500
    
    @pytest.mark.asyncio
    async def test_batch_process_invalid_coordinates(
        self, db_session, sample_hazards
    ):
        """Test batch processing filters invalid coordinates."""
        service = ExportService(db_session)
        
        coordinates = [
            {"lat": 91, "lon": 0, "name": "Invalid1"},  # Invalid
            {"lat": 37.7749, "lon": -122.4194, "name": "Valid"},  # Valid
            {"lat": 0, "lon": 181, "name": "Invalid2"}  # Invalid
        ]
        
        results = await service.batch_process_locations(
            coordinates=coordinates,
            save_to_db=False
        )
        
        # Only valid coordinate should be processed
        assert len(results) == 1
        assert results[0]['location']['name'] == "Valid"


class TestHistoricalTrends:
    """Tests for historical trend exports."""
    
    @pytest.mark.asyncio
    async def test_export_historical_trends_basic(
        self, db_session, sample_historical_data
    ):
        """Test basic historical trends export."""
        service = ExportService(db_session)
        
        csv_data = await service.export_historical_trends(
            location_id=1,
            hazard_type=HazardType.EARTHQUAKE
        )
        
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)
        
        assert len(rows) > 0
        assert all(col in rows[0] for col in ['event_id', 'event_date', 'severity'])
    
    @pytest.mark.asyncio
    async def test_export_historical_trends_with_date_range(
        self, db_session, sample_historical_data
    ):
        """Test historical trends export with date filtering."""
        service = ExportService(db_session)
        
        start_date = datetime.utcnow() - timedelta(days=365)
        end_date = datetime.utcnow()
        
        csv_data = await service.export_historical_trends(
            location_id=1,
            hazard_type=HazardType.EARTHQUAKE,
            start_date=start_date,
            end_date=end_date
        )
        
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)
        
        # Verify dates are in range
        for row in rows:
            event_date = datetime.fromisoformat(row['event_date'])
            assert start_date <= event_date <= end_date


class TestPerformance:
    """Performance tests for export service."""
    
    @pytest.mark.asyncio
    async def test_csv_generation_performance(
        self, db_session, large_dataset_assessments
    ):
        """Test CSV generation performance with 10k+ records."""
        import time
        
        service = ExportService(db_session)
        
        start_time = time.time()
        csv_data = await service.generate_risk_report_csv()
        duration = time.time() - start_time
        
        # Should complete within reasonable time (< 5 seconds for 10k records)
        assert duration < 5.0
        assert len(csv_data) > 0
    
    @pytest.mark.asyncio
    async def test_streaming_memory_efficiency(
        self, db_session, large_dataset_assessments
    ):
        """Test that streaming doesn't load entire dataset into memory."""
        import sys
        
        service = ExportService(db_session)
        
        max_chunk_size = 0
        async for chunk in service.stream_risk_report_csv():
            chunk_size = sys.getsizeof(chunk)
            max_chunk_size = max(max_chunk_size, chunk_size)
        
        # Individual chunks should be relatively small (< 1MB)
        assert max_chunk_size < 1024 * 1024
    
    @pytest.mark.asyncio
    async def test_batch_processing_performance(
        self, db_session, sample_hazards
    ):
        """Test batch processing performance with 1000 locations."""
        import time
        
        service = ExportService(db_session)
        
        coordinates = [
            {
                "lat": 37.0 + (i % 10) * 0.1,
                "lon": -122.0 + (i // 10) * 0.1,
                "name": f"Location_{i}"
            }
            for i in range(1000)
        ]
        
        start_time = time.time()
        results = await service.batch_process_locations(
            coordinates=coordinates,
            hazard_types=[HazardType.EARTHQUAKE],
            save_to_db=False
        )
        duration = time.time() - start_time
        
        # Should complete within reasonable time (< 30 seconds for 1000 locations)
        assert duration < 30.0
        assert len(results) == 1000


class TestCSVValidation:
    """Tests for CSV format and encoding validation."""
    
    @pytest.mark.asyncio
    async def test_csv_format_validation(self, db_session, sample_assessments):
        """Test that generated CSV has valid format."""
        service = ExportService(db_session)
        
        csv_data = await service.generate_risk_report_csv()
        
        # Should parse without errors
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)
        
        assert len(rows) > 0
        
        # Verify required columns exist
        for col in ExportService.RISK_REPORT_COLUMNS:
            assert col in rows[0]
    
    @pytest.mark.asyncio
    async def test_csv_encoding_utf8(self, db_session, sample_assessments):
        """Test that CSV uses UTF-8 encoding."""
        service = ExportService(db_session)
        
        csv_data = await service.generate_risk_report_csv()
        
        # Should encode to UTF-8 without errors
        encoded = csv_data.encode('utf-8')
        decoded = encoded.decode('utf-8')
        
        assert decoded == csv_data
    
    @pytest.mark.asyncio
    async def test_csv_special_characters(self, db_session):
        """Test CSV handles special characters in data."""
        # Create location with special characters
        location = Location(
            name="Test, City; with \"quotes\"",
            latitude=37.7749,
            longitude=-122.4194
        )
        db_session.add(location)
        await db_session.flush()
        
        hazard = Hazard(
            hazard_type=HazardType.EARTHQUAKE,
            name="Test",
            base_severity=5.0
        )
        db_session.add(hazard)
        await db_session.flush()
        
        assessment = RiskAssessment(
            location_id=location.id,
            hazard_id=hazard.id,
            risk_score=50.0,
            risk_level=RiskLevel.MODERATE,
            confidence_level=0.7
        )
        db_session.add(assessment)
        await db_session.commit()
        
        service = ExportService(db_session)
        csv_data = await service.generate_risk_report_csv()
        
        # Should parse correctly with special characters
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)
        
        assert any('Test, City' in row['location_name'] for row in rows)

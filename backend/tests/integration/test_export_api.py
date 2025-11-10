"""Integration tests for export API endpoints."""
import pytest
import csv
import io
from datetime import datetime, timedelta
from httpx import AsyncClient

from app.models import HazardType, RiskLevel


class TestExportRiskReportAPI:
    """Tests for /api/export/risk-report endpoint."""
    
    @pytest.mark.asyncio
    async def test_export_risk_report_basic(self, client: AsyncClient, sample_assessments):
        """Test basic risk report export."""
        response = await client.post(
            "/api/export/risk-report",
            json={"stream": False}
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]
        
        # Parse CSV
        csv_data = response.text
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)
        
        assert len(rows) > 0
        assert "assessment_id" in rows[0]
        assert "location_name" in rows[0]
        assert "risk_score" in rows[0]
    
    @pytest.mark.asyncio
    async def test_export_risk_report_with_filters(
        self, client: AsyncClient, sample_assessments
    ):
        """Test risk report export with filters."""
        response = await client.post(
            "/api/export/risk-report",
            json={
                "hazard_types": ["earthquake"],
                "min_risk_score": 30.0,
                "stream": False
            }
        )
        
        assert response.status_code == 200
        
        csv_data = response.text
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)
        
        # Verify filters applied
        for row in rows:
            assert row["hazard_type"] == "earthquake"
            assert float(row["risk_score"]) >= 30.0
    
    @pytest.mark.asyncio
    async def test_export_risk_report_with_date_range(
        self, client: AsyncClient, sample_assessments
    ):
        """Test risk report export with date range filter."""
        start_date = (datetime.utcnow() - timedelta(days=5)).isoformat()
        end_date = datetime.utcnow().isoformat()
        
        response = await client.post(
            "/api/export/risk-report",
            json={
                "start_date": start_date,
                "end_date": end_date,
                "stream": False
            }
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_export_risk_report_with_location_bounds(
        self, client: AsyncClient, sample_assessments
    ):
        """Test risk report export with geographic bounding box."""
        response = await client.post(
            "/api/export/risk-report",
            json={
                "location_bounds": {
                    "min_lat": 30.0,
                    "max_lat": 50.0,
                    "min_lon": -130.0,
                    "max_lon": -100.0
                },
                "stream": False
            }
        )
        
        assert response.status_code == 200
        
        csv_data = response.text
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)
        
        # Verify all locations within bounds
        for row in rows:
            lat = float(row["latitude"])
            lon = float(row["longitude"])
            assert 30.0 <= lat <= 50.0
            assert -130.0 <= lon <= -100.0
    
    @pytest.mark.asyncio
    async def test_export_risk_report_streaming(
        self, client: AsyncClient, sample_assessments
    ):
        """Test risk report export with streaming enabled."""
        response = await client.post(
            "/api/export/risk-report",
            json={"stream": True}
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        
        # Read streamed content
        content = b""
        async for chunk in response.aiter_bytes():
            content += chunk
        
        csv_data = content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)
        
        assert len(rows) > 0


class TestBatchProcessAPI:
    """Tests for /api/export/batch-process endpoint."""
    
    @pytest.mark.asyncio
    async def test_batch_process_basic(self, client: AsyncClient, sample_hazards):
        """Test basic batch processing."""
        response = await client.post(
            "/api/export/batch-process",
            json={
                "coordinates": [
                    {"lat": 37.7749, "lon": -122.4194, "name": "San Francisco"},
                    {"lat": 34.0522, "lon": -118.2437, "name": "Los Angeles"}
                ],
                "save_to_db": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_processed"] == 2
        assert data["successful"] == 2
        assert data["failed"] == 0
        assert len(data["results"]) == 2
        
        # Verify results structure
        for result in data["results"]:
            assert "location" in result
            assert "assessments" in result
            assert "overall_risk_score" in result
    
    @pytest.mark.asyncio
    async def test_batch_process_with_hazard_filter(
        self, client: AsyncClient, sample_hazards
    ):
        """Test batch processing with specific hazard types."""
        response = await client.post(
            "/api/export/batch-process",
            json={
                "coordinates": [
                    {"lat": 37.7749, "lon": -122.4194, "name": "Test City"}
                ],
                "hazard_types": ["earthquake", "flood"],
                "save_to_db": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        result = data["results"][0]
        assessments = result["assessments"]
        
        # Should only have earthquake and flood assessments
        assert len(assessments) == 2
        hazard_types = [a["hazard_type"] for a in assessments]
        assert "earthquake" in hazard_types
        assert "flood" in hazard_types
    
    @pytest.mark.asyncio
    async def test_batch_process_save_to_db(
        self, client: AsyncClient, sample_hazards
    ):
        """Test batch processing with database saving."""
        response = await client.post(
            "/api/export/batch-process",
            json={
                "coordinates": [
                    {"lat": 40.7128, "lon": -74.0060, "name": "New York"}
                ],
                "save_to_db": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        result = data["results"][0]
        
        # Should have database IDs
        assert result["location"]["id"] is not None
        for assessment in result["assessments"]:
            assert "id" in assessment
    
    @pytest.mark.asyncio
    async def test_batch_process_invalid_coordinates(
        self, client: AsyncClient, sample_hazards
    ):
        """Test batch processing filters invalid coordinates."""
        response = await client.post(
            "/api/export/batch-process",
            json={
                "coordinates": [
                    {"lat": 91, "lon": 0, "name": "Invalid"},
                    {"lat": 37.7749, "lon": -122.4194, "name": "Valid"}
                ],
                "save_to_db": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Only valid coordinate should be processed
        assert data["successful"] == 1
    
    @pytest.mark.asyncio
    async def test_batch_process_large_dataset(
        self, client: AsyncClient, sample_hazards
    ):
        """Test batch processing with 100 locations."""
        coordinates = [
            {
                "lat": 37.0 + i * 0.1,
                "lon": -122.0 + i * 0.1,
                "name": f"Location_{i}"
            }
            for i in range(100)
        ]
        
        response = await client.post(
            "/api/export/batch-process",
            json={
                "coordinates": coordinates,
                "hazard_types": ["earthquake"],
                "save_to_db": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_processed"] == 100
        assert data["successful"] == 100


class TestHistoricalTrendsAPI:
    """Tests for /api/export/historical-trends endpoint."""
    
    @pytest.mark.asyncio
    async def test_export_historical_trends_basic(
        self, client: AsyncClient, sample_historical_data, sample_locations
    ):
        """Test basic historical trends export."""
        response = await client.post(
            "/api/export/historical-trends",
            json={
                "location_id": sample_locations[0].id,
                "hazard_type": "earthquake"
            }
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        
        csv_data = response.text
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)
        
        assert len(rows) > 0
        assert "event_id" in rows[0]
        assert "event_date" in rows[0]
        assert "severity" in rows[0]
    
    @pytest.mark.asyncio
    async def test_export_historical_trends_with_date_range(
        self, client: AsyncClient, sample_historical_data, sample_locations
    ):
        """Test historical trends export with date filtering."""
        start_date = (datetime.utcnow() - timedelta(days=200)).isoformat()
        end_date = datetime.utcnow().isoformat()
        
        response = await client.post(
            "/api/export/historical-trends",
            json={
                "location_id": sample_locations[0].id,
                "hazard_type": "earthquake",
                "start_date": start_date,
                "end_date": end_date
            }
        )
        
        assert response.status_code == 200
        
        csv_data = response.text
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)
        
        # Verify dates in range
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        for row in rows:
            event_date = datetime.fromisoformat(row["event_date"])
            assert start <= event_date <= end


class TestExportFormatsAPI:
    """Tests for /api/export/formats endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_supported_formats(self, client: AsyncClient):
        """Test getting supported export formats."""
        response = await client.get("/api/export/formats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "formats" in data
        assert "csv" in data["formats"]
        assert "risk_report_schema" in data
        assert "batch_size" in data
        
        # Verify CSV format details
        csv_format = data["formats"]["csv"]
        assert csv_format["mime_type"] == "text/csv"
        assert csv_format["supports_streaming"] is True
        
        # Verify schema
        schema = data["risk_report_schema"]
        assert "columns" in schema
        assert isinstance(schema["columns"], list)
        assert len(schema["columns"]) > 0


class TestExportPerformance:
    """Performance tests for export endpoints."""
    
    @pytest.mark.asyncio
    async def test_export_large_dataset_performance(
        self, client: AsyncClient, large_dataset_assessments
    ):
        """Test export performance with 10k+ records."""
        import time
        
        start_time = time.time()
        response = await client.post(
            "/api/export/risk-report",
            json={"stream": True}
        )
        
        # Read all content
        content = b""
        async for chunk in response.aiter_bytes():
            content += chunk
        
        duration = time.time() - start_time
        
        assert response.status_code == 200
        # Should complete within 10 seconds for 10k records
        assert duration < 10.0
        
        # Verify data integrity
        csv_data = content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)
        
        assert len(rows) > 1000


class TestExportErrorHandling:
    """Tests for error handling in export endpoints."""
    
    @pytest.mark.asyncio
    async def test_batch_process_empty_coordinates(
        self, client: AsyncClient, sample_hazards
    ):
        """Test batch processing with empty coordinates list."""
        response = await client.post(
            "/api/export/batch-process",
            json={
                "coordinates": [],
                "save_to_db": False
            }
        )
        
        # Should return 422 validation error
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_export_with_invalid_bounds(
        self, client: AsyncClient, sample_assessments
    ):
        """Test export with invalid location bounds."""
        response = await client.post(
            "/api/export/risk-report",
            json={
                "location_bounds": {
                    "min_lat": 100,  # Invalid
                    "max_lat": 90,
                    "min_lon": -180,
                    "max_lon": 180
                },
                "stream": False
            }
        )
        
        # Should return 422 validation error
        assert response.status_code == 422

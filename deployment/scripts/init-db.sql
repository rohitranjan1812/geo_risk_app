-- Initialize GeoRisk Database

-- Create extensions
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_locations_coordinates ON locations(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_hazards_type ON hazards(hazard_type);
CREATE INDEX IF NOT EXISTS idx_hazards_occurred_at ON hazards(occurred_at);
CREATE INDEX IF NOT EXISTS idx_risk_assessments_location ON risk_assessments(location_id);
CREATE INDEX IF NOT EXISTS idx_risk_assessments_date ON risk_assessments(assessment_date);

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE georisk_db TO georisk;

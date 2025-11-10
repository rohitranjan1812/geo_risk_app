"""Add performance indexes for geospatial and time-based queries

Revision ID: 002_performance_indexes
Revises: 001_initial_schema
Create Date: 2024-11-10

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add performance optimization indexes."""
    
    # Geospatial indexes for location lookups
    # Composite index on (latitude, longitude) for bounding box queries
    op.create_index(
        'idx_locations_lat_lon',
        'locations',
        ['latitude', 'longitude'],
        unique=False
    )
    
    # Individual indexes for range queries
    op.create_index(
        'idx_locations_latitude',
        'locations',
        ['latitude'],
        unique=False
    )
    
    op.create_index(
        'idx_locations_longitude',
        'locations',
        ['longitude'],
        unique=False
    )
    
    # Foreign key indexes for join performance
    op.create_index(
        'idx_risk_assessments_location_id',
        'risk_assessments',
        ['location_id'],
        unique=False
    )
    
    op.create_index(
        'idx_risk_assessments_hazard_id',
        'risk_assessments',
        ['hazard_id'],
        unique=False
    )
    
    # Composite index for location-hazard lookups
    op.create_index(
        'idx_risk_assessments_location_hazard',
        'risk_assessments',
        ['location_id', 'hazard_id'],
        unique=False
    )
    
    # Index on risk_level for filtering and aggregation
    op.create_index(
        'idx_risk_assessments_risk_level',
        'risk_assessments',
        ['risk_level'],
        unique=False
    )
    
    # Time-based index for recent assessments
    op.create_index(
        'idx_risk_assessments_assessed_at',
        'risk_assessments',
        ['assessed_at'],
        unique=False
    )
    
    # Historical data indexes
    op.create_index(
        'idx_historical_data_location_id',
        'historical_data',
        ['location_id'],
        unique=False
    )
    
    op.create_index(
        'idx_historical_data_hazard_id',
        'historical_data',
        ['hazard_id'],
        unique=False
    )
    
    # Time-based index for historical queries
    op.create_index(
        'idx_historical_data_event_date',
        'historical_data',
        ['event_date'],
        unique=False
    )
    
    # Composite index for location-hazard-date queries
    op.create_index(
        'idx_historical_data_location_hazard_date',
        'historical_data',
        ['location_id', 'hazard_id', 'event_date'],
        unique=False
    )
    
    # Hazard type index for filtering
    op.create_index(
        'idx_hazards_type',
        'hazards',
        ['hazard_type'],
        unique=False
    )


def downgrade() -> None:
    """Remove performance indexes."""
    
    # Drop all indexes in reverse order
    op.drop_index('idx_hazards_type', table_name='hazards')
    
    op.drop_index('idx_historical_data_location_hazard_date', table_name='historical_data')
    op.drop_index('idx_historical_data_event_date', table_name='historical_data')
    op.drop_index('idx_historical_data_hazard_id', table_name='historical_data')
    op.drop_index('idx_historical_data_location_id', table_name='historical_data')
    
    op.drop_index('idx_risk_assessments_assessed_at', table_name='risk_assessments')
    op.drop_index('idx_risk_assessments_risk_level', table_name='risk_assessments')
    op.drop_index('idx_risk_assessments_location_hazard', table_name='risk_assessments')
    op.drop_index('idx_risk_assessments_hazard_id', table_name='risk_assessments')
    op.drop_index('idx_risk_assessments_location_id', table_name='risk_assessments')
    
    op.drop_index('idx_locations_longitude', table_name='locations')
    op.drop_index('idx_locations_latitude', table_name='locations')
    op.drop_index('idx_locations_lat_lon', table_name='locations')

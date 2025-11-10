"""Initial schema for geographic risk assessment.

Revision ID: 001
Revises: 
Create Date: 2025-11-10 16:21:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables for geographic risk assessment."""
    
    # Create locations table
    op.create_table(
        'locations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('population_density', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('building_code_rating', sa.Float(), nullable=False, server_default='5.0'),
        sa.Column('infrastructure_quality', sa.Float(), nullable=False, server_default='5.0'),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_locations_id'), 'locations', ['id'], unique=False)
    op.create_index(op.f('ix_locations_name'), 'locations', ['name'], unique=False)
    
    # Create hazards table
    op.create_table(
        'hazards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hazard_type', sa.Enum('EARTHQUAKE', 'FLOOD', 'FIRE', 'STORM', name='hazardtype'), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('base_severity', sa.Float(), nullable=False, server_default='5.0'),
        sa.Column('weight_factors', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('hazard_type')
    )
    op.create_index(op.f('ix_hazards_hazard_type'), 'hazards', ['hazard_type'], unique=True)
    op.create_index(op.f('ix_hazards_id'), 'hazards', ['id'], unique=False)
    
    # Create risk_assessments table
    op.create_table(
        'risk_assessments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('hazard_id', sa.Integer(), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('risk_level', sa.Enum('LOW', 'MODERATE', 'HIGH', 'CRITICAL', name='risklevel'), nullable=False),
        sa.Column('confidence_level', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('factors_analysis', sa.JSON(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('assessed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['hazard_id'], ['hazards.id'], ),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_risk_assessments_assessed_at'), 'risk_assessments', ['assessed_at'], unique=False)
    op.create_index(op.f('ix_risk_assessments_hazard_id'), 'risk_assessments', ['hazard_id'], unique=False)
    op.create_index(op.f('ix_risk_assessments_id'), 'risk_assessments', ['id'], unique=False)
    op.create_index(op.f('ix_risk_assessments_location_id'), 'risk_assessments', ['location_id'], unique=False)
    
    # Create historical_data table
    op.create_table(
        'historical_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('hazard_id', sa.Integer(), nullable=False),
        sa.Column('event_date', sa.DateTime(), nullable=False),
        sa.Column('severity', sa.Float(), nullable=False),
        sa.Column('impact_description', sa.String(length=1000), nullable=True),
        sa.Column('casualties', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('economic_damage', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['hazard_id'], ['hazards.id'], ),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_historical_data_event_date'), 'historical_data', ['event_date'], unique=False)
    op.create_index(op.f('ix_historical_data_hazard_id'), 'historical_data', ['hazard_id'], unique=False)
    op.create_index(op.f('ix_historical_data_id'), 'historical_data', ['id'], unique=False)
    op.create_index(op.f('ix_historical_data_location_id'), 'historical_data', ['location_id'], unique=False)


def downgrade() -> None:
    """Drop all tables."""
    op.drop_index(op.f('ix_historical_data_location_id'), table_name='historical_data')
    op.drop_index(op.f('ix_historical_data_id'), table_name='historical_data')
    op.drop_index(op.f('ix_historical_data_hazard_id'), table_name='historical_data')
    op.drop_index(op.f('ix_historical_data_event_date'), table_name='historical_data')
    op.drop_table('historical_data')
    
    op.drop_index(op.f('ix_risk_assessments_location_id'), table_name='risk_assessments')
    op.drop_index(op.f('ix_risk_assessments_id'), table_name='risk_assessments')
    op.drop_index(op.f('ix_risk_assessments_hazard_id'), table_name='risk_assessments')
    op.drop_index(op.f('ix_risk_assessments_assessed_at'), table_name='risk_assessments')
    op.drop_table('risk_assessments')
    
    op.drop_index(op.f('ix_hazards_id'), table_name='hazards')
    op.drop_index(op.f('ix_hazards_hazard_type'), table_name='hazards')
    op.drop_table('hazards')
    
    op.drop_index(op.f('ix_locations_name'), table_name='locations')
    op.drop_index(op.f('ix_locations_id'), table_name='locations')
    op.drop_table('locations')

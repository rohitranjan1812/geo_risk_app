"""Database initialization script with sample data."""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import init_db, AsyncSessionLocal
from app.models import Hazard, HazardType, Location, HistoricalData
from datetime import datetime, timedelta


async def create_sample_hazards(db: AsyncSession):
    """Create default hazard configurations."""
    hazards_data = [
        {
            "hazard_type": HazardType.EARTHQUAKE,
            "name": "Earthquake",
            "description": "Seismic activity and ground shaking",
            "base_severity": 7.0,
            "weight_factors": {
                "building_codes": 0.35,
                "infrastructure": 0.25,
                "population": 0.15
            }
        },
        {
            "hazard_type": HazardType.FLOOD,
            "name": "Flood",
            "description": "Water overflow from rivers, storms, or sea level rise",
            "base_severity": 6.0,
            "weight_factors": {
                "infrastructure": 0.35,
                "population": 0.20,
                "building_codes": 0.15
            }
        },
        {
            "hazard_type": HazardType.FIRE,
            "name": "Fire",
            "description": "Wildfire or urban fire hazards",
            "base_severity": 5.5,
            "weight_factors": {
                "population": 0.30,
                "building_codes": 0.30,
                "infrastructure": 0.15
            }
        },
        {
            "hazard_type": HazardType.STORM,
            "name": "Storm",
            "description": "Severe weather including hurricanes, tornadoes, and windstorms",
            "base_severity": 6.5,
            "weight_factors": {
                "infrastructure": 0.30,
                "building_codes": 0.25,
                "population": 0.20
            }
        }
    ]
    
    for hazard_data in hazards_data:
        hazard = Hazard(**hazard_data)
        db.add(hazard)
    
    await db.commit()
    print("✓ Created 4 hazard types")


async def create_sample_locations(db: AsyncSession):
    """Create sample locations."""
    locations_data = [
        {
            "name": "San Francisco, CA",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "population_density": 7174.0,
            "building_code_rating": 8.5,
            "infrastructure_quality": 7.8,
            "extra_data": {"state": "California", "country": "USA"}
        },
        {
            "name": "New Orleans, LA",
            "latitude": 29.9511,
            "longitude": -90.0715,
            "population_density": 2029.0,
            "building_code_rating": 6.0,
            "infrastructure_quality": 5.5,
            "extra_data": {"state": "Louisiana", "country": "USA"}
        },
        {
            "name": "Tokyo, Japan",
            "latitude": 35.6762,
            "longitude": 139.6503,
            "population_density": 6158.0,
            "building_code_rating": 9.5,
            "infrastructure_quality": 9.0,
            "extra_data": {"country": "Japan"}
        },
        {
            "name": "Miami, FL",
            "latitude": 25.7617,
            "longitude": -80.1918,
            "population_density": 4770.0,
            "building_code_rating": 7.5,
            "infrastructure_quality": 7.0,
            "extra_data": {"state": "Florida", "country": "USA"}
        },
        {
            "name": "Los Angeles, CA",
            "latitude": 34.0522,
            "longitude": -118.2437,
            "population_density": 3276.0,
            "building_code_rating": 7.0,
            "infrastructure_quality": 6.5,
            "extra_data": {"state": "California", "country": "USA"}
        }
    ]
    
    for loc_data in locations_data:
        location = Location(**loc_data)
        db.add(location)
    
    await db.commit()
    print(f"✓ Created {len(locations_data)} sample locations")


async def create_sample_historical_data(db: AsyncSession):
    """Create sample historical event data."""
    from sqlalchemy import select
    
    # Get some locations and hazards
    result = await db.execute(select(Location).limit(3))
    locations = result.scalars().all()
    
    result = await db.execute(select(Hazard))
    hazards = result.scalars().all()
    hazards_dict = {h.hazard_type: h for h in hazards}
    
    # San Francisco - Earthquakes
    if len(locations) > 0 and HazardType.EARTHQUAKE in hazards_dict:
        sf = locations[0]
        eq_hazard = hazards_dict[HazardType.EARTHQUAKE]
        
        events = [
            (datetime(1989, 10, 17), 6.9, "Loma Prieta Earthquake", 63, 6000000000),
            (datetime(2014, 8, 24), 6.0, "South Napa Earthquake", 0, 400000000),
        ]
        
        for event_date, severity, description, casualties, damage in events:
            historical = HistoricalData(
                location_id=sf.id,
                hazard_id=eq_hazard.id,
                event_date=event_date,
                severity=severity,
                impact_description=description,
                casualties=casualties,
                economic_damage=damage
            )
            db.add(historical)
    
    # New Orleans - Floods/Storms
    if len(locations) > 1:
        nola = locations[1]
        
        if HazardType.STORM in hazards_dict:
            storm_hazard = hazards_dict[HazardType.STORM]
            historical = HistoricalData(
                location_id=nola.id,
                hazard_id=storm_hazard.id,
                event_date=datetime(2005, 8, 29),
                severity=9.5,
                impact_description="Hurricane Katrina",
                casualties=1833,
                economic_damage=125000000000
            )
            db.add(historical)
        
        if HazardType.FLOOD in hazards_dict:
            flood_hazard = hazards_dict[HazardType.FLOOD]
            historical = HistoricalData(
                location_id=nola.id,
                hazard_id=flood_hazard.id,
                event_date=datetime(2005, 8, 30),
                severity=9.0,
                impact_description="Katrina Flooding",
                casualties=1200,
                economic_damage=100000000000
            )
            db.add(historical)
    
    await db.commit()
    print("✓ Created sample historical event data")


async def init_sample_data():
    """Initialize database with sample data."""
    print("Initializing database...")
    
    # Create tables
    await init_db()
    print("✓ Database tables created")
    
    # Create sample data
    async with AsyncSessionLocal() as db:
        await create_sample_hazards(db)
        await create_sample_locations(db)
        await create_sample_historical_data(db)
    
    print("\n✓ Database initialization complete!")
    print("\nSample data created:")
    print("  - 4 hazard types (earthquake, flood, fire, storm)")
    print("  - 5 sample locations")
    print("  - Historical event data")


if __name__ == "__main__":
    asyncio.run(init_sample_data())

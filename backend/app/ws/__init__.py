"""WebSocket endpoints for real-time visualization."""
from fastapi import WebSocket, WebSocketDisconnect, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
import asyncio
from datetime import datetime

from app.db import get_db
from app.models import Location, Hazard, RiskAssessment
from app.services import AdvancedAnalyticsService


class RealTimeVisualizationManager:
    """Manages WebSocket connections for real-time risk visualization."""
    
    def __init__(self):
        """Initialize the connection manager."""
        self.active_connections: list[WebSocket] = []
        self.subscriptions: dict[str, set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, channel: str):
        """Connect a new WebSocket client.
        
        Args:
            websocket: WebSocket connection
            channel: Subscription channel (e.g., 'location:1', 'hazard:2')
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if channel not in self.subscriptions:
            self.subscriptions[channel] = set()
        self.subscriptions[channel].add(websocket)
    
    def disconnect(self, websocket: WebSocket, channel: str):
        """Disconnect a WebSocket client.
        
        Args:
            websocket: WebSocket connection
            channel: Subscription channel
        """
        self.active_connections.remove(websocket)
        if channel in self.subscriptions:
            self.subscriptions[channel].discard(websocket)
    
    async def broadcast(self, channel: str, data: dict):
        """Broadcast data to all subscribers of a channel.
        
        Args:
            channel: Subscription channel
            data: Data to broadcast
        """
        if channel in self.subscriptions:
            dead_connections = []
            for connection in self.subscriptions[channel]:
                try:
                    await connection.send_json(data)
                except Exception:
                    dead_connections.append(connection)
            
            for conn in dead_connections:
                self.subscriptions[channel].discard(conn)


# Global manager instance
visualization_manager = RealTimeVisualizationManager()


async def stream_location_risk_updates(
    location_id: int,
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db)
):
    """Stream real-time risk updates for a specific location.
    
    Args:
        location_id: Location ID to monitor
        websocket: WebSocket connection
        db: Database session
    """
    channel = f"location:{location_id}"
    
    try:
        await visualization_manager.connect(websocket, channel)
        
        result = await db.execute(
            select(Location).where(Location.id == location_id)
        )
        location = result.scalar_one_or_none()
        
        if not location:
            await websocket.send_json({
                'type': 'error',
                'message': f'Location {location_id} not found'
            })
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Send initial location data
        await websocket.send_json({
            'type': 'location_info',
            'data': {
                'id': location.id,
                'name': location.name,
                'latitude': location.latitude,
                'longitude': location.longitude,
                'connected_at': datetime.utcnow().isoformat()
            }
        })
        
        # Stream risk updates
        while True:
            result = await db.execute(
                select(RiskAssessment)
                .where(RiskAssessment.location_id == location_id)
                .order_by(RiskAssessment.assessed_at.desc())
                .limit(10)
            )
            assessments = result.scalars().all()
            
            if assessments:
                await websocket.send_json({
                    'type': 'risk_update',
                    'timestamp': datetime.utcnow().isoformat(),
                    'data': [
                        {
                            'assessment_id': a.id,
                            'hazard_id': a.hazard_id,
                            'risk_score': a.risk_score,
                            'risk_level': a.risk_level.value,
                            'confidence': a.confidence_level,
                            'assessed_at': a.assessed_at.isoformat()
                        }
                        for a in assessments
                    ]
                })
            
            await asyncio.sleep(5)
    
    except WebSocketDisconnect:
        visualization_manager.disconnect(websocket, channel)
    except Exception as e:
        visualization_manager.disconnect(websocket, channel)
        await websocket.send_json({
            'type': 'error',
            'message': str(e)
        })


async def stream_regional_risk_visualization(
    min_latitude: float,
    max_latitude: float,
    min_longitude: float,
    max_longitude: float,
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db)
):
    """Stream real-time regional risk visualization.
    
    Args:
        min_latitude: Minimum latitude
        max_latitude: Maximum latitude
        min_longitude: Minimum longitude
        max_longitude: Maximum longitude
        websocket: WebSocket connection
        db: Database session
    """
    channel = f"region:{min_latitude}:{max_latitude}:{min_longitude}:{max_longitude}"
    
    try:
        await visualization_manager.connect(websocket, channel)
        
        analytics = AdvancedAnalyticsService(db)
        
        # Send initial region info
        await websocket.send_json({
            'type': 'region_info',
            'data': {
                'bounds': {
                    'latitude': [min_latitude, max_latitude],
                    'longitude': [min_longitude, max_longitude]
                },
                'connected_at': datetime.utcnow().isoformat()
            }
        })
        
        # Stream regional risk updates
        while True:
            regional_risk = await analytics.calculate_regional_risk_index(
                min_latitude, max_latitude, min_longitude, max_longitude
            )
            
            await websocket.send_json({
                'type': 'region_risk_update',
                'timestamp': datetime.utcnow().isoformat(),
                'data': regional_risk
            })
            
            await asyncio.sleep(10)
    
    except WebSocketDisconnect:
        visualization_manager.disconnect(websocket, channel)
    except Exception as e:
        visualization_manager.disconnect(websocket, channel)
        await websocket.send_json({
            'type': 'error',
            'message': str(e)
        })


async def stream_hazard_risk_heatmap(
    hazard_id: int,
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db)
):
    """Stream real-time hazard risk heatmap data.
    
    Args:
        hazard_id: Hazard ID
        websocket: WebSocket connection
        db: Database session
    """
    channel = f"hazard:{hazard_id}"
    
    try:
        await visualization_manager.connect(websocket, channel)
        
        result = await db.execute(
            select(Hazard).where(Hazard.id == hazard_id)
        )
        hazard = result.scalar_one_or_none()
        
        if not hazard:
            await websocket.send_json({
                'type': 'error',
                'message': f'Hazard {hazard_id} not found'
            })
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Send hazard info
        await websocket.send_json({
            'type': 'hazard_info',
            'data': {
                'id': hazard.id,
                'type': hazard.hazard_type.value,
                'name': hazard.name,
                'base_severity': hazard.base_severity,
                'connected_at': datetime.utcnow().isoformat()
            }
        })
        
        analytics = AdvancedAnalyticsService(db)
        
        # Stream hotspot updates
        while True:
            hotspots = await analytics.calculate_risk_hotspots(hazard, limit=50)
            
            await websocket.send_json({
                'type': 'hotspot_update',
                'timestamp': datetime.utcnow().isoformat(),
                'hazard_type': hazard.hazard_type.value,
                'data': hotspots
            })
            
            await asyncio.sleep(15)
    
    except WebSocketDisconnect:
        visualization_manager.disconnect(websocket, channel)
    except Exception as e:
        visualization_manager.disconnect(websocket, channel)
        await websocket.send_json({
            'type': 'error',
            'message': str(e)
        })

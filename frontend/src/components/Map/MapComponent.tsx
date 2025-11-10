import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, useMapEvents } from 'react-leaflet';
import { LatLngExpression, Icon, LatLng } from 'leaflet';
import { Box, Typography, Paper } from '@mui/material';
import { useRiskContext } from '../../contexts/RiskContext';
import { Location } from '../../types';
import { getRiskColorFromScore } from '../../utils/helpers';
import HeatmapLayer from './HeatmapLayer';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons in React-Leaflet
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

const DefaultIcon = new Icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

interface MapComponentProps {
  onLocationSelect?: (lat: number, lng: number) => void;
  showHeatmap?: boolean;
}

// Component to handle map clicks
const MapClickHandler: React.FC<{ onLocationSelect: (lat: number, lng: number) => void }> = ({
  onLocationSelect,
}) => {
  useMapEvents({
    click: (e) => {
      onLocationSelect(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
};

// Component to update map view when location changes
const MapViewController: React.FC<{ center: LatLngExpression; zoom: number }> = ({
  center,
  zoom,
}) => {
  const map = useMap();

  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);

  return null;
};

const MapComponent: React.FC<MapComponentProps> = ({ onLocationSelect, showHeatmap = false }) => {
  const { selectedLocation, allLocations, assessmentResult } = useRiskContext();
  const [mapCenter, setMapCenter] = useState<LatLngExpression>([37.7749, -122.4194]); // San Francisco
  const [mapZoom, setMapZoom] = useState<number>(10);

  useEffect(() => {
    if (selectedLocation) {
      setMapCenter([selectedLocation.latitude, selectedLocation.longitude]);
      setMapZoom(12);
    }
  }, [selectedLocation]);

  const handleMapClick = (lat: number, lng: number) => {
    if (onLocationSelect) {
      onLocationSelect(lat, lng);
    }
  };

  const getMarkerIcon = (location: Location): Icon => {
    if (assessmentResult && assessmentResult.location.id === location.id) {
      const color = getRiskColorFromScore(assessmentResult.overall_risk_score);
      return new Icon({
        iconUrl: `data:image/svg+xml;base64,${btoa(`
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 36">
            <path fill="${color}" stroke="black" stroke-width="1" 
              d="M12 0C7.03 0 3 4.03 3 9c0 6.21 9 18 9 18s9-11.79 9-18c0-4.97-4.03-9-9-9z"/>
          </svg>
        `)}`,
        shadowUrl: iconShadow,
        iconSize: [30, 45],
        iconAnchor: [15, 45],
        popupAnchor: [0, -45],
      });
    }
    return DefaultIcon;
  };

  return (
    <Box sx={{ height: '100%', width: '100%', position: 'relative' }}>
      <MapContainer
        center={mapCenter}
        zoom={mapZoom}
        style={{ height: '100%', width: '100%' }}
        zoomControl={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <MapViewController center={mapCenter} zoom={mapZoom} />
        <MapClickHandler onLocationSelect={handleMapClick} />

        {/* Render location markers */}
        {allLocations.map((location) => (
          <Marker
            key={location.id}
            position={[location.latitude, location.longitude]}
            icon={getMarkerIcon(location)}
          >
            <Popup>
              <Paper elevation={0}>
                <Typography variant="subtitle1" fontWeight="bold">
                  {location.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Lat: {location.latitude.toFixed(4)}, Lng: {location.longitude.toFixed(4)}
                </Typography>
                <Typography variant="body2">
                  Population Density: {location.population_density.toFixed(0)}
                </Typography>
                <Typography variant="body2">
                  Building Code Rating: {location.building_code_rating.toFixed(1)}/10
                </Typography>
                <Typography variant="body2">
                  Infrastructure Quality: {location.infrastructure_quality.toFixed(1)}/10
                </Typography>
              </Paper>
            </Popup>
          </Marker>
        ))}

        {/* Heatmap layer */}
        {showHeatmap && assessmentResult && <HeatmapLayer />}
      </MapContainer>
    </Box>
  );
};

export default MapComponent;

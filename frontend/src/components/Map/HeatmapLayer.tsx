import { useEffect } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet.heat';
import { useRiskContext } from '../../contexts/RiskContext';
import { HeatmapPoint } from '../../types';

const HeatmapLayer: React.FC = () => {
  const map = useMap();
  const { assessmentResult, allLocations } = useRiskContext();

  useEffect(() => {
    if (!assessmentResult || !map) return;

    const heatmapPoints: HeatmapPoint[] = [];

    // Add current assessment location with high intensity
    const mainLocation = assessmentResult.location;
    const mainIntensity = assessmentResult.overall_risk_score / 100;
    heatmapPoints.push({
      lat: mainLocation.latitude,
      lng: mainLocation.longitude,
      intensity: mainIntensity,
    });

    // Add surrounding locations with lower intensities (simulated spread)
    const spreadRadius = 0.5; // degrees
    const spreadPoints = 20;

    for (let i = 0; i < spreadPoints; i++) {
      const angle = (Math.PI * 2 * i) / spreadPoints;
      const distance = Math.random() * spreadRadius;
      const lat = mainLocation.latitude + Math.cos(angle) * distance;
      const lng = mainLocation.longitude + Math.sin(angle) * distance;
      const intensity = mainIntensity * (1 - distance / spreadRadius) * 0.7;

      heatmapPoints.push({ lat, lng, intensity });
    }

    // Convert to format expected by leaflet.heat
    const heatData: [number, number, number][] = heatmapPoints.map((point) => [
      point.lat,
      point.lng,
      point.intensity,
    ]);

    // Create heatmap layer
    const heatLayer = (L as any).heatLayer(heatData, {
      radius: 25,
      blur: 15,
      maxZoom: 17,
      max: 1.0,
      gradient: {
        0.0: '#4caf50',
        0.3: '#ffeb3b',
        0.5: '#ff9800',
        0.7: '#f44336',
        1.0: '#9c27b0',
      },
    });

    heatLayer.addTo(map);

    return () => {
      map.removeLayer(heatLayer);
    };
  }, [assessmentResult, allLocations, map]);

  return null;
};

export default HeatmapLayer;

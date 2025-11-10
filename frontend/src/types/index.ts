// Type definitions matching backend schemas

export interface Location {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  population_density: number;
  building_code_rating: number;
  infrastructure_quality: number;
  extra_data?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
}

export interface LocationCreate {
  name: string;
  latitude: number;
  longitude: number;
  population_density?: number;
  building_code_rating?: number;
  infrastructure_quality?: number;
  extra_data?: Record<string, any>;
}

export interface Hazard {
  id: number;
  name: string;
  category: HazardCategory;
  description?: string;
  severity_scale?: string;
  created_at?: string;
}

export enum HazardCategory {
  EARTHQUAKE = 'earthquake',
  FLOOD = 'flood',
  FIRE = 'fire',
  STORM = 'storm'
}

export interface RiskFactors {
  population_density?: number;
  building_code_rating?: number;
  infrastructure_quality?: number;
  proximity_to_water?: number;
  elevation?: number;
  soil_type?: number;
}

export interface RiskAssessmentRequest {
  location_id?: number;
  location_data?: LocationCreate;
  hazard_types: HazardCategory[];
  custom_factors?: RiskFactors;
}

export interface RiskResult {
  hazard_type: HazardCategory;
  risk_score: number;
  risk_level: RiskLevel;
  confidence: number;
  contributing_factors: Record<string, number>;
  mitigation_recommendations: string[];
}

export enum RiskLevel {
  LOW = 'LOW',
  MODERATE = 'MODERATE',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL'
}

export interface RiskAssessmentResponse {
  location: Location;
  assessments: RiskResult[];
  overall_risk_score: number;
  timestamp: string;
}

export interface HistoricalData {
  id: number;
  location_id: number;
  hazard_id: number;
  event_date: string;
  severity: number;
  impact_description?: string;
  casualties?: number;
  economic_damage?: number;
  extra_data?: Record<string, any>;
  created_at?: string;
}

export interface HeatmapPoint {
  lat: number;
  lng: number;
  intensity: number;
}

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor: string[];
    borderColor: string[];
    borderWidth: number;
  }[];
}

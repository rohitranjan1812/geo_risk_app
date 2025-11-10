"""
Type definitions placeholder
"""

export interface Location {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  address?: string;
}

export interface RiskAssessment {
  id: number;
  locationId: number;
  overallRiskScore: number;
  earthquakeRisk: number;
  floodRisk: number;
  fireRisk: number;
  stormRisk: number;
  assessmentDate: string;
}

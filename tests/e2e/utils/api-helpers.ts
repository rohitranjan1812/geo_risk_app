import { APIRequestContext } from '@playwright/test';

/**
 * API helper functions for E2E tests
 */

export interface Location {
  id?: number;
  name: string;
  latitude: number;
  longitude: number;
  population_density?: number;
  building_code_rating?: number;
  infrastructure_quality?: number;
}

export interface RiskAssessmentRequest {
  location_id?: number;
  location?: Location;
  hazard_types: string[];
  risk_factors?: {
    population_density?: number;
    building_code_rating?: number;
    infrastructure_quality?: number;
  };
}

export interface RiskAssessment {
  hazard_type: string;
  hazard_name: string;
  risk_score: number;
  risk_level: string;
  confidence_level: number;
  factors_analysis: Record<string, number>;
  recommendations: string[];
}

export class ApiHelpers {
  constructor(private request: APIRequestContext, private baseURL: string) {}

  /**
   * Create a location via API
   */
  async createLocation(location: Location): Promise<Location> {
    const response = await this.request.post(`${this.baseURL}/api/locations`, {
      data: location,
    });
    
    if (!response.ok()) {
      throw new Error(`Failed to create location: ${response.status()}`);
    }
    
    return await response.json();
  }

  /**
   * Get location by ID
   */
  async getLocation(id: number): Promise<Location> {
    const response = await this.request.get(`${this.baseURL}/api/locations/${id}`);
    
    if (!response.ok()) {
      throw new Error(`Failed to get location: ${response.status()}`);
    }
    
    return await response.json();
  }

  /**
   * Assess risk for a location
   */
  async assessRisk(request: RiskAssessmentRequest): Promise<any> {
    const response = await this.request.post(`${this.baseURL}/api/assess-risk`, {
      data: request,
    });
    
    if (!response.ok()) {
      const text = await response.text();
      throw new Error(`Failed to assess risk: ${response.status()} - ${text}`);
    }
    
    return await response.json();
  }

  /**
   * Clean up test data
   */
  async deleteLocation(id: number): Promise<void> {
    await this.request.delete(`${this.baseURL}/api/locations/${id}`);
  }

  /**
   * Check backend health
   */
  async checkHealth(): Promise<boolean> {
    try {
      const response = await this.request.get(`${this.baseURL}/health`);
      return response.ok();
    } catch {
      return false;
    }
  }

  /**
   * Get all hazards
   */
  async getHazards(): Promise<any[]> {
    const response = await this.request.get(`${this.baseURL}/api/hazards`);
    
    if (!response.ok()) {
      throw new Error(`Failed to get hazards: ${response.status()}`);
    }
    
    return await response.json();
  }
}

import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  Location,
  LocationCreate,
  Hazard,
  RiskAssessmentRequest,
  RiskAssessmentResponse,
  HistoricalData,
} from '../types';

class ApiService {
  private api: AxiosInstance;

  constructor(baseURL: string = '/api') {
    this.api = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // Location endpoints
  async getLocations(): Promise<Location[]> {
    const response = await this.api.get<Location[]>('/locations');
    return response.data;
  }

  async getLocation(id: number): Promise<Location> {
    const response = await this.api.get<Location>(`/locations/${id}`);
    return response.data;
  }

  async createLocation(location: LocationCreate): Promise<Location> {
    const response = await this.api.post<Location>('/locations', location);
    return response.data;
  }

  async updateLocation(id: number, location: Partial<LocationCreate>): Promise<Location> {
    const response = await this.api.put<Location>(`/locations/${id}`, location);
    return response.data;
  }

  async deleteLocation(id: number): Promise<void> {
    await this.api.delete(`/locations/${id}`);
  }

  async searchLocations(query: string): Promise<Location[]> {
    const response = await this.api.get<Location[]>('/locations/search', {
      params: { q: query },
    });
    return response.data;
  }

  // Hazard endpoints
  async getHazards(): Promise<Hazard[]> {
    const response = await this.api.get<Hazard[]>('/hazards');
    return response.data;
  }

  async getHazard(id: number): Promise<Hazard> {
    const response = await this.api.get<Hazard>(`/hazards/${id}`);
    return response.data;
  }

  // Risk assessment
  async assessRisk(request: RiskAssessmentRequest): Promise<RiskAssessmentResponse> {
    const response = await this.api.post<RiskAssessmentResponse>('/assess-risk', request);
    return response.data;
  }

  // Historical data
  async getHistoricalData(locationId?: number, hazardId?: number): Promise<HistoricalData[]> {
    const response = await this.api.get<HistoricalData[]>('/historical-data', {
      params: {
        location_id: locationId,
        hazard_id: hazardId,
      },
    });
    return response.data;
  }

  async getHistoricalEvent(id: number): Promise<HistoricalData> {
    const response = await this.api.get<HistoricalData>(`/historical-data/${id}`);
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;

import { http, HttpResponse } from 'msw';
import { Location, Hazard, RiskAssessmentResponse, HazardCategory, RiskLevel } from '../../types';

export const mockLocations: Location[] = [
  {
    id: 1,
    name: 'San Francisco, CA',
    latitude: 37.7749,
    longitude: -122.4194,
    population_density: 7174.0,
    building_code_rating: 8.5,
    infrastructure_quality: 7.8,
    extra_data: { state: 'California', country: 'USA' },
  },
  {
    id: 2,
    name: 'Miami, FL',
    latitude: 25.7617,
    longitude: -80.1918,
    population_density: 5000.0,
    building_code_rating: 7.5,
    infrastructure_quality: 6.8,
    extra_data: { state: 'Florida', country: 'USA' },
  },
];

export const mockHazards: Hazard[] = [
  {
    id: 1,
    name: 'Earthquake',
    category: HazardCategory.EARTHQUAKE,
    severity: 7.5,
    probability: 0.65,
    description: 'Major earthquake risk',
    affected_radius_km: 50.0,
    extra_data: {},
  },
];

export const mockRiskAssessment: RiskAssessmentResponse = {
  location: mockLocations[0],
  assessments: [
    {
      hazard_type: HazardCategory.EARTHQUAKE,
      risk_score: 68.5,
      risk_level: RiskLevel.HIGH,
      confidence: 0.85,
      contributing_factors: {
        population_density: 25.0,
        building_code_rating: 22.5,
        infrastructure_quality: 21.0,
      },
      mitigation_recommendations: [
        'Enforce strict building codes',
        'Regular infrastructure inspections',
        'Emergency preparedness training',
      ],
    },
  ],
  overall_risk_score: 68.5,
  timestamp: new Date('2024-01-01T00:00:00Z').toISOString(),
};

export const handlers = [
  http.get('/api/locations', () => {
    return HttpResponse.json(mockLocations);
  }),
  http.get('/api/locations/search', ({ request }) => {
    const url = new URL(request.url);
    const query = url.searchParams.get('q');
    const filtered = mockLocations.filter((loc) =>
      loc.name.toLowerCase().includes(query?.toLowerCase() || '')
    );
    return HttpResponse.json(filtered);
  }),
  http.post('/api/assess-risk', async ({ request }) => {
    const body = await request.json() as any;
    return HttpResponse.json(mockRiskAssessment);
  }),
  http.get('/api/hazards', () => {
    return HttpResponse.json(mockHazards);
  }),
  http.post('/api/export', () => {
    return new HttpResponse('location,risk_score\nSan Francisco,68.5', {
      headers: {
        'Content-Type': 'text/csv',
      },
    });
  }),
];

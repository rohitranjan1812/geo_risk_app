import '@testing-library/jest-dom';

// Mock environment variables
process.env.REACT_APP_API_URL = 'http://localhost:8000/api';

// Mock leaflet
jest.mock('react-leaflet', () => ({
  MapContainer: ({ children }: any) => <div data-testid="map-container">{children}</div>,
  TileLayer: () => <div data-testid="tile-layer" />,
  Marker: ({ children }: any) => <div data-testid="marker">{children}</div>,
  Popup: ({ children }: any) => <div data-testid="popup">{children}</div>,
  useMap: () => ({
    setView: jest.fn(),
    removeLayer: jest.fn(),
  }),
  useMapEvents: () => null,
}));

// Mock leaflet.heat
jest.mock('leaflet.heat', () => ({
  heatLayer: jest.fn(() => ({
    addTo: jest.fn(),
    remove: jest.fn(),
  })),
}));

// Mock window.URL.createObjectURL
global.URL.createObjectURL = jest.fn(() => 'blob:mock-url');
global.URL.revokeObjectURL = jest.fn();

// Mock HTMLAnchorElement click
HTMLAnchorElement.prototype.click = jest.fn();

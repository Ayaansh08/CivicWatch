/**
 * Tests for Hotspots feature: HotspotLayer, HotspotList, and MapView overlay toggle.
 */
import React from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import MapView from "../../features/geo/MapView";
import HotspotLayer from "../../features/geo/HotspotLayer";
import HotspotList from "../../features/geo/HotspotList";
import { TOKEN_KEY } from "../../config";

// Mock react-leaflet components
jest.mock("react-leaflet", () => ({
  MapContainer: ({ children }) => <div data-testid="map-container">{children}</div>,
  TileLayer: () => <div data-testid="tile-layer" />,
  Circle: ({ children, center }) => (
    <div data-testid="leaflet-circle" data-lat={center[0]} data-lon={center[1]}>
      {children}
    </div>
  ),
  Popup: ({ children }) => <div data-testid="popup">{children}</div>,
  useMap: () => ({
    addLayer: jest.fn(),
    removeLayer: jest.fn(),
  }),
}));

// Mock MarkerClusterLayer and HeatLayer
jest.mock("../../features/geo/MarkerClusterLayer", () => {
  return function MockMarkerClusterLayer() {
    return <div data-testid="marker-cluster-layer" />;
  };
});
jest.mock("../../features/geo/HeatLayer", () => {
  return function MockHeatLayer() {
    return <div data-testid="heat-layer" />;
  };
});

// Mock MapFilters
jest.mock("../../features/geo/MapFilters", () => {
  return function MockMapFilters() {
    return <div data-testid="mock-filters" />;
  };
});

const mockHotspots = [
  { count: 6, center_lat: 28.625, center_lon: 77.365, category: "Pothole" },
  { count: 3, center_lat: 28.635, center_lon: 77.375, category: "Garbage" },
];

beforeEach(() => {
  localStorage.setItem(TOKEN_KEY, "test-jwt-token");

  // Global fetch mock returning complaints and hotspots
  global.fetch = jest.fn((url) => {
    if (url.includes("/geo/hotspots")) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockHotspots),
      });
    }
    return Promise.resolve({
      ok: true,
      status: 200,
      json: () => Promise.resolve([]),
    });
  });
});

afterEach(() => {
  jest.clearAllMocks();
  localStorage.clear();
});

test("checkbox shows and hides the hotspot zones", async () => {
  // Render MapView
  render(<MapView />);

  // Checkbox should be present and unchecked initially
  const checkbox = screen.getByRole("checkbox", { name: /Hotspots/i });
  expect(checkbox).not.toBeChecked();
  expect(screen.queryByTestId("leaflet-circle")).not.toBeInTheDocument();

  // Click checkbox to enable hotspots
  fireEvent.click(checkbox);
  expect(checkbox).toBeChecked();

  // Circles should appear on the map
  await waitFor(() => {
    const circles = screen.getAllByTestId("leaflet-circle");
    expect(circles).toHaveLength(2);
  });

  // Click checkbox again to hide hotspots
  fireEvent.click(checkbox);
  expect(checkbox).not.toBeChecked();
  expect(screen.queryByTestId("leaflet-circle")).not.toBeInTheDocument();
});

test("HotspotLayer renders a Circle and popup for each hotspot", () => {
  // Render HotspotLayer directly
  render(<HotspotLayer hotspots={mockHotspots} cell_size={0.01} />);

  // Check circles and popup text
  const circles = screen.getAllByTestId("leaflet-circle");
  expect(circles).toHaveLength(2);
  expect(screen.getByText(/Hotspot: 6 complaints, mostly Pothole/i)).toBeInTheDocument();
  expect(screen.getByText(/Hotspot: 3 complaints, mostly Garbage/i)).toBeInTheDocument();
});

test("HotspotList renders rows for each hotspot item", () => {
  // Render HotspotList table
  render(<HotspotList hotspots={mockHotspots} />);

  // Assert row content
  expect(screen.getByText("#1")).toBeInTheDocument();
  expect(screen.getByText("6")).toBeInTheDocument();
  expect(screen.getByText("Pothole")).toBeInTheDocument();
  expect(screen.getByText("28.625, 77.365")).toBeInTheDocument();

  expect(screen.getByText("#2")).toBeInTheDocument();
  expect(screen.getByText("3")).toBeInTheDocument();
  expect(screen.getByText("Garbage")).toBeInTheDocument();
  expect(screen.getByText("28.635, 77.375")).toBeInTheDocument();
});

test("HotspotList renders empty message when no hotspots exist", () => {
  // Render empty list
  render(<HotspotList hotspots={[]} />);

  // Check empty state
  expect(screen.getByText("No hotspots detected")).toBeInTheDocument();
});

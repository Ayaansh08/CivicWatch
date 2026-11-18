/**
 * Tests for HeatLayer integration and Markers/Heatmap toggle in MapView.
 */
import React from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import MapView from "../../features/geo/MapView";
import { TOKEN_KEY } from "../../config";

// Mock react-leaflet components
jest.mock("react-leaflet", () => ({
  MapContainer: ({ children }) => <div data-testid="map-container">{children}</div>,
  TileLayer: () => <div data-testid="tile-layer" />,
  useMap: () => ({
    addLayer: jest.fn(),
    removeLayer: jest.fn(),
  }),
}));

// Mock MarkerClusterLayer
jest.mock("../../features/geo/MarkerClusterLayer", () => {
  return function MockMarkerClusterLayer() {
    return <div data-testid="marker-cluster-layer" />;
  };
});

// Mock HeatLayer
jest.mock("../../features/geo/HeatLayer", () => {
  return function MockHeatLayer({ points }) {
    return <div data-testid="heat-layer" data-count={points ? points.length : 0} />;
  };
});

// Mock MapFilters to render simple select controls
jest.mock("../../features/geo/MapFilters", () => {
  return function MockMapFilters({ filters, onFilterChange }) {
    return (
      <div data-testid="mock-filters">
        <button
          type="button"
          onClick={() => onFilterChange({ ...filters, category_id: 1 })}
        >
          Set Category 1
        </button>
      </div>
    );
  };
});

const mockHeatmapData = [
  { lat: 28.62, lon: 77.36, count: 5 },
  { lat: 28.64, lon: 77.38, count: 2 },
];

beforeEach(() => {
  localStorage.setItem(TOKEN_KEY, "test-jwt-token");

  // Global fetch mock handling bbox and heatmap endpoints
  global.fetch = jest.fn((url) => {
    if (url.includes("/geo/heatmap")) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockHeatmapData),
      });
    }
    // Default complaints response
    return Promise.resolve({
      ok: true,
      status: 200,
      json: () =>
        Promise.resolve([
          {
            id: 1,
            title: "Road issue",
            category_name: "Pothole",
            status: "Submitted",
            priority: "High",
            latitude: 28.62,
            longitude: 77.36,
          },
        ]),
    });
  });
});

afterEach(() => {
  jest.clearAllMocks();
  localStorage.clear();
});

test("toggle switches from markers to heatmap layer", async () => {
  // Render MapView
  render(<MapView />);

  // Wait for initial markers layer
  await waitFor(() => {
    expect(screen.getByTestId("marker-cluster-layer")).toBeInTheDocument();
  });

  // Click Heatmap toggle button
  const heatmapButton = screen.getByRole("button", { name: /^Heatmap$/i });
  fireEvent.click(heatmapButton);

  // Assert HeatLayer is displayed instead of cluster layer
  await waitFor(() => {
    expect(screen.getByTestId("heat-layer")).toBeInTheDocument();
    expect(screen.queryByTestId("marker-cluster-layer")).not.toBeInTheDocument();
  });
});

test("heatmap data is fetched with active filters", async () => {
  // Render MapView
  render(<MapView />);

  // Apply category filter
  const filterBtn = screen.getByRole("button", { name: /Set Category 1/i });
  fireEvent.click(filterBtn);

  // Switch to heatmap view
  const heatmapButton = screen.getByRole("button", { name: /^Heatmap$/i });
  fireEvent.click(heatmapButton);

  // Verify fetch was called with /geo/heatmap and category_id=1
  await waitFor(() => {
    const urls = global.fetch.mock.calls.map((call) => call[0]);
    const heatmapCall = urls.find((u) => u.includes("/geo/heatmap") && u.includes("category_id=1"));
    expect(heatmapCall).toBeTruthy();
  });
});

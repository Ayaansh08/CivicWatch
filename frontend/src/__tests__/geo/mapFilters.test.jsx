/**
 * Tests for MapFilters component and MapView filter integration.
 */
import React from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import MapFilters from "../../features/geo/MapFilters";
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
  return function MockMarkerClusterLayer({ complaints }) {
    return <div data-testid="cluster-layer" data-count={complaints ? complaints.length : 0} />;
  };
});

// Mock HeatLayer
jest.mock("../../features/geo/HeatLayer", () => {
  return function MockHeatLayer() {
    return <div data-testid="heat-layer" />;
  };
});

const mockCategories = [
  { id: 1, name: "Pothole" },
  { id: 2, name: "Garbage" },
];

beforeEach(() => {
  localStorage.setItem(TOKEN_KEY, "test-jwt-token");

  // Global fetch mock handling categories and bbox endpoints
  global.fetch = jest.fn((url) => {
    if (url.includes("/complaints/categories")) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockCategories),
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
            title: "Road hole",
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

test("MapFilters renders category and status dropdowns and clear button", async () => {
  // Render MapFilters standalone
  const onFilterChange = jest.fn();
  render(<MapFilters filters={{ category_id: "", status: "" }} onFilterChange={onFilterChange} />);

  // Verify elements are present
  expect(screen.getByRole("combobox", { name: /Category/i })).toBeInTheDocument();
  expect(screen.getByRole("combobox", { name: /Status/i })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /Clear filters/i })).toBeInTheDocument();

  // Wait for categories to populate from API
  await waitFor(() => {
    expect(screen.getByText("Pothole")).toBeInTheDocument();
  });
});

test("choosing a category calls the API with category_id parameter", async () => {
  // Render MapView containing MapFilters
  render(<MapView />);

  // Wait for initial fetch
  await waitFor(() => {
    expect(global.fetch).toHaveBeenCalled();
  });

  // Wait for category options to load
  await waitFor(() => {
    expect(screen.getByText("Pothole")).toBeInTheDocument();
  });

  // Select category id 1
  const categorySelect = screen.getByRole("combobox", { name: /Category/i });
  fireEvent.change(categorySelect, { target: { value: "1" } });

  // Verify fetch was called with category_id=1
  await waitFor(() => {
    const urls = global.fetch.mock.calls.map((call) => call[0]);
    const matched = urls.some((u) => u.includes("category_id=1"));
    expect(matched).toBe(true);
  });
});

test("Clear filters button resets filter values", async () => {
  // Render MapFilters with active filters
  const onFilterChange = jest.fn();
  render(
    <MapFilters
      filters={{ category_id: 1, status: "Submitted" }}
      onFilterChange={onFilterChange}
    />
  );

  // Click clear button
  const clearBtn = screen.getByRole("button", { name: /Clear filters/i });
  fireEvent.click(clearBtn);

  // Assert callback was called with reset values
  expect(onFilterChange).toHaveBeenCalledWith({
    category_id: "",
    status: "",
  });
});

test("shows No complaints match these filters when filtered result is empty", async () => {
  // Initial complaints returned, subsequent filtered return empty
  global.fetch = jest.fn((url) => {
    if (url.includes("/complaints/categories")) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockCategories),
      });
    }
    if (url.includes("category_id=1")) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve([]),
      });
    }
    return Promise.resolve({
      ok: true,
      status: 200,
      json: () => Promise.resolve([]),
    });
  });

  // Render MapView
  render(<MapView />);

  // Wait for categories to load
  await waitFor(() => {
    expect(screen.getByText("Pothole")).toBeInTheDocument();
  });

  // Select category id 1
  const categorySelect = screen.getByRole("combobox", { name: /Category/i });
  fireEvent.change(categorySelect, { target: { value: "1" } });

  // Assert empty filtered message is shown
  await waitFor(() => {
    expect(screen.getByText("No complaints match these filters")).toBeInTheDocument();
  });
});

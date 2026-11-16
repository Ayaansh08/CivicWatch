/**
 * Tests for the MapView component real marker loading.
 * Verifies API requests with auth token, marker rendering, popup details,
 * loading indicator, empty list message, error handling, and complaint count.
 */
import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import MapView from "../../features/geo/MapView";
import { API_URL, TOKEN_KEY } from "../../config";

// Mock react-leaflet components with simple div containers and test IDs
jest.mock("react-leaflet", () => ({
  MapContainer: ({ children }) => <div data-testid="map-container">{children}</div>,
  TileLayer: () => <div data-testid="tile-layer" />,
  Marker: ({ children, position }) => (
    <div data-testid="marker" data-lat={position?.[0]} data-lon={position?.[1]}>
      {children}
    </div>
  ),
  Popup: ({ children }) => <div data-testid="popup">{children}</div>,
}));

// Sample mock complaints for testing
const mockApiComplaints = [
  {
    id: 1,
    title: "Large pothole on highway",
    category_name: "Pothole",
    status: "Submitted",
    priority: "High",
    latitude: 28.625,
    longitude: 77.365,
  },
  {
    id: 2,
    title: "Overflowing garbage dump",
    category_name: "Garbage",
    status: "In Progress",
    priority: "Medium",
    latitude: 28.630,
    longitude: 77.370,
  },
  {
    id: 3,
    title: "Broken streetlight pole",
    category_name: "Streetlight",
    status: "Resolved",
    priority: "Low",
    latitude: 28.635,
    longitude: 77.375,
  },
];

beforeEach(() => {
  // Store a mock token in localStorage
  localStorage.setItem(TOKEN_KEY, "test-jwt-token");

  // Default mock fetch implementation returning the 3 complaints
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      status: 200,
      json: () => Promise.resolve(mockApiComplaints),
    })
  );
});

afterEach(() => {
  // Clear all mocks and localStorage after each test
  jest.clearAllMocks();
  localStorage.clear();
});

test("MapView calls GET /geo/complaints/bbox with a Bearer token from localStorage", async () => {
  // Render MapView
  render(<MapView />);

  // Verify fetch was called with the correct URL and Authorization header
  await waitFor(() => {
    expect(global.fetch).toHaveBeenCalled();
  });

  const calledUrl = global.fetch.mock.calls[0][0];
  const calledOptions = global.fetch.mock.calls[0][1];

  expect(calledUrl).toContain(`${API_URL}/geo/complaints/bbox`);
  expect(calledOptions.headers.Authorization).toBe("Bearer test-jwt-token");
});

test("it renders one marker per complaint from the mocked response", async () => {
  // Render MapView
  render(<MapView />);

  // Wait for markers to appear
  await waitFor(() => {
    const markers = screen.getAllByTestId("marker");
    expect(markers).toHaveLength(3);
  });
});

test("each popup shows title, category and status", async () => {
  // Render MapView
  render(<MapView />);

  // Verify first complaint popup details are displayed
  await waitFor(() => {
    expect(screen.getByText("Large pothole on highway")).toBeInTheDocument();
    expect(screen.getByText(/Pothole/)).toBeInTheDocument();
    expect(screen.getByText(/Submitted/)).toBeInTheDocument();
  });
});

test("it shows 'Loading complaints...' first", () => {
  // Return an unresolved promise to check loading state
  global.fetch = jest.fn(() => new Promise(() => {}));

  // Render MapView
  render(<MapView />);

  // Loading indicator must be visible immediately
  expect(screen.getByText("Loading complaints...")).toBeInTheDocument();
});

test("it shows 'No complaints found in this area' for an empty list", async () => {
  // Return empty list of complaints
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      status: 200,
      json: () => Promise.resolve([]),
    })
  );

  // Render MapView
  render(<MapView />);

  // Empty state message should appear
  await waitFor(() => {
    expect(screen.getByText("No complaints found in this area")).toBeInTheDocument();
  });
});

test("it shows 'Could not load complaints' when fetch fails or returns 401", async () => {
  // Simulate 401 Unauthorized failure
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: false,
      status: 401,
      json: () => Promise.resolve({ detail: "Not authenticated" }),
    })
  );

  // Render MapView
  render(<MapView />);

  // Error message should be displayed
  await waitFor(() => {
    expect(screen.getByText("Could not load complaints")).toBeInTheDocument();
  });
});

test("the total count text '3 complaints' appears for three items", async () => {
  // Render MapView with 3 complaints
  render(<MapView />);

  // Total count indicator should appear
  await waitFor(() => {
    expect(screen.getByText("3 complaints")).toBeInTheDocument();
  });
});

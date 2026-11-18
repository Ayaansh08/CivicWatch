/**
 * Tests for map marker clustering, helper functions, and MapView state rendering.
 */
import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import MapView from "../../features/geo/MapView";
import { escapeHtml, buildPopupHtml, toHeatPoints } from "../../features/geo/mapHelpers";
import { API_URL, TOKEN_KEY } from "../../config";

// Mock react-leaflet components with simple div containers
jest.mock("react-leaflet", () => ({
  MapContainer: ({ children }) => <div data-testid="map-container">{children}</div>,
  TileLayer: () => <div data-testid="tile-layer" />,
  useMap: () => ({
    addLayer: jest.fn(),
    removeLayer: jest.fn(),
  }),
}));

// Mock MarkerClusterLayer with a div showing complaint count
jest.mock("../../features/geo/MarkerClusterLayer", () => {
  return function MockMarkerClusterLayer({ complaints }) {
    return (
      <div data-testid="marker-cluster-layer" data-count={complaints ? complaints.length : 0}>
        {(complaints || []).map((c) => (
          <div key={c.id} data-testid="cluster-item">
            {c.title}
          </div>
        ))}
      </div>
    );
  };
});

// Mock HeatLayer so real Leaflet plugin is not evaluated in Jest
jest.mock("../../features/geo/HeatLayer", () => {
  return function MockHeatLayer() {
    return <div data-testid="heat-layer" />;
  };
});

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

  // Default mock fetch implementation returning complaints and categories
  global.fetch = jest.fn((url) => {
    if (typeof url === "string" && url.includes("/complaints/categories")) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve([]),
      });
    }
    return Promise.resolve({
      ok: true,
      status: 200,
      json: () => Promise.resolve(mockApiComplaints),
    });
  });
});

afterEach(() => {
  // Clear mocks and localStorage
  jest.clearAllMocks();
  localStorage.clear();
});

test("escapeHtml escapes script tags and special characters", () => {
  // Test malicious script tags
  const raw = '<script>alert("xss")</script>&\'';
  const escaped = escapeHtml(raw);

  // Assert characters are replaced with safe entities
  expect(escaped).toBe("&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;&amp;&#039;");
});

test("buildPopupHtml escapes a malicious title", () => {
  // Complaint with script injection in title
  const maliciousComplaint = {
    title: "<img src=x onerror=alert(1)>",
    category_name: "Pothole",
    status: "Submitted",
    priority: "High",
  };
  const html = buildPopupHtml(maliciousComplaint);

  // Assert HTML does not contain unescaped tag
  expect(html).not.toContain("<img src=x onerror=alert(1)>");
  expect(html).toContain("&lt;img src=x onerror=alert(1)&gt;");
  expect(html).toContain("Pothole");
  expect(html).toContain("Submitted");
});

test("toHeatPoints formats points into lat lon intensity shape", () => {
  // Input point list
  const points = [
    { lat: 28.62, lon: 77.36, count: 5 },
    { latitude: 28.63, longitude: 77.37, intensity: 2 },
  ];
  const heatPoints = toHeatPoints(points);

  // Assert output structure
  expect(heatPoints).toEqual([
    [28.62, 77.36, 5],
    [28.63, 77.37, 2],
  ]);
});

test("MapView calls GET /geo/complaints/bbox with a Bearer token from localStorage", async () => {
  // Render MapView
  render(<MapView />);

  // Wait for bbox fetch call to complete
  await waitFor(() => {
    const bboxCall = global.fetch.mock.calls.find((call) =>
      call[0].includes(`${API_URL}/geo/complaints/bbox`)
    );
    expect(bboxCall).toBeTruthy();
    expect(bboxCall[1].headers.Authorization).toBe("Bearer test-jwt-token");
  });
});

test("MapView passes all complaints to the cluster layer", async () => {
  // Render MapView
  render(<MapView />);

  // Wait for cluster layer to receive the items
  await waitFor(() => {
    const items = screen.getAllByTestId("cluster-item");
    expect(items).toHaveLength(3);
  });
});

test("MapView shows Loading complaints message first", () => {
  // Return pending promise for bbox
  global.fetch = jest.fn((url) => {
    if (typeof url === "string" && url.includes("/complaints/categories")) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve([]),
      });
    }
    return new Promise(() => {});
  });

  // Render MapView
  render(<MapView />);

  // Check loading text
  expect(screen.getByText("Loading complaints...")).toBeInTheDocument();
});

test("MapView shows empty message when no complaints exist", async () => {
  // Return empty list
  global.fetch = jest.fn((url) => {
    if (typeof url === "string" && url.includes("/complaints/categories")) {
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

  // Check empty message
  await waitFor(() => {
    expect(screen.getByText("No complaints found in this area")).toBeInTheDocument();
  });
});

test("MapView shows error message when fetch fails", async () => {
  // Simulate 401 error
  global.fetch = jest.fn((url) => {
    if (typeof url === "string" && url.includes("/complaints/categories")) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve([]),
      });
    }
    return Promise.resolve({
      ok: false,
      status: 401,
      json: () => Promise.resolve({ detail: "Not authenticated" }),
    });
  });

  // Render MapView
  render(<MapView />);

  // Check error message
  await waitFor(() => {
    expect(screen.getByText("Could not load complaints")).toBeInTheDocument();
  });
});

test("MapView shows total complaints count message", async () => {
  // Render MapView
  render(<MapView />);

  // Check count indicator
  await waitFor(() => {
    expect(screen.getByText("3 complaints")).toBeInTheDocument();
  });
});

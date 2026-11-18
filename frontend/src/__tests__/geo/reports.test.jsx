/**
 * Tests for ReportsPage and BarChart components.
 */
import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import ReportsPage from "../../features/geo/ReportsPage";
import BarChart from "../../features/geo/BarChart";
import { TOKEN_KEY } from "../../config";

const mockReportData = {
  total: 10,
  by_status: [
    { status: "Submitted", count: 6 },
    { status: "Resolved", count: 4 },
  ],
  by_category: [
    { category: "Pothole", count: 7 },
    { category: "Garbage", count: 3 },
  ],
  by_area: [
    { area: "28.62,77.36", count: 8 },
    { area: "28.65,77.40", count: 2 },
  ],
  avg_resolution_hours: 14.5,
};

beforeEach(() => {
  localStorage.setItem(TOKEN_KEY, "test-jwt-token");

  // Global fetch mock returning mock report
  global.fetch = jest.fn((url) => {
    if (url.includes("/geo/reports/summary")) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockReportData),
      });
    }
    return Promise.resolve({
      ok: true,
      status: 200,
      json: () => Promise.resolve({}),
    });
  });
});

afterEach(() => {
  jest.clearAllMocks();
  localStorage.clear();
});

test("BarChart bar widths are proportional to the values", () => {
  const items = [
    { label: "High Volume", value: 100 },
    { label: "Low Volume", value: 50 },
  ];

  render(<BarChart items={items} />);

  // Retrieve bar fill elements
  const fills = screen.getAllByTestId("bar-fill");
  expect(fills).toHaveLength(2);

  // Maximum value is 100, so width is 100% and 50%
  expect(fills[0].style.width).toBe("100%");
  expect(fills[1].style.width).toBe("50%");
});

test("ReportsPage shows summary cards and charts from mocked data", async () => {
  render(
    <MemoryRouter>
      <ReportsPage />
    </MemoryRouter>
  );

  // Wait for report data to render
  await waitFor(() => {
    expect(screen.getByText("Total Complaints")).toBeInTheDocument();
    expect(screen.getByText("10")).toBeInTheDocument();
    expect(screen.getByText("Resolved Complaints")).toBeInTheDocument();
    expect(screen.getAllByText("4").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("14.5 hrs")).toBeInTheDocument();
  });

  // Check section headings and labels
  expect(screen.getByText("Complaints by Status")).toBeInTheDocument();
  expect(screen.getByText("Complaints by Category")).toBeInTheDocument();
  expect(screen.getByText("Top Geographic Areas")).toBeInTheDocument();
  expect(screen.getByText("Pothole")).toBeInTheDocument();
  expect(screen.getByText("28.62,77.36")).toBeInTheDocument();
});

test("ReportsPage shows empty state when total is zero", async () => {
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      status: 200,
      json: () =>
        Promise.resolve({
          total: 0,
          by_status: [],
          by_category: [],
          by_area: [],
          avg_resolution_hours: null,
        }),
    })
  );

  render(
    <MemoryRouter>
      <ReportsPage />
    </MemoryRouter>
  );

  // Assert empty message appears
  await waitFor(() => {
    expect(screen.getByText("No data yet")).toBeInTheDocument();
  });
});

test("ReportsPage shows error state when API request fails", async () => {
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: false,
      status: 500,
      json: () => Promise.resolve({ detail: "Server error" }),
    })
  );

  render(
    <MemoryRouter>
      <ReportsPage />
    </MemoryRouter>
  );

  // Assert error message appears
  await waitFor(() => {
    expect(screen.getByText("Could not load report")).toBeInTheDocument();
  });
});

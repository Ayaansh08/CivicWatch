/**
 * Tests for AuthorityDashboard component (CW-305).
 *
 * Uses mocked fetch to avoid real network calls.
 */
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import AuthorityDashboard from "../../features/authority/AuthorityDashboard";

// Sample complaint data returned by the mocked API
const FAKE_COMPLAINTS = [
  {
    id: 1,
    title: "Broken pipe",
    category_name: "Water",
    status: "Submitted",
    priority: "Medium",
    department_name: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 2,
    title: "Pothole",
    category_name: "Roads",
    status: "Under Review",
    priority: "High",
    department_name: "Roads Department",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

function renderDashboard() {
  return render(
    <MemoryRouter>
      <AuthorityDashboard />
    </MemoryRouter>
  );
}

beforeEach(() => {
  // Set a fake token so the dashboard does not show the login prompt
  localStorage.setItem("token", "fake-jwt-token");
  // Mock fetch to return fake complaints
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve(FAKE_COMPLAINTS),
    })
  );
});

afterEach(() => {
  localStorage.clear();
  jest.resetAllMocks();
});

test("dashboard renders complaint rows from the API", async () => {
  renderDashboard();
  // Both complaint titles should appear in the table
  await waitFor(() => {
    expect(screen.getByText("Broken pipe")).toBeTruthy();
    expect(screen.getByText("Pothole")).toBeTruthy();
  });
});

test("changing the status filter calls the API with the status parameter", async () => {
  renderDashboard();
  await waitFor(() => screen.getByText("Broken pipe"));
  // Change the filter dropdown to "Submitted"
  const select = screen.getByLabelText("Filter by status");
  await userEvent.selectOptions(select, "Submitted");
  // The second fetch call should include status=Submitted in the URL
  await waitFor(() => {
    const calls = global.fetch.mock.calls;
    const lastUrl = calls[calls.length - 1][0];
    expect(lastUrl).toContain("status=Submitted");
  });
});

test("dashboard shows empty message when no complaints are returned", async () => {
  // Override fetch to return an empty list
  global.fetch = jest.fn(() =>
    Promise.resolve({ ok: true, json: () => Promise.resolve([]) })
  );
  renderDashboard();
  await waitFor(() => {
    expect(screen.getByText("No complaints found")).toBeTruthy();
  });
});

test("dashboard shows error message when the API call fails", async () => {
  // Override fetch to simulate a server error
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: false,
      json: () => Promise.resolve({ detail: "Server error" }),
    })
  );
  renderDashboard();
  await waitFor(() => {
    expect(screen.getByText("Server error")).toBeTruthy();
  });
});

test("dashboard shows login prompt when no token is present", () => {
  localStorage.clear();
  renderDashboard();
  expect(screen.getByText("Please log in to continue")).toBeTruthy();
});

import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import NavBar from "../../features/auth/NavBar";
import { TOKEN_KEY } from "../../config";

/** Reset mocked fetch and localStorage before each test. */
beforeEach(() => {
  global.fetch = jest.fn();
  localStorage.clear();
});

/** Clear mocks and localStorage after each test. */
afterEach(() => {
  jest.clearAllMocks();
  localStorage.clear();
});

/** Render NavBar inside a router so Link components work. */
function renderNavBar() {
  return render(
    <MemoryRouter>
      <NavBar />
    </MemoryRouter>
  );
}

test("navbar shows nothing when no token is in localStorage", () => {
  // No token set, so the navbar should be empty
  renderNavBar();
  // The navbar returns null when not logged in
  expect(screen.queryByRole("link")).toBeNull();
});

test("navbar shows citizen links when logged in as a citizen", async () => {
  // Set a token and return a citizen profile from /auth/me
  localStorage.setItem(TOKEN_KEY, "citizen-token");
  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: () => Promise.resolve({ id: 1, name: "Sam", email: "sam@test.com", role: "citizen" }),
  });

  renderNavBar();

  // Wait for the user profile to load
  expect(await screen.findByText("Report")).toBeInTheDocument();
  expect(screen.getByText("My Complaints")).toBeInTheDocument();
  // Admin link should NOT be visible for citizens
  expect(screen.queryByText("Admin")).toBeNull();
  // Authority links should NOT be visible for citizens
  expect(screen.queryByText("Authority")).toBeNull();
});

test("navbar shows officer links when logged in as an officer", async () => {
  // Set a token and return an officer profile from /auth/me
  localStorage.setItem(TOKEN_KEY, "officer-token");
  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: () => Promise.resolve({ id: 2, name: "Raj", email: "raj@test.com", role: "officer" }),
  });

  renderNavBar();

  // Wait for the user profile to load
  expect(await screen.findByText("Authority")).toBeInTheDocument();
  expect(screen.getByText("Map")).toBeInTheDocument();
  expect(screen.getByText("Reports")).toBeInTheDocument();
  // Admin link should NOT be visible for officers
  expect(screen.queryByText("Admin")).toBeNull();
});

test("navbar shows admin link when logged in as an admin", async () => {
  // Set a token and return an admin profile from /auth/me
  localStorage.setItem(TOKEN_KEY, "admin-token");
  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: () => Promise.resolve({ id: 3, name: "Admin", email: "admin@test.com", role: "admin" }),
  });

  renderNavBar();

  // Wait for the user profile to load and confirm Admin link is present
  expect(await screen.findByText("Admin")).toBeInTheDocument();
  expect(screen.getByText("Authority")).toBeInTheDocument();
  expect(screen.getByText("Map")).toBeInTheDocument();
  expect(screen.getByText("Report")).toBeInTheDocument();
});

test("navbar shows nothing when the token fetch returns 401", async () => {
  // Set an expired token that the backend rejects
  localStorage.setItem(TOKEN_KEY, "expired-token");
  global.fetch.mockResolvedValueOnce({
    ok: false,
    status: 401,
    json: () => Promise.resolve({ detail: "Invalid token" }),
  });

  renderNavBar();

  // Wait for fetch to settle then confirm no links appear
  await waitFor(() => {
    expect(screen.queryByRole("link")).toBeNull();
  });
  // Token should be removed from localStorage
  expect(localStorage.getItem(TOKEN_KEY)).toBeNull();
});

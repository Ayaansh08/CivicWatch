import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import ProtectedRoute from "../../features/auth/ProtectedRoute";
import { TOKEN_KEY } from "../../config";

/** Reset mocked fetch and localStorage before each test. */
beforeEach(() => {
  // Replace global fetch with a Jest mock function
  global.fetch = jest.fn();
  // Start each test with an empty localStorage
  localStorage.clear();
});

/** Clear mocks and localStorage after each test. */
afterEach(() => {
  jest.clearAllMocks();
  localStorage.clear();
});

/** Render a protected test route alongside a /login route inside MemoryRouter. */
function renderProtected(allowedRoles) {
  return render(
    <MemoryRouter initialEntries={["/secret"]}>
      <Routes>
        <Route path="/login" element={<div>Login Screen</div>} />
        <Route
          path="/secret"
          element={
            <ProtectedRoute allowedRoles={allowedRoles}>
              <div>Secret Content</div>
            </ProtectedRoute>
          }
        />
      </Routes>
    </MemoryRouter>
  );
}

describe("ProtectedRoute", () => {
  test("redirects to the login page when there is no token in localStorage", () => {
    // Render without setting any token in localStorage
    renderProtected(["citizen", "officer", "admin"]);

    // Expect immediate redirect to /login
    expect(screen.getByText("Login Screen")).toBeInTheDocument();
  });

  test("shows Checking access... while loading the current user", () => {
    // Store a token and mock a fetch promise that stays pending
    localStorage.setItem(TOKEN_KEY, "valid-token");
    global.fetch.mockImplementation(() => new Promise(() => {}));

    // Render the protected route
    renderProtected(["officer", "admin"]);

    // Expect the loading message while /auth/me is in flight
    expect(screen.getByText("Checking access...")).toBeInTheDocument();
  });

  test("shows protected content when the user's role is allowed", async () => {
    // Store a token and return an officer profile from /auth/me
    localStorage.setItem(TOKEN_KEY, "officer-token");
    global.fetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: () =>
        Promise.resolve({
          id: 2,
          name: "Officer Raj",
          email: "raj@civicwatch.com",
          role: "officer",
        }),
    });

    // Render a route that allows officers and admins
    renderProtected(["officer", "admin"]);

    // Expect the protected content to be displayed
    expect(await screen.findByText("Secret Content")).toBeInTheDocument();
  });

  test("shows permission message when the user's role is not allowed", async () => {
    // Store a token and return a citizen profile from /auth/me
    localStorage.setItem(TOKEN_KEY, "citizen-token");
    global.fetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: () =>
        Promise.resolve({
          id: 3,
          name: "Citizen Sam",
          email: "sam@civicwatch.com",
          role: "citizen",
        }),
    });

    // Render a route restricted to officers and admins
    renderProtected(["officer", "admin"]);

    // Expect the permission denied message
    expect(
      await screen.findByText("You do not have permission to view this page")
    ).toBeInTheDocument();
  });

  test("removes the token and redirects to login if /auth/me returns 401", async () => {
    // Store an expired token and return 401 from /auth/me
    localStorage.setItem(TOKEN_KEY, "expired-token");
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: () => Promise.resolve({ detail: "Invalid or expired token" }),
    });

    // Render the protected route
    renderProtected(["citizen", "officer", "admin"]);

    // Expect redirect to /login and token removal from localStorage
    expect(await screen.findByText("Login Screen")).toBeInTheDocument();
    await waitFor(() => {
      expect(localStorage.getItem(TOKEN_KEY)).toBeNull();
    });
  });
});

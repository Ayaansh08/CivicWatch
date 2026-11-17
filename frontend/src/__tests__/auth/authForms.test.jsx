import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import LoginPage from "../../features/auth/LoginPage";
import RegisterPage from "../../features/auth/RegisterPage";
import { TOKEN_KEY } from "../../config";

/** Reset mocked fetch and localStorage before each test. */
beforeEach(() => {
  // Replace global fetch with a Jest mock function
  global.fetch = jest.fn();
  // Start each test with an empty localStorage
  localStorage.clear();
});

/** Clear mock call history after each test. */
afterEach(() => {
  jest.clearAllMocks();
  localStorage.clear();
});

describe("LoginPage", () => {
  test("login form shows email and password fields", () => {
    // Render the login page inside a router
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    // Check that email and password inputs are visible
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  test("submitting an empty login shows Email is required and Password is required", () => {
    // Render the login page
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    // Click the submit button without typing anything
    fireEvent.click(screen.getByRole("button", { name: /log in/i }));

    // Expect both required-field validation messages
    expect(screen.getByText("Email is required")).toBeInTheDocument();
    expect(screen.getByText("Password is required")).toBeInTheDocument();
  });

  test("a failed login shows the error message returned by the API", async () => {
    // Mock a 401 response from the backend login endpoint
    global.fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ detail: "Invalid email or password" }),
    });

    // Render the login page
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    // Fill in email and password and submit the form
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: "wrong@example.com" },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: "wrongpass" },
    });
    fireEvent.click(screen.getByRole("button", { name: /log in/i }));

    // Expect the API error detail to appear on screen
    expect(
      await screen.findByText("Invalid email or password")
    ).toBeInTheDocument();
  });

  test("a successful login stores the token under TOKEN_KEY and calls onSuccess", async () => {
    // Mock a successful login response with a JWT access token
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({ access_token: "jwt-123", token_type: "bearer" }),
    });
    // Create a mock callback to check onSuccess is called
    const handleSuccess = jest.fn();

    // Render the login page with the onSuccess prop
    render(
      <MemoryRouter>
        <LoginPage onSuccess={handleSuccess} />
      </MemoryRouter>
    );

    // Fill in valid credentials and submit
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: "alice@example.com" },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: "secret123" },
    });
    fireEvent.click(screen.getByRole("button", { name: /log in/i }));

    // Verify token is saved in localStorage and onSuccess was called
    await waitFor(() => {
      expect(localStorage.getItem(TOKEN_KEY)).toBe("jwt-123");
      expect(handleSuccess).toHaveBeenCalledTimes(1);
    });
  });
});

describe("RegisterPage", () => {
  test("register form shows name, email and password fields", () => {
    // Render the register page inside a router
    render(
      <MemoryRouter>
        <RegisterPage />
      </MemoryRouter>
    );

    // Check that name, email, and password inputs are visible
    expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  test("register with a password under 6 characters shows a length error", () => {
    // Render the register page
    render(
      <MemoryRouter>
        <RegisterPage />
      </MemoryRouter>
    );

    // Fill in fields using a short 3-character password
    fireEvent.change(screen.getByLabelText(/name/i), {
      target: { value: "Alice" },
    });
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: "alice@example.com" },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: "abc" },
    });

    // Submit the form
    fireEvent.click(screen.getByRole("button", { name: /register/i }));

    // Expect the password length validation message
    expect(
      screen.getByText("Password must be at least 6 characters")
    ).toBeInTheDocument();
  });

  test("a successful register shows Account created. Please log in.", async () => {
    // Mock a 201 response from the backend register endpoint
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          id: 1,
          name: "Alice",
          email: "alice@example.com",
          role: "citizen",
        }),
    });

    // Render the register page
    render(
      <MemoryRouter>
        <RegisterPage />
      </MemoryRouter>
    );

    // Fill in valid registration details and submit
    fireEvent.change(screen.getByLabelText(/name/i), {
      target: { value: "Alice" },
    });
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: "alice@example.com" },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: "secret123" },
    });
    fireEvent.click(screen.getByRole("button", { name: /register/i }));

    // Expect the confirmation message to appear
    expect(
      await screen.findByText("Account created. Please log in.")
    ).toBeInTheDocument();
  });
});

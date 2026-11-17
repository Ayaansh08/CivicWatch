import { API_URL } from "../../config";

/**
 * Send login credentials to the backend and return the token response.
 * Throws an Error with the backend's detail message if login fails.
 */
export async function login(email, password) {
  // Send a POST request with JSON email and password
  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  // Parse the JSON response body
  const data = await response.json();

  // Throw the API error detail if the request failed
  if (!response.ok) {
    throw new Error(data.detail || "Login failed");
  }

  return data;
}

/**
 * Send new user details to the backend to create a citizen account.
 * Throws an Error with the backend's detail message if registration fails.
 */
export async function register(name, email, password) {
  // Send a POST request with JSON name, email, and password
  const response = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password }),
  });

  // Parse the JSON response body
  const data = await response.json();

  // Throw the API error detail if the request failed
  if (!response.ok) {
    throw new Error(data.detail || "Registration failed");
  }

  return data;
}

/**
 * Fetch the currently logged-in user's profile using their Bearer token.
 * Attaches the HTTP status code to the thrown Error when the request fails.
 */
export async function getCurrentUser(token) {
  // Send a GET request to /auth/me with the Bearer token header
  const response = await fetch(`${API_URL}/auth/me`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  // Parse the JSON response body
  const data = await response.json();

  // Throw an Error carrying the HTTP status when authentication fails
  if (!response.ok) {
    const error = new Error(data.detail || "Unable to verify user");
    error.status = response.status;
    throw error;
  }

  return data;
}

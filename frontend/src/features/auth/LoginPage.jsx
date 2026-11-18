import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { TOKEN_KEY } from "../../config";
import { login } from "./authApi";
import "./auth.css";

/**
 * Displays the login form, validates inputs, calls POST /auth/login,
 * saves the JWT token in localStorage, and notifies onSuccess or redirects to "/".
 */
function LoginPage({ onSuccess }) {
  // Form input states
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  // Validation and API error states
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // Router helper for navigating after login
  const navigate = useNavigate();

  /** Validate form fields and return an object of error messages. */
  function validateForm() {
    const newErrors = {};
    // Require a non-empty email
    if (!email.trim()) {
      newErrors.email = "Email is required";
    }
    // Require a non-empty password
    if (!password.trim()) {
      newErrors.password = "Password is required";
    }
    return newErrors;
  }

  /** Handle login form submission. */
  async function handleSubmit(event) {
    // Prevent default browser page reload
    event.preventDefault();
    setApiError("");

    // Run client-side validation before calling the API
    const validationErrors = validateForm();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    // Clear previous field errors and start submission
    setErrors({});
    setSubmitting(true);

    try {
      // Call the login API and store the returned JWT token
      const data = await login(email.trim(), password);
      localStorage.setItem(TOKEN_KEY, data.access_token);

      // Call the optional callback prop or navigate to the home page
      if (onSuccess) {
        onSuccess(data);
      } else {
        navigate("/");
      }
    } catch (err) {
      // Display the error message returned by the API
      setApiError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-container">
      <h1>Log In</h1>

      {apiError && (
        <div className="auth-error-banner" role="alert">
          {apiError}
        </div>
      )}

      <form className="auth-form" onSubmit={handleSubmit} noValidate>
        <div className="auth-field">
          <label htmlFor="login-email">Email</label>
          <input
            id="login-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
          />
          {errors.email && <p className="auth-field-error">{errors.email}</p>}
        </div>

        <div className="auth-field">
          <label htmlFor="login-password">Password</label>
          <input
            id="login-password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
          />
          {errors.password && (
            <p className="auth-field-error">{errors.password}</p>
          )}
        </div>

        <button className="auth-button" type="submit" disabled={submitting}>
          {submitting ? "Logging in..." : "Log In"}
        </button>
      </form>

      <p className="auth-footer">
        Need an account? <Link to="/register">Register</Link>
      </p>
    </div>
  );
}

export default LoginPage;

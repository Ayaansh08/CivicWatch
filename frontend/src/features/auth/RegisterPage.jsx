import React, { useState } from "react";
import { Link } from "react-router-dom";
import { register } from "./authApi";
import "./auth.css";

/**
 * Displays the registration form, validates inputs, calls POST /auth/register,
 * and shows a confirmation message when the account is created.
 */
function RegisterPage() {
  // Form input states
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  // Validation, API error, and success states
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);

  /** Validate registration fields and return an object of error messages. */
  function validateForm() {
    const newErrors = {};
    // Require a non-empty name
    if (!name.trim()) {
      newErrors.name = "Name is required";
    }
    // Require a non-empty email
    if (!email.trim()) {
      newErrors.email = "Email is required";
    }
    // Require a password of at least 6 characters
    if (!password) {
      newErrors.password = "Password is required";
    } else if (password.length < 6) {
      newErrors.password = "Password must be at least 6 characters";
    }
    return newErrors;
  }

  /** Handle registration form submission. */
  async function handleSubmit(event) {
    // Prevent default browser page reload
    event.preventDefault();
    setApiError("");
    setSuccessMessage("");

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
      // Send registration data to the backend
      await register(name.trim(), email.trim(), password);
      // Show success confirmation and reset fields
      setSuccessMessage("Account created. Please log in.");
      setName("");
      setEmail("");
      setPassword("");
    } catch (err) {
      // Display the error message returned by the API
      setApiError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-container">
      <h1>Register</h1>

      {apiError && (
        <div className="auth-error-banner" role="alert">
          {apiError}
        </div>
      )}

      {successMessage && (
        <div className="auth-success-banner" role="status">
          {successMessage}
        </div>
      )}

      <form className="auth-form" onSubmit={handleSubmit} noValidate>
        <div className="auth-field">
          <label htmlFor="register-name">Name</label>
          <input
            id="register-name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Your full name"
          />
          {errors.name && <p className="auth-field-error">{errors.name}</p>}
        </div>

        <div className="auth-field">
          <label htmlFor="register-email">Email</label>
          <input
            id="register-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
          />
          {errors.email && <p className="auth-field-error">{errors.email}</p>}
        </div>

        <div className="auth-field">
          <label htmlFor="register-password">Password</label>
          <input
            id="register-password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="At least 6 characters"
          />
          {errors.password && (
            <p className="auth-field-error">{errors.password}</p>
          )}
        </div>

        <button className="auth-button" type="submit" disabled={submitting}>
          {submitting ? "Creating account..." : "Register"}
        </button>
      </form>

      <p className="auth-footer">
        Already have an account? <Link to="/login">Log In</Link>
      </p>
    </div>
  );
}

export default RegisterPage;

import React, { useEffect, useState } from "react";
import { TOKEN_KEY } from "../../config";
import { getOfficers, createOfficer } from "./adminApi";
import "./admin.css";

/**
 * Panel for managing officer accounts.
 * Shows a paged list of officers and a form to create a new one.
 */
function OfficersPanel() {
  // List of officers on the current page
  const [officers, setOfficers] = useState([]);
  // Current page number
  const [page, setPage] = useState(1);
  // Total number of pages
  const [totalPages, setTotalPages] = useState(1);
  // Form input states for creating a new officer
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  // Validation and API error messages
  const [fieldError, setFieldError] = useState("");
  const [apiError, setApiError] = useState("");
  // Loading indicator
  const [loading, setLoading] = useState(false);

  const token = localStorage.getItem(TOKEN_KEY);

  /** Load the officers list for the current page. */
  async function loadOfficers() {
    setLoading(true);
    setApiError("");
    try {
      const data = await getOfficers(token, page);
      setOfficers(data.items);
      setTotalPages(data.pages);
    } catch (err) {
      setApiError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // Reload the list whenever the page changes
  useEffect(() => {
    loadOfficers();
  }, [page]);

  /** Validate and submit the create-officer form. */
  async function handleCreate(event) {
    event.preventDefault();
    setFieldError("");
    setApiError("");

    // Require a password of at least 6 characters
    if (password.length < 6) {
      setFieldError("Password must be at least 6 characters");
      return;
    }

    try {
      await createOfficer(token, name.trim(), email.trim(), password);
      // Reset the form and refresh the list on success
      setName("");
      setEmail("");
      setPassword("");
      loadOfficers();
    } catch (err) {
      setApiError(err.message);
    }
  }

  return (
    <section className="admin-panel">
      <h2>Officers</h2>

      {apiError && <p className="admin-error">{apiError}</p>}

      {loading ? (
        <p>Loading...</p>
      ) : officers.length === 0 ? (
        <p>No officers yet</p>
      ) : (
        <ul className="admin-list">
          {officers.map((officer) => (
            <li key={officer.id} className="admin-list-item">
              <span>{officer.name}</span>
              <span className="admin-email">{officer.email}</span>
            </li>
          ))}
        </ul>
      )}

      {/* Previous / Next pagination controls */}
      <div className="admin-pagination">
        <button
          disabled={page <= 1}
          onClick={() => setPage((p) => p - 1)}
        >
          Previous
        </button>
        <span>Page {page} of {totalPages}</span>
        <button
          disabled={page >= totalPages}
          onClick={() => setPage((p) => p + 1)}
        >
          Next
        </button>
      </div>

      {/* Form to create a new officer account */}
      <form className="admin-form" onSubmit={handleCreate}>
        <h3>Create Officer</h3>
        {fieldError && <p className="admin-error">{fieldError}</p>}
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Full name"
        />
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email address"
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password (min 6 characters)"
        />
        <button type="submit">Create Officer</button>
      </form>
    </section>
  );
}

export default OfficersPanel;

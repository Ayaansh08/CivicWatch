import React, { useEffect, useState } from "react";
import { TOKEN_KEY } from "../../config";
import {
  getDepartments,
  createDepartment,
  renameDepartment,
  deleteDepartment,
} from "./adminApi";
import "./admin.css";

/**
 * Panel for managing city departments.
 * Displays a paged list with Previous/Next buttons, an add form, rename, and delete.
 */
function DepartmentsPanel() {
  // List of departments on the current page
  const [departments, setDepartments] = useState([]);
  // Current page number
  const [page, setPage] = useState(1);
  // Total number of pages from the API
  const [totalPages, setTotalPages] = useState(1);
  // The name typed into the new-department input
  const [newName, setNewName] = useState("");
  // Any error message from the API
  const [error, setError] = useState("");
  // Loading indicator while fetch is in flight
  const [loading, setLoading] = useState(false);

  // Read the auth token once from localStorage
  const token = localStorage.getItem(TOKEN_KEY);

  /** Load the departments for the current page from the API. */
  async function loadDepartments() {
    setLoading(true);
    setError("");
    try {
      const data = await getDepartments(token, page);
      setDepartments(data.items);
      setTotalPages(data.pages);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // Reload the list whenever the page number changes
  useEffect(() => {
    loadDepartments();
  }, [page]);

  /** Submit the new-department form. */
  async function handleAdd(event) {
    event.preventDefault();
    setError("");
    try {
      await createDepartment(token, newName.trim());
      // Clear the input and refresh the list
      setNewName("");
      loadDepartments();
    } catch (err) {
      setError(err.message);
    }
  }

  /** Ask the user to confirm and then rename the department. */
  async function handleRename(dept) {
    // Prompt for the new name inline
    const updated = window.prompt("Enter a new name:", dept.name);
    if (!updated || updated.trim() === dept.name) {
      return;
    }
    setError("");
    try {
      await renameDepartment(token, dept.id, updated.trim());
      loadDepartments();
    } catch (err) {
      setError(err.message);
    }
  }

  /** Ask the user to confirm and then delete the department. */
  async function handleDelete(dept) {
    // Confirm before deleting so the user does not delete by accident
    if (!window.confirm(`Delete "${dept.name}"?`)) {
      return;
    }
    setError("");
    try {
      await deleteDepartment(token, dept.id);
      loadDepartments();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="admin-panel">
      <h2>Departments</h2>

      {error && <p className="admin-error">{error}</p>}

      {loading ? (
        <p>Loading...</p>
      ) : departments.length === 0 ? (
        <p>No departments yet</p>
      ) : (
        <ul className="admin-list">
          {departments.map((dept) => (
            <li key={dept.id} className="admin-list-item">
              <span>{dept.name}</span>
              <button onClick={() => handleRename(dept)}>Rename</button>
              <button onClick={() => handleDelete(dept)}>Delete</button>
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

      {/* Form to add a new department */}
      <form className="admin-form" onSubmit={handleAdd}>
        <h3>Add Department</h3>
        <input
          type="text"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          placeholder="Department name"
        />
        <button type="submit">Add</button>
      </form>
    </section>
  );
}

export default DepartmentsPanel;

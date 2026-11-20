import { API_URL } from "../../config";

/**
 * Send an authenticated request to the /admin API endpoints.
 * Throws an Error with the backend detail message on failure.
 */
async function authFetch(path, token, options = {}) {
  // Attach the Bearer token to every admin API call
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(options.headers || {}),
    },
  });

  // Parse the JSON body
  const data = await response.json();

  // Throw the API error on failure
  if (!response.ok) {
    throw new Error(data.detail || "Request failed");
  }

  return data;
}

/**
 * Fetch a paginated list of departments.
 * Returns { items, total, page, size, pages }.
 */
export async function getDepartments(token, page = 1) {
  return authFetch(`/admin/departments?page=${page}`, token);
}

/**
 * Create a new department with the given name.
 * Returns the created department object.
 */
export async function createDepartment(token, name) {
  return authFetch("/admin/departments", token, {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

/**
 * Rename an existing department by its id.
 * Returns the updated department object.
 */
export async function renameDepartment(token, id, name) {
  return authFetch(`/admin/departments/${id}`, token, {
    method: "PUT",
    body: JSON.stringify({ name }),
  });
}

/**
 * Delete a department by its id.
 * Returns null (204 No Content on success).
 */
export async function deleteDepartment(token, id) {
  const response = await fetch(`${API_URL}/admin/departments/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  // A 204 has no body, so only parse JSON if there is content
  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.detail || "Delete failed");
  }
  return null;
}

/**
 * Fetch a paginated list of officers.
 * Returns { items, total, page, size, pages }.
 */
export async function getOfficers(token, page = 1) {
  return authFetch(`/admin/officers?page=${page}`, token);
}

/**
 * Create a new officer account with the given name, email, and password.
 * Returns the created officer user object.
 */
export async function createOfficer(token, name, email, password) {
  return authFetch("/admin/officers", token, {
    method: "POST",
    body: JSON.stringify({ name, email, password }),
  });
}

/** Authority module API calls — all fetch requests for the dashboard. */
import { API_URL, TOKEN_KEY } from "../../config";

/** Allowed next statuses for each current status — mirrors workflow.py. */
export const ALLOWED_NEXT = {
  Submitted: ["Under Review", "Rejected"],
  "Under Review": ["Assigned", "Rejected"],
  Assigned: ["In Progress"],
  "In Progress": ["Resolved"],
  Resolved: [],
  Rejected: [],
};

/** Build the Authorization header from localStorage. */
function authHeaders() {
  const token = localStorage.getItem(TOKEN_KEY);
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/** Unified request helper for authority API calls. */
async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { ...authHeaders(), ...(options.headers || {}) },
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || "Request failed");
  }
  return response.json();
}

/** Fetch complaints with optional status and category filters. */
export async function fetchComplaints(status = "", categoryId = "", sort = "newest") {
  const params = new URLSearchParams();
  if (status) params.set("status", status);
  if (categoryId) params.set("category_id", categoryId);
  if (sort) params.set("sort", sort);
  return request(`/authority/complaints?${params}`);
}

/** Fetch all departments. */
export async function fetchDepartments() {
  return request("/authority/departments");
}

/** Move a complaint to Under Review. */
export async function reviewComplaint(id) {
  return request(`/authority/complaints/${id}/review`, { method: "POST" });
}

/** Assign a complaint to a department with a priority. */
export async function assignComplaint(id, departmentId, priority) {
  return request(`/authority/complaints/${id}/assign`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ department_id: departmentId, priority }),
  });
}

/** Update the status of a complaint. */
export async function updateStatus(id, status, note = "") {
  return request(`/authority/complaints/${id}/status`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status, note }),
  });
}

/** Trigger auto-escalation of overdue complaints. */
export async function escalateOverdue() {
  return request("/authority/escalate", { method: "POST" });
}

import { API_URL, TOKEN_KEY } from "../../config";

const getAuthHeaders = () => {
  const token = localStorage.getItem(TOKEN_KEY);

  return token ? { Authorization: `Bearer ${token}` } : {};
};

/** Unified request helper for citizen API calls. */
async function request(path, options = {}, defaultError = "Request failed") {
  const headers = {
    ...getAuthHeaders(),
    ...(options.headers || {}),
  };

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || defaultError);
  }

  return response.json();
}

/** Fetch available complaint categories. */
export async function fetchCategories() {
  return request("/complaints/categories", {}, "Unable to load categories");
}

/** Submit a new complaint. */
export async function createComplaint(complaintData) {
  return request(
    "/complaints",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(complaintData),
    },
    "Unable to submit complaint"
  );
}

/** Upload a photo for a complaint. */
export async function uploadPhoto(complaintId, file) {
  const formData = new FormData();
  formData.append("file", file);

  return request(
    `/complaints/${complaintId}/photo`,
    {
      method: "POST",
      body: formData,
    },
    "Unable to upload photo"
  );
}

/** Fetch all complaints filed by the current user. */
export async function fetchMyComplaints(filters = {}) {
  const params = new URLSearchParams();
  if (filters.status) params.append("status", filters.status);
  if (filters.category_id) params.append("category_id", filters.category_id);

  const queryString = params.toString() ? `?${params.toString()}` : "";
  return request(`/complaints/mine${queryString}`, {}, "Unable to load complaints");
}

/** Fetch status history for a complaint. */
export async function fetchHistory(complaintId) {
  return request(`/complaints/${complaintId}/history`, {}, "Unable to load history");
}

/** Submit feedback rating and comment. */
export async function submitFeedback(complaintId, rating, comment = null) {
  return request(
    `/complaints/${complaintId}/feedback`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rating, comment }),
    },
    "Unable to submit feedback"
  );
}

/** Reopen a resolved complaint. */
export async function reopenComplaint(complaintId, reason) {
  return request(
    `/complaints/${complaintId}/reopen`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reason }),
    },
    "Unable to reopen complaint"
  );
}

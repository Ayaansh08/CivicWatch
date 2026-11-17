import { API_URL, TOKEN_KEY } from "../../config";

const getAuthHeaders = () => {
  const token = localStorage.getItem(TOKEN_KEY);

  return token ? { Authorization: `Bearer ${token}` } : {};
};

/** Fetch available complaint categories. */
export async function fetchCategories() {
  const response = await fetch(`${API_URL}/complaints/categories`, {
    headers: {
      ...getAuthHeaders(),
    },
  });

  if (!response.ok) {
    throw new Error("Unable to load categories");
  }

  return response.json();
}

/** Submit a new complaint. */
export async function createComplaint(complaintData) {
  const response = await fetch(`${API_URL}/complaints`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify(complaintData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Unable to submit complaint");
  }

  return response.json();
}

/** Upload a photo for a complaint. */
export async function uploadPhoto(complaintId, file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/complaints/${complaintId}/photo`, {
    method: "POST",
    headers: {
      ...getAuthHeaders(),
    },
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Unable to upload photo");
  }

  return response.json();
}

/** Fetch all complaints filed by the current user. */
export async function fetchMyComplaints(filters = {}) {
  const params = new URLSearchParams();
  if (filters.status) params.append("status", filters.status);
  if (filters.category_id) params.append("category_id", filters.category_id);

  const queryString = params.toString() ? `?${params.toString()}` : "";
  const response = await fetch(`${API_URL}/complaints/mine${queryString}`, {
    headers: {
      ...getAuthHeaders(),
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Unable to load complaints");
  }

  return response.json();
}

/** Fetch status history for a complaint. */
export async function fetchHistory(complaintId) {
  const response = await fetch(`${API_URL}/complaints/${complaintId}/history`, {
    headers: {
      ...getAuthHeaders(),
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Unable to load history");
  }

  return response.json();
}

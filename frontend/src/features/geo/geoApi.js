/**
 * API helper functions for geospatial complaints data.
 * Communicates with the FastAPI backend /geo endpoints using JWT Bearer authentication.
 */
import { API_URL, TOKEN_KEY } from "../../config";

/**
 * Fetch complaints within a given bounding box with optional filters.
 *
 * @param {Object} box Bounding box containing min_lat, min_lon, max_lat, max_lon.
 * @param {Object} [filters={}] Optional filters containing category_id and/or status.
 * @returns {Promise<Array>} List of complaint objects.
 * @throws {Error} If the HTTP response is not OK.
 */
export async function fetchComplaintsInBox(box, filters = {}) {
  // Retrieve token from local storage
  const token = localStorage.getItem(TOKEN_KEY);

  // Construct query parameters string for the bounding box
  const params = new URLSearchParams({
    min_lat: box.min_lat,
    min_lon: box.min_lon,
    max_lat: box.max_lat,
    max_lon: box.max_lon,
  });

  // Append category filter if present
  if (filters && filters.category_id) {
    params.append("category_id", filters.category_id);
  }

  // Append status filter if present
  if (filters && filters.status) {
    params.append("status", filters.status);
  }

  // Call the backend bounding box endpoint with authorization header
  const response = await fetch(`${API_URL}/geo/complaints/bbox?${params.toString()}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token || ""}`,
    },
  });

  // Throw descriptive error if request failed
  if (!response.ok) {
    throw new Error(`Failed to fetch complaints in bounding box: ${response.status}`);
  }

  // Parse and return JSON complaint records
  return await response.json();
}

/**
 * Fetch density heatmap cells within a bounding box with optional filters.
 *
 * @param {Object} box Bounding box containing min_lat, min_lon, max_lat, max_lon.
 * @param {Object} [filters={}] Optional filters containing category_id and/or status.
 * @returns {Promise<Array>} List of cell objects { lat, lon, count }.
 * @throws {Error} If the HTTP response is not OK.
 */
export async function fetchHeatmap(box, filters = {}) {
  // Retrieve token from local storage
  const token = localStorage.getItem(TOKEN_KEY);

  // Construct query parameters string for heatmap bounding box
  const params = new URLSearchParams({
    min_lat: box.min_lat,
    min_lon: box.min_lon,
    max_lat: box.max_lat,
    max_lon: box.max_lon,
  });

  // Append category filter if present
  if (filters && filters.category_id) {
    params.append("category_id", filters.category_id);
  }

  // Append status filter if present
  if (filters && filters.status) {
    params.append("status", filters.status);
  }

  // Call the backend heatmap endpoint with authorization header
  const response = await fetch(`${API_URL}/geo/heatmap?${params.toString()}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token || ""}`,
    },
  });

  // Throw descriptive error if request failed
  if (!response.ok) {
    throw new Error(`Failed to fetch heatmap data: ${response.status}`);
  }

  // Parse and return JSON heatmap cells
  return await response.json();
}

/**
 * Fetch repeat-issue spatial hotspots with optional filters.
 *
 * @param {number} [cellSize=0.01] Cell size in degrees.
 * @param {number} [minCount=3] Minimum complaint threshold.
 * @param {Object} [filters={}] Optional filters containing category_id and/or status.
 * @returns {Promise<Array>} List of hotspot objects { count, center_lat, center_lon, category }.
 * @throws {Error} If the HTTP response is not OK.
 */
export async function fetchHotspots(cellSize = 0.01, minCount = 3, filters = {}) {
  // Retrieve token from local storage
  const token = localStorage.getItem(TOKEN_KEY);

  // Construct query parameters string
  const params = new URLSearchParams({
    cell_size: cellSize,
    min_count: minCount,
  });

  // Append category filter if present
  if (filters && filters.category_id) {
    params.append("category_id", filters.category_id);
  }

  // Append status filter if present
  if (filters && filters.status) {
    params.append("status", filters.status);
  }

  // Call backend hotspots endpoint with authorization header
  const response = await fetch(`${API_URL}/geo/hotspots?${params.toString()}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token || ""}`,
    },
  });

  // Throw descriptive error if request failed
  if (!response.ok) {
    throw new Error(`Failed to fetch hotspots: ${response.status}`);
  }

  // Parse and return JSON hotspot records
  return await response.json();
}

/**
 * Fetch overall geospatial analytics summary report.
 *
 * @returns {Promise<Object>} Report summary containing totals, breakdowns, and averages.
 * @throws {Error} If the HTTP response is not OK.
 */
export async function fetchReport() {
  // Retrieve token from local storage
  const token = localStorage.getItem(TOKEN_KEY);

  // Call backend reports summary endpoint with authorization header
  const response = await fetch(`${API_URL}/geo/reports/summary`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token || ""}`,
    },
  });

  // Throw descriptive error if request failed
  if (!response.ok) {
    throw new Error(`Failed to fetch reports summary: ${response.status}`);
  }

  // Parse and return JSON report object
  return await response.json();
}

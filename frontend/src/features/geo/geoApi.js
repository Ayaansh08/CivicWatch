/**
 * API helper functions for geospatial complaints data.
 * Communicates with the FastAPI backend /geo endpoints using JWT Bearer authentication.
 */
import { API_URL, TOKEN_KEY } from "../../config";

/**
 * Fetch complaints within a given bounding box.
 *
 * @param {Object} box Bounding box containing min_lat, min_lon, max_lat, max_lon.
 * @returns {Promise<Array>} List of complaint objects.
 * @throws {Error} If the HTTP response is not OK.
 */
export async function fetchComplaintsInBox(box) {
  // Retrieve token from local storage
  const token = localStorage.getItem(TOKEN_KEY);

  // Construct query parameters string for the bounding box
  const params = new URLSearchParams({
    min_lat: box.min_lat,
    min_lon: box.min_lon,
    max_lat: box.max_lat,
    max_lon: box.max_lon,
  });

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

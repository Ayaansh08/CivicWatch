/**
 * Helper utility functions for map rendering and data transformation.
 */

/**
 * Escape HTML special characters to prevent XSS injection attacks.
 *
 * @param {string} text Raw string possibly containing special characters.
 * @returns {string} Escaped HTML string safe for innerHTML insertion.
 */
export function escapeHtml(text) {
  // Return empty string if input is null or undefined
  if (text == null) {
    return "";
  }
  // Convert input to string
  const str = String(text);
  // Replace characters &, <, >, ", and ' with HTML entities
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/**
 * Build safe HTML content for a complaint map marker popup.
 *
 * @param {Object} complaint Complaint object with title, category_name, status, priority.
 * @returns {string} Sanitized HTML string for popup display.
 */
export function buildPopupHtml(complaint) {
  // Escape all text fields from user input
  const title = escapeHtml(complaint.title || "");
  const category = escapeHtml(complaint.category_name || "");
  const status = escapeHtml(complaint.status || "");
  const priority = escapeHtml(complaint.priority || "");

  // Build and return popup HTML layout
  return `<div>` +
    `<h4 style="margin: 0 0 6px 0; font-size: 14px;">${title}</h4>` +
    `<p style="margin: 2px 0; font-size: 12px;"><strong>Category:</strong> ${category}</p>` +
    `<p style="margin: 2px 0; font-size: 12px;"><strong>Status:</strong> ${status}</p>` +
    `<p style="margin: 2px 0; font-size: 12px;"><strong>Priority:</strong> ${priority}</p>` +
    `</div>`;
}

/**
 * Convert a list of point dictionaries into Leaflet heat layer coordinates.
 *
 * @param {Array<Object>} points List of objects with lat/latitude, lon/longitude, and count/intensity.
 * @returns {Array<Array<number>>} Array of [lat, lon, intensity] tuples.
 */
export function toHeatPoints(points) {
  // Return empty array if input points is empty or falsy
  if (!points || !Array.isArray(points)) {
    return [];
  }

  // Transform each point into [lat, lon, intensity]
  return points.map((p) => {
    // Determine latitude
    const lat = p.lat !== undefined ? p.lat : p.latitude;
    // Determine longitude
    const lon = p.lon !== undefined ? p.lon : p.longitude;
    // Determine intensity / count (default 1)
    const intensity = p.count !== undefined ? p.count : (p.intensity !== undefined ? p.intensity : 1);
    return [lat, lon, intensity];
  });
}

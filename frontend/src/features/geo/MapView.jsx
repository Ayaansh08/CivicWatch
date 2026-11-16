/**
 * MapView component: renders an interactive Leaflet map with real complaints
 * fetched from the backend API.
 */
import React, { useState, useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Marker asset imports for Vite compatibility
import iconUrl from "leaflet/dist/images/marker-icon.png";
import iconRetinaUrl from "leaflet/dist/images/marker-icon-2x.png";
import shadowUrl from "leaflet/dist/images/marker-shadow.png";

// Geo API helper to fetch complaints by bounding box
import { fetchComplaintsInBox } from "./geoApi";

// NOTE: mockComplaints.js is kept in this folder only for offline demos and development stubs.

// Fix default marker icon resolution in Vite asset bundling
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl,
  iconRetinaUrl,
  shadowUrl,
});

// Fixed starting bounding box covering the Delhi NCR region (Sprint 3 filters will dynamically adjust this)
const DELHI_NCR_BBOX = {
  min_lat: 28.2,
  min_lon: 76.8,
  max_lat: 29.0,
  max_lon: 77.8,
};

/**
 * Interactive map component displaying complaint locations and details.
 */
function MapView() {
  // Component state for fetched complaints, loading status, and error messages
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Noida center coordinates (lat: 28.62, lon: 77.36)
  const defaultCenter = [28.62, 77.36];
  const defaultZoom = 13;

  // Fetch real complaints from backend on mount
  useEffect(() => {
    let isMounted = true;

    // Load complaints using bounding box query
    async function loadComplaints() {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchComplaintsInBox(DELHI_NCR_BBOX);
        if (isMounted) {
          setComplaints(data);
          setLoading(false);
        }
      } catch {
        if (isMounted) {
          setError("Could not load complaints");
          setLoading(false);
        }
      }
    }

    loadComplaints();

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="map-view-container" style={{ width: "100%", margin: "0 auto" }}>
      {/* Status banner messages */}
      {loading && <p className="status-message">Loading complaints...</p>}
      {error && <p className="error-message">{error}</p>}
      {!loading && !error && complaints.length === 0 && (
        <p className="empty-message">No complaints found in this area</p>
      )}
      {!loading && !error && complaints.length > 0 && (
        <p className="count-message">{complaints.length} complaints</p>
      )}

      {/* Leaflet map container */}
      <MapContainer
        center={defaultCenter}
        zoom={defaultZoom}
        scrollWheelZoom={true}
        style={{ height: "500px", width: "100%", borderRadius: "8px" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Render a marker and popup for each complaint */}
        {complaints.map((complaint) => (
          <Marker
            key={complaint.id}
            position={[complaint.latitude, complaint.longitude]}
          >
            <Popup>
              <div>
                <h4 style={{ margin: "0 0 6px 0", fontSize: "14px" }}>
                  {complaint.title}
                </h4>
                <p style={{ margin: "2px 0", fontSize: "12px" }}>
                  <strong>Category:</strong> {complaint.category_name}
                </p>
                <p style={{ margin: "2px 0", fontSize: "12px" }}>
                  <strong>Status:</strong> {complaint.status}
                </p>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}

export default MapView;

/**
 * MapView component: renders an interactive Leaflet map with real complaints
 * fetched from the backend API, clustered using MarkerClusterLayer, with filters.
 */
import React, { useState, useEffect } from "react";
import { MapContainer, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";

// Geo API helper to fetch complaints by bounding box
import { fetchComplaintsInBox } from "./geoApi";
import MarkerClusterLayer from "./MarkerClusterLayer";
import MapFilters from "./MapFilters";

// Fixed starting bounding box covering the Delhi NCR region
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
  // Component state for fetched complaints, loading status, error messages, and filters
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({ category_id: "", status: "" });

  // Noida center coordinates (lat: 28.62, lon: 77.36)
  const defaultCenter = [28.62, 77.36];
  const defaultZoom = 13;

  // Determine whether any filter is currently applied
  const hasActiveFilters = Boolean(filters.category_id || filters.status);

  // Fetch complaints from backend whenever filters change
  useEffect(() => {
    let isMounted = true;

    // Load complaints using bounding box query with filters
    async function loadComplaints() {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchComplaintsInBox(DELHI_NCR_BBOX, filters);
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
  }, [filters]);

  return (
    <div className="map-view-container" style={{ width: "100%", margin: "0 auto" }}>
      {/* Filter controls toolbar */}
      <MapFilters filters={filters} onFilterChange={setFilters} />

      {/* Status banner messages */}
      {loading && <p className="status-message">Loading complaints...</p>}
      {error && <p className="error-message">{error}</p>}
      {!loading && !error && complaints.length === 0 && (
        <p className="empty-message">
          {hasActiveFilters ? "No complaints match these filters" : "No complaints found in this area"}
        </p>
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

        {/* Render clustered complaint markers */}
        <MarkerClusterLayer complaints={complaints} />
      </MapContainer>
    </div>
  );
}

export default MapView;

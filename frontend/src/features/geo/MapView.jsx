/**
 * MapView component: renders an interactive Leaflet map with real complaints
 * fetched from the backend API, clustered using MarkerClusterLayer, with filters
 * and a toggle between Markers and Heatmap views.
 */
import React, { useState, useEffect } from "react";
import { MapContainer, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "./geo.css";

// Geo API helpers
import { fetchComplaintsInBox, fetchHeatmap } from "./geoApi";
import MarkerClusterLayer from "./MarkerClusterLayer";
import HeatLayer from "./HeatLayer";
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
  // Component state for complaints, heatmap density cells, loading, errors, filters, and view mode
  const [complaints, setComplaints] = useState([]);
  const [heatmapPoints, setHeatmapPoints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({ category_id: "", status: "" });
  const [viewMode, setViewMode] = useState("markers"); // "markers" or "heatmap"

  // Noida center coordinates (lat: 28.62, lon: 77.36)
  const defaultCenter = [28.62, 77.36];
  const defaultZoom = 13;

  // Determine whether any filter is currently applied
  const hasActiveFilters = Boolean(filters.category_id || filters.status);

  // Fetch complaints or heatmap data whenever filters or viewMode changes
  useEffect(() => {
    let isMounted = true;

    async function loadData() {
      try {
        setLoading(true);
        setError(null);

        if (viewMode === "markers") {
          // Fetch complaint point markers
          const data = await fetchComplaintsInBox(DELHI_NCR_BBOX, filters);
          if (isMounted) {
            setComplaints(data);
            setLoading(false);
          }
        } else {
          // Fetch heatmap density cells
          const data = await fetchHeatmap(DELHI_NCR_BBOX, filters);
          if (isMounted) {
            setHeatmapPoints(data);
            setLoading(false);
          }
        }
      } catch {
        if (isMounted) {
          setError(
            viewMode === "markers"
              ? "Could not load complaints"
              : "Could not load heatmap data"
          );
          setLoading(false);
        }
      }
    }

    loadData();

    return () => {
      isMounted = false;
    };
  }, [filters, viewMode]);

  return (
    <div className="map-view-container">
      {/* Top toolbar with filters and view toggle */}
      <div className="map-toolbar">
        <MapFilters filters={filters} onFilterChange={setFilters} />

        <div className="map-view-toggle">
          <button
            type="button"
            className={viewMode === "markers" ? "active" : ""}
            onClick={() => setViewMode("markers")}
          >
            Markers
          </button>
          <button
            type="button"
            className={viewMode === "heatmap" ? "active" : ""}
            onClick={() => setViewMode("heatmap")}
          >
            Heatmap
          </button>
        </div>
      </div>

      {/* Status banner messages */}
      {loading && <p className="status-message">Loading complaints...</p>}
      {error && <p className="error-message">{error}</p>}
      {!loading && !error && viewMode === "markers" && complaints.length === 0 && (
        <p className="empty-message">
          {hasActiveFilters ? "No complaints match these filters" : "No complaints found in this area"}
        </p>
      )}
      {!loading && !error && viewMode === "markers" && complaints.length > 0 && (
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

        {/* Render either clustered markers or heatmap layer */}
        {viewMode === "markers" ? (
          <MarkerClusterLayer complaints={complaints} />
        ) : (
          <HeatLayer points={heatmapPoints} />
        )}
      </MapContainer>
    </div>
  );
}

export default MapView;

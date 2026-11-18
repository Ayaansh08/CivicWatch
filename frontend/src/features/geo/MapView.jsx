/**
 * MapView component: renders an interactive Leaflet map with real complaints
 * fetched from the backend API, clustered using MarkerClusterLayer, with filters,
 * a toggle between Markers and Heatmap views, and optional Hotspots layer overlay.
 */
import React, { useState, useEffect } from "react";
import { MapContainer, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "./geo.css";

// Geo API helpers
import { fetchComplaintsInBox, fetchHeatmap, fetchHotspots } from "./geoApi";
import MarkerClusterLayer from "./MarkerClusterLayer";
import HeatLayer from "./HeatLayer";
import HotspotLayer from "./HotspotLayer";
import MapFilters from "./MapFilters";

// Fixed starting bounding box covering the Delhi NCR region
const DELHI_NCR_BBOX = {
  min_lat: 28.2,
  min_lon: 76.8,
  max_lat: 29.0,
  max_lon: 77.8,
};

/**
 * Interactive map component displaying complaint locations, clusters, heatmaps, and hotspots.
 */
function MapView() {
  // Component state for complaints, heatmap cells, hotspots, loading, errors, filters, and layer toggles
  const [complaints, setComplaints] = useState([]);
  const [heatmapPoints, setHeatmapPoints] = useState([]);
  const [hotspots, setHotspots] = useState([]);
  const [showHotspots, setShowHotspots] = useState(false);
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

  // Fetch hotspots when hotspots overlay is enabled or filters change
  useEffect(() => {
    let isMounted = true;

    if (!showHotspots) {
      return;
    }

    async function loadHotspots() {
      try {
        const data = await fetchHotspots(0.01, 3, filters);
        if (isMounted) {
          setHotspots(data);
        }
      } catch {
        // Log or keep previous hotspots on failure without breaking primary map
      }
    }

    loadHotspots();

    return () => {
      isMounted = false;
    };
  }, [showHotspots, filters]);

  return (
    <div className="map-view-container">
      {/* Top toolbar with filters, view toggle, and hotspots checkbox */}
      <div className="map-toolbar">
        <MapFilters filters={filters} onFilterChange={setFilters} />

        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          {/* Hotspots layer toggle checkbox */}
          <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer", fontSize: "14px" }}>
            <input
              type="checkbox"
              aria-label="Hotspots"
              checked={showHotspots}
              onChange={(e) => setShowHotspots(e.target.checked)}
            />
            Hotspots
          </label>

          {/* Markers / Heatmap mode switcher */}
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

        {/* Primary map layer: either clustered markers or heatmap */}
        {viewMode === "markers" ? (
          <MarkerClusterLayer complaints={complaints} />
        ) : (
          <HeatLayer points={heatmapPoints} />
        )}

        {/* Optional hotspot circles overlay */}
        {showHotspots && <HotspotLayer hotspots={hotspots} cell_size={0.01} />}
      </MapContainer>
    </div>
  );
}

export default MapView;

import React, { useEffect } from "react";
import { MapContainer, TileLayer, Marker, useMapEvents, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

import iconUrl from "leaflet/dist/images/marker-icon.png";
import iconRetinaUrl from "leaflet/dist/images/marker-icon-2x.png";
import shadowUrl from "leaflet/dist/images/marker-shadow.png";
import { useGeolocation } from "./useGeolocation";

// Fix default marker icon inside LocationPicker
const defaultIcon = L.icon({
  iconUrl,
  iconRetinaUrl,
  shadowUrl,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  tooltipAnchor: [16, -28],
  shadowSize: [41, 41],
});
L.Marker.prototype.options.icon = defaultIcon;

// Map click handler component
function ClickHandler({ onLocationSelect }) {
  useMapEvents({
    click(e) {
      onLocationSelect(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

// Center watcher to pan map when coordinates change
function RecenterMap({ lat, lng }) {
  const map = useMap();
  useEffect(() => {
    if (lat && lng) {
      map.setView([lat, lng], map.getZoom());
    }
  }, [lat, lng, map]);
  return null;
}

/**
 * Leaflet map picker allowing user to select a location or use GPS.
 */
export default function LocationPicker({ latitude, longitude, onLocationChange }) {
  const defaultCenter = [28.62, 77.36]; // Noida default centre
  const { coordinates: geoCoords, error: geoError, loading: geoLoading, getLocation } = useGeolocation();

  // Update parent when GPS retrieves coordinates
  useEffect(() => {
    if (geoCoords) {
      onLocationChange(geoCoords.latitude, geoCoords.longitude);
    }
  }, [geoCoords, onLocationChange]);

  const currentLat = latitude ? Number(latitude) : null;
  const currentLng = longitude ? Number(longitude) : null;
  const center = currentLat && currentLng ? [currentLat, currentLng] : defaultCenter;

  return (
    <div className="location-picker">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
        <label>Pick Location on Map</label>
        <button
          type="button"
          onClick={getLocation}
          disabled={geoLoading}
          style={{ padding: "4px 8px", fontSize: "14px" }}
        >
          {geoLoading ? "Locating..." : "Use my location"}
        </button>
      </div>
      {geoError && <p role="alert" style={{ color: "#c62828" }}>{geoError}</p>}
      <div style={{ height: "250px", width: "100%", borderRadius: "4px", overflow: "hidden", marginBottom: "8px" }}>
        <MapContainer center={center} zoom={13} style={{ height: "100%", width: "100%" }}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <ClickHandler onLocationSelect={onLocationChange} />
          {currentLat && currentLng && <RecenterMap lat={currentLat} lng={currentLng} />}
          {currentLat && currentLng && (
            <Marker position={[currentLat, currentLng]} icon={defaultIcon} />
          )}
        </MapContainer>
      </div>
      <div style={{ fontSize: "14px", color: "#666" }}>
        {currentLat && currentLng ? (
          <span>Selected coordinates: {currentLat.toFixed(4)}, {currentLng.toFixed(4)}</span>
        ) : (
          <span>Click on the map to drop a pin</span>
        )}
      </div>
    </div>
  );
}

// MapView component: renders an interactive Leaflet map with complaint markers
import React from 'react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
// Import Leaflet CSS styles required for rendering map tiles and controls
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
// Import marker assets from leaflet package for Vite bundler compatibility
import iconUrl from 'leaflet/dist/images/marker-icon.png'
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png'
import shadowUrl from 'leaflet/dist/images/marker-shadow.png'
// Import mock complaint records
import { mockComplaints } from './mockComplaints'

// Fix the known Leaflet default marker icon issue under Vite asset bundling
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconUrl,
  iconRetinaUrl,
  shadowUrl,
})

/**
 * MapView renders an OpenStreetMap view centered on Noida with complaint markers.
 * Each marker has a popup showing complaint title, category, and status.
 */
function MapView() {
  // Center coordinates for Noida (lat: 28.62, lon: 77.36)
  const defaultCenter = [28.62, 77.36]
  // Default zoom level suitable for city/neighborhood view
  const defaultZoom = 13

  return (
    <div className="map-view-container" style={{ width: '100%', margin: '0 auto' }}>
      {/* MapContainer initializes the Leaflet map with a 500px fixed height */}
      <MapContainer
        center={defaultCenter}
        zoom={defaultZoom}
        scrollWheelZoom={true}
        style={{ height: '500px', width: '100%', borderRadius: '8px' }}
      >
        {/* TileLayer provides OpenStreetMap tile images */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Render a Marker with a Popup for each mock complaint */}
        {mockComplaints.map((complaint) => (
          <Marker
            key={complaint.id}
            position={[complaint.lat, complaint.lon]}
          >
            <Popup>
              <div>
                <h4 style={{ margin: '0 0 6px 0', fontSize: '14px' }}>{complaint.title}</h4>
                <p style={{ margin: '2px 0', fontSize: '12px' }}>
                  <strong>Category:</strong> {complaint.category}
                </p>
                <p style={{ margin: '2px 0', fontSize: '12px' }}>
                  <strong>Status:</strong> {complaint.status}
                </p>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  )
}

export default MapView

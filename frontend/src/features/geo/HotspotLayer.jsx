/**
 * HotspotLayer component: renders repeat-issue zones as translucent red circles using react-leaflet.
 */
import React from "react";
import { Circle, Popup } from "react-leaflet";

/**
 * Circle layer visualizing repeat-issue zones with complaint count and dominant category.
 *
 * @param {Object} props Component properties containing hotspots array and cell_size.
 */
function HotspotLayer({ hotspots, cell_size = 0.01 }) {
  // Convert cell_size degrees to approximate circle radius in meters (~111 km per degree)
  const radiusMeters = Math.max((cell_size * 111000) / 2, 50);

  return (
    <>
      {(hotspots || []).map((hotspot, index) => (
        <Circle
          key={`hotspot-${index}`}
          center={[hotspot.center_lat, hotspot.center_lon]}
          radius={radiusMeters}
          pathOptions={{
            color: "#d32f2f",
            fillColor: "#f44336",
            fillOpacity: 0.35,
            weight: 2,
          }}
        >
          <Popup>
            <div>
              <p style={{ margin: "2px 0", fontWeight: "bold" }}>
                Hotspot: {hotspot.count} complaints, mostly {hotspot.category}
              </p>
              <p style={{ margin: "2px 0", fontSize: "12px", color: "#666" }}>
                Centre: {hotspot.center_lat}, {hotspot.center_lon}
              </p>
            </div>
          </Popup>
        </Circle>
      ))}
    </>
  );
}

export default HotspotLayer;

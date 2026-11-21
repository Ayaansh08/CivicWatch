/**
 * HeatLayer component: renders a Leaflet heatmap layer using leaflet.heat.
 */
import { useEffect } from "react";
import { useMap } from "react-leaflet";
import L from "./leafletSetup";
import * as HeatModule from "leaflet.heat";
import { toHeatPoints } from "./mapHelpers";

/**
 * Safely create a Leaflet heat layer across different module formats.
 */
function createHeatLayer(points, options) {
  if (typeof L.heatLayer === "function") {
    return L.heatLayer(points, options);
  }
  if (typeof window !== "undefined" && typeof window.L?.heatLayer === "function") {
    return window.L.heatLayer(points, options);
  }
  if (HeatModule && typeof HeatModule.HeatLayer === "function") {
    return new HeatModule.HeatLayer(points, options);
  }
  return null;
}

/**
 * Leaflet heat layer overlay for density visualization.
 *
 * @param {Object} props Component properties containing points array.
 */
function HeatLayer({ points }) {
  // Access parent Leaflet map instance
  const map = useMap();

  useEffect(() => {
    // Convert density cells to [lat, lon, intensity] tuples
    const heatCoords = toHeatPoints(points || []);

    // Create Leaflet heat layer with options
    const heatLayer = createHeatLayer(heatCoords, {
      radius: 25,
      blur: 15,
      maxZoom: 17,
    });

    if (!heatLayer) {
      return;
    }

    // Add heat layer to the map
    heatLayer.addTo(map);

    // Cleanup: remove heat layer on unmount or points change
    return () => {
      map.removeLayer(heatLayer);
    };
  }, [map, points]);

  // Leaflet manages rendering directly
  return null;
}

export default HeatLayer;

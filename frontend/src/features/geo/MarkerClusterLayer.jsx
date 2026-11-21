/**
 * MarkerClusterLayer component: groups map markers into clusters using leaflet.markercluster.
 */
import { useEffect } from "react";
import { useMap } from "react-leaflet";
import L from "./leafletSetup";
import * as MarkerClusterModule from "leaflet.markercluster";
import "leaflet.markercluster/dist/MarkerCluster.css";
import "leaflet.markercluster/dist/MarkerCluster.Default.css";

import { buildPopupHtml } from "./mapHelpers";

/**
 * Helper to safely instantiate a marker cluster group, with fallback to standard FeatureGroup.
 */
function createClusterGroup() {
  if (typeof L.markerClusterGroup === "function") {
    return L.markerClusterGroup();
  }
  if (typeof window !== "undefined" && typeof window.L?.markerClusterGroup === "function") {
    return window.L.markerClusterGroup();
  }
  if (MarkerClusterModule && typeof MarkerClusterModule.MarkerClusterGroup === "function") {
    return new MarkerClusterModule.MarkerClusterGroup();
  }
  // Safe fallback if cluster plugin cannot attach
  return L.featureGroup();
}

/**
 * Leaflet cluster layer that places complaints inside an L.markerClusterGroup.
 *
 * @param {Object} props Component properties containing complaints list.
 */
function MarkerClusterLayer({ complaints }) {
  // Access the parent Leaflet map instance
  const map = useMap();

  useEffect(() => {
    // Create a new marker cluster group
    const clusterGroup = createClusterGroup();

    // Iterate over complaints and add individual markers to the cluster group
    (complaints || []).forEach((complaint) => {
      // Validate coordinates exist
      if (complaint.latitude != null && complaint.longitude != null) {
        // Create marker at complaint coordinates
        const marker = L.marker([complaint.latitude, complaint.longitude]);
        // Bind popup with sanitized HTML content
        const popupContent = buildPopupHtml(complaint);
        marker.bindPopup(popupContent);
        // Add marker to cluster group
        clusterGroup.addLayer(marker);
      }
    });

    // Add cluster group to the Leaflet map
    map.addLayer(clusterGroup);

    // Cleanup: remove cluster group when complaints change or component unmounts
    return () => {
      map.removeLayer(clusterGroup);
    };
  }, [map, complaints]);

  // This component manages Leaflet map layers directly and renders no DOM elements
  return null;
}

export default MarkerClusterLayer;

/**
 * Global Leaflet configuration.
 * Ensures `window.L` is initialized before any Leaflet plugins run,
 * and fixes default marker icon paths when bundled with Vite.
 */
import L from "leaflet";
import "leaflet/dist/leaflet.css";

import iconUrl from "leaflet/dist/images/marker-icon.png";
import iconRetinaUrl from "leaflet/dist/images/marker-icon-2x.png";
import shadowUrl from "leaflet/dist/images/marker-shadow.png";

// Fix default marker icon paths in Vite bundling
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl,
  iconRetinaUrl,
  shadowUrl,
});

// Ensure global window.L is available for plugins
if (typeof window !== "undefined") {
  window.L = L;
}

export default L;

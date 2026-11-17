import { useState } from "react";

/**
 * Hook to retrieve coordinates from the browser's navigator.geolocation.
 */
export function useGeolocation() {
  const [coordinates, setCoordinates] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Request user's current location
  function getLocation() {
    if (!navigator.geolocation) {
      setError("Geolocation is not supported by your browser");
      return;
    }

    setLoading(true);
    setError("");

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLoading(false);
        setCoordinates({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        });
      },
      (err) => {
        setLoading(false);
        setError(err.message || "Unable to retrieve location");
      }
    );
  }

  return { coordinates, error, loading, getLocation };
}

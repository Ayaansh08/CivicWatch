import React from "react";
import { render, screen, fireEvent, renderHook, act } from "@testing-library/react";
import { useGeolocation } from "../../features/citizen/useGeolocation";
import LocationPicker from "../../features/citizen/LocationPicker";

// Mock react-leaflet
let triggerMapClick = null;
jest.mock("react-leaflet", () => {
  return {
    MapContainer: ({ children }) => <div data-testid="map-container">{children}</div>,
    TileLayer: () => <div data-testid="tile-layer" />,
    Marker: ({ position }) => <div data-testid="marker">{position[0]},{position[1]}</div>,
    useMapEvents: (handlers) => {
      triggerMapClick = handlers.click;
      return null;
    },
    useMap: () => ({
      setView: jest.fn(),
      getZoom: () => 13,
    }),
  };
});

describe("Location pin-drop and useGeolocation", () => {
  const originalGeolocation = navigator.geolocation;

  afterEach(() => {
    jest.clearAllMocks();
  });

  afterAll(() => {
    Object.defineProperty(navigator, "geolocation", {
      value: originalGeolocation,
      writable: true,
    });
  });

  test("hook returns coordinates on success", () => {
    const mockGeolocation = {
      getCurrentPosition: jest.fn((success) =>
        success({
          coords: { latitude: 28.5355, longitude: 77.3910 },
        })
      ),
    };
    Object.defineProperty(navigator, "geolocation", {
      value: mockGeolocation,
      writable: true,
    });

    const { result } = renderHook(() => useGeolocation());
    act(() => {
      result.current.getLocation();
    });

    expect(result.current.coordinates).toEqual({ latitude: 28.5355, longitude: 77.3910 });
    expect(result.current.error).toBe("");
  });

  test("hook returns an error message on denial", () => {
    const mockGeolocation = {
      getCurrentPosition: jest.fn((_, error) =>
        error({ message: "User denied Geolocation" })
      ),
    };
    Object.defineProperty(navigator, "geolocation", {
      value: mockGeolocation,
      writable: true,
    });

    const { result } = renderHook(() => useGeolocation());
    act(() => {
      result.current.getLocation();
    });

    expect(result.current.error).toBe("User denied Geolocation");
    expect(result.current.coordinates).toBeNull();
  });

  test("button fills coordinates using geolocation", () => {
    const mockGeolocation = {
      getCurrentPosition: jest.fn((success) =>
        success({
          coords: { latitude: 28.6200, longitude: 77.3600 },
        })
      ),
    };
    Object.defineProperty(navigator, "geolocation", {
      value: mockGeolocation,
      writable: true,
    });

    const onLocationChange = jest.fn();
    render(<LocationPicker latitude={null} longitude={null} onLocationChange={onLocationChange} />);

    fireEvent.click(screen.getByRole("button", { name: /use my location/i }));
    expect(onLocationChange).toHaveBeenCalledWith(28.6200, 77.3600);
  });

  test("map click updates coordinates", () => {
    const onLocationChange = jest.fn();
    render(<LocationPicker latitude={null} longitude={null} onLocationChange={onLocationChange} />);

    expect(triggerMapClick).toBeDefined();
    act(() => {
      triggerMapClick({ latlng: { lat: 28.7041, lng: 77.1025 } });
    });

    expect(onLocationChange).toHaveBeenCalledWith(28.7041, 77.1025);
  });
});

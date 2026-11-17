import { TextEncoder, TextDecoder } from "util";

globalThis.TextEncoder = TextEncoder;
globalThis.TextDecoder = TextDecoder;

import "@testing-library/jest-dom";

// Mock react-leaflet globally for Jest tests
jest.mock("react-leaflet", () => {
  return {
    MapContainer: ({ children }) => <div data-testid="map-container">{children}</div>,
    TileLayer: () => <div data-testid="tile-layer" />,
    Marker: ({ children, position }) => (
      <div data-testid="marker" data-lat={position?.[0]} data-lon={position?.[1]}>
        {children}
      </div>
    ),
    Popup: ({ children }) => <div data-testid="popup">{children}</div>,
    useMapEvents: () => null,
    useMap: () => ({
      setView: jest.fn(),
      getZoom: () => 13,
    }),
  };
});

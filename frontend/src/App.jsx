import React, { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";
import ComplaintForm from "./features/citizen/ComplaintForm";

const MapView = lazy(() => import("./features/geo/MapView"));

/** Displays the CivicWatch home page. */
function Home() {
  return (
    <div>
      <h1>CivicWatch</h1>
    </div>
  );
}

/** Defines the application routes. */
function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/report" element={<ComplaintForm />} />
      <Route
        path="/map"
        element={
          <Suspense fallback={<div>Loading map...</div>}>
            <MapView />
          </Suspense>
        }
      />
    </Routes>
  );
}

export default App;

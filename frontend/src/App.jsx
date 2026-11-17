import React, { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";
import ComplaintForm from "./features/citizen/ComplaintForm";
import MyComplaints from "./features/citizen/MyComplaints";
import LoginPage from "./features/auth/LoginPage";
import RegisterPage from "./features/auth/RegisterPage";

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
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/report" element={<ComplaintForm />} />
      <Route path="/my-complaints" element={<MyComplaints />} />
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

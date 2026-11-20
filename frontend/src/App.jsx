import React, { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";
import ComplaintForm from "./features/citizen/ComplaintForm";
import MyComplaints from "./features/citizen/MyComplaints";
import LoginPage from "./features/auth/LoginPage";
import RegisterPage from "./features/auth/RegisterPage";
import ProtectedRoute from "./features/auth/ProtectedRoute";
import NavBar from "./features/auth/NavBar";
import AuthorityDashboard from "./features/authority/AuthorityDashboard";

// Lazy-load heavy map and reports pages to keep the initial bundle small
const MapView = lazy(() => import("./features/geo/MapView"));
const ReportsPage = lazy(() => import("./features/geo/ReportsPage"));
// Lazy-load the admin page so only admins download that code
const AdminPage = lazy(() => import("./features/admin/AdminPage"));

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
    <>
      {/* Show the navigation bar above all routes */}
      <NavBar />

      <Routes>
        {/* Public routes — no authentication needed */}
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Citizen routes — accessible to citizen, officer, and admin */}
        <Route
          path="/report"
          element={
            <ProtectedRoute allowedRoles={["citizen", "officer", "admin"]}>
              <ComplaintForm />
            </ProtectedRoute>
          }
        />
        <Route
          path="/my-complaints"
          element={
            <ProtectedRoute allowedRoles={["citizen", "officer", "admin"]}>
              <MyComplaints />
            </ProtectedRoute>
          }
        />

        {/* Authority route — accessible to officer and admin */}
        <Route
          path="/authority"
          element={
            <ProtectedRoute allowedRoles={["officer", "admin"]}>
              <AuthorityDashboard />
            </ProtectedRoute>
          }
        />

        {/* Map route — accessible to officer and admin */}
        <Route
          path="/map"
          element={
            <ProtectedRoute allowedRoles={["officer", "admin"]}>
              <Suspense fallback={<div>Loading map...</div>}>
                <MapView />
              </Suspense>
            </ProtectedRoute>
          }
        />

        {/* Reports route — accessible to officer and admin */}
        <Route
          path="/reports"
          element={
            <ProtectedRoute allowedRoles={["officer", "admin"]}>
              <Suspense fallback={<div>Loading reports...</div>}>
                <ReportsPage />
              </Suspense>
            </ProtectedRoute>
          }
        />

        {/* Admin route — accessible to admin only */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <Suspense fallback={<div>Loading admin...</div>}>
                <AdminPage />
              </Suspense>
            </ProtectedRoute>
          }
        />
      </Routes>
    </>
  );
}

export default App;

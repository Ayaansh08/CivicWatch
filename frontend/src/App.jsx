import React, { lazy, Suspense, useEffect, useState } from "react";
import { Routes, Route, Link } from "react-router-dom";
import ComplaintForm from "./features/citizen/ComplaintForm";
import MyComplaints from "./features/citizen/MyComplaints";
import LoginPage from "./features/auth/LoginPage";
import RegisterPage from "./features/auth/RegisterPage";
import ProtectedRoute from "./features/auth/ProtectedRoute";
import NavBar from "./features/auth/NavBar";
import AuthorityDashboard from "./features/authority/AuthorityDashboard";
import { TOKEN_KEY } from "./config";
import { getCurrentUser } from "./features/auth/authApi";

// Lazy-load heavy map and reports pages to keep the initial bundle small
const MapView = lazy(() => import("./features/geo/MapView"));
const ReportsPage = lazy(() => import("./features/geo/ReportsPage"));
// Lazy-load the admin page so only admins download that code
const AdminPage = lazy(() => import("./features/admin/AdminPage"));

/** Displays the CivicWatch home page with landing info or role dashboard. */
function Home() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
      setLoading(false);
      return;
    }
    getCurrentUser(token)
      .then((data) => setUser(data))
      .catch(() => {
        localStorage.removeItem(TOKEN_KEY);
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="home-container">
      <h1>CivicWatch</h1>
      <p className="home-subtitle">
        Connecting citizens with local government to report, track, and resolve civic complaints.
      </p>

      {!loading && !user && (
        <div className="home-auth-actions">
          <div className="home-cta-card">
            <h2>Welcome</h2>
            <p>Log in to access your dashboard, file issues, or manage city complaints.</p>
            <div className="home-buttons">
              <Link to="/login" className="btn btn-primary">Log In</Link>
              <Link to="/register" className="btn btn-secondary">Register as Citizen</Link>
            </div>
            <div className="home-demo-hint">
              <strong>Admin Demo Account:</strong>
              <span><code>admin@civicwatch.com</code> / <code>secret123</code></span>
            </div>
          </div>
        </div>
      )}

      {!loading && user && (
        <div className="home-user-dashboard">
          <p className="welcome-banner">
            Logged in as <strong>{user.name}</strong> ({user.role})
          </p>
          <div className="home-quick-links">
            {(user.role === "citizen" || user.role === "officer" || user.role === "admin") && (
              <>
                <Link to="/report" className="dashboard-card">
                  <h3>Report Issue</h3>
                  <p>File a new complaint with category, description, and location pin.</p>
                </Link>
                <Link to="/my-complaints" className="dashboard-card">
                  <h3>My Complaints</h3>
                  <p>Track reported complaints, view progress history, and rate resolution.</p>
                </Link>
              </>
            )}
            {(user.role === "officer" || user.role === "admin") && (
              <>
                <Link to="/authority" className="dashboard-card">
                  <h3>Authority Dashboard</h3>
                  <p>Review incoming issues, assign departments, and resolve tickets.</p>
                </Link>
                <Link to="/map" className="dashboard-card">
                  <h3>Geospatial Map</h3>
                  <p>Explore heatmaps, clustered markers, and repeat-issue hotspots.</p>
                </Link>
                <Link to="/reports" className="dashboard-card">
                  <h3>Analytics Reports</h3>
                  <p>View resolution metrics, department workloads, and SLA charts.</p>
                </Link>
              </>
            )}
            {user.role === "admin" && (
              <Link to="/admin" className="dashboard-card">
                <h3>Admin Management</h3>
                <p>Create and manage city departments and officer accounts.</p>
              </Link>
            )}
          </div>
        </div>
      )}
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

        {/* Map route — accessible to citizen, officer, and admin */}
        <Route
          path="/map"
          element={
            <ProtectedRoute allowedRoles={["citizen", "officer", "admin"]}>
              <Suspense fallback={<div className="status-message" style={{ textAlign: "center", padding: "40px" }}>Loading map...</div>}>
                <MapView />
              </Suspense>
            </ProtectedRoute>
          }
        />

        {/* Reports route — accessible to citizen, officer, and admin */}
        <Route
          path="/reports"
          element={
            <ProtectedRoute allowedRoles={["citizen", "officer", "admin"]}>
              <Suspense fallback={<div className="status-message" style={{ textAlign: "center", padding: "40px" }}>Loading reports...</div>}>
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

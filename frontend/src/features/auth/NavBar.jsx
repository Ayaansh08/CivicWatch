import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { TOKEN_KEY } from "../../config";
import { getCurrentUser } from "./authApi";
import Logout from "./Logout";
import "./auth.css";

/**
 * Top navigation bar that shows links based on the current user's role.
 * Citizens see Report and My Complaints.
 * Officers see Authority, Map, and Reports.
 * Admins see everything plus Admin.
 * Shows nothing when the user is not logged in.
 */
function NavBar() {
  // Store the current user object (or null when not logged in)
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Read the token from localStorage
    const token = localStorage.getItem(TOKEN_KEY);
    // If no token exists, stay logged out
    if (!token) {
      return;
    }
    // Fetch the current user's profile from the backend
    getCurrentUser(token)
      .then((data) => setUser(data))
      .catch(() => {
        // If the token is invalid or expired, clear it and show no nav
        localStorage.removeItem(TOKEN_KEY);
        setUser(null);
      });
  }, []);

  // Show nothing when the user is not logged in
  if (!user) {
    return null;
  }

  // Determine the user's role for conditional link rendering
  const role = user.role;

  return (
    <nav className="navbar">
      {/* Links visible to citizens, officers, and admins */}
      {(role === "citizen" || role === "officer" || role === "admin") && (
        <Link to="/report" className="nav-link">Report</Link>
      )}
      {(role === "citizen" || role === "officer" || role === "admin") && (
        <Link to="/my-complaints" className="nav-link">My Complaints</Link>
      )}

      {/* Links visible to officers and admins only */}
      {(role === "officer" || role === "admin") && (
        <Link to="/authority" className="nav-link">Authority</Link>
      )}
      {(role === "officer" || role === "admin") && (
        <Link to="/map" className="nav-link">Map</Link>
      )}
      {(role === "officer" || role === "admin") && (
        <Link to="/reports" className="nav-link">Reports</Link>
      )}

      {/* Admin-only link */}
      {role === "admin" && (
        <Link to="/admin" className="nav-link">Admin</Link>
      )}

      {/* Logout button is always shown when logged in */}
      <Logout />
    </nav>
  );
}

export default NavBar;

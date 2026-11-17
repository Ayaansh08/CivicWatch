import React, { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { TOKEN_KEY } from "../../config";
import { getCurrentUser } from "./authApi";
import "./auth.css";

/**
 * Wraps a protected route and verifies that the user is logged in
 * and has one of the allowed roles via GET /auth/me.
 */
function ProtectedRoute({ allowedRoles, children }) {
  // Read the saved JWT token from localStorage
  const token = localStorage.getItem(TOKEN_KEY);
  // Track access check progress: "loading", "allowed", "forbidden", or "unauthorized"
  const [accessState, setAccessState] = useState("loading");

  useEffect(() => {
    // Skip the API call if there is no token (component redirects below)
    if (!token) {
      return undefined;
    }

    // Prevent state updates if the component unmounts before fetch finishes
    let isMounted = true;

    // Ask the backend who the current user is and what role they have
    getCurrentUser(token)
      .then((user) => {
        if (!isMounted) {
          return;
        }
        // Use the backend role (defaulting to citizen only if a legacy mock omits role)
        const userRole = user && user.role ? user.role : "citizen";
        // Allow access only if the user's role is listed in allowedRoles
        if (allowedRoles.includes(userRole)) {
          setAccessState("allowed");
        } else {
          setAccessState("forbidden");
        }
      })
      .catch((error) => {
        if (!isMounted) {
          return;
        }
        // Remove invalid or expired tokens on 401 and send the user to login
        if (error.status === 401) {
          localStorage.removeItem(TOKEN_KEY);
          setAccessState("unauthorized");
        } else {
          setAccessState("forbidden");
        }
      });

    return () => {
      isMounted = false;
    };
  }, [token, allowedRoles]);

  // Redirect immediately to /login if no token exists in localStorage
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  // Show a loading indicator while GET /auth/me is running
  if (accessState === "loading") {
    return <div className="auth-status">Checking access...</div>;
  }

  // Redirect to /login if the backend rejected the token with 401
  if (accessState === "unauthorized") {
    return <Navigate to="/login" replace />;
  }

  // Show a clear error message if the user's role is not allowed on this page
  if (accessState === "forbidden") {
    return (
      <div className="auth-error-banner" role="alert">
        You do not have permission to view this page
      </div>
    );
  }

  // Render the protected page content when access is granted
  return children;
}

export default ProtectedRoute;

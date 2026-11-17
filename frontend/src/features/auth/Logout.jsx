import React from "react";
import { useNavigate } from "react-router-dom";
import { TOKEN_KEY } from "../../config";
import "./auth.css";

/**
 * Displays a Log Out button that clears the stored JWT token
 * and navigates the user back to the login page.
 */
function Logout() {
  // Router helper for redirecting after logout
  const navigate = useNavigate();

  /** Clear the auth token and redirect to /login. */
  function handleLogout() {
    // Remove the saved token from localStorage
    localStorage.removeItem(TOKEN_KEY);
    // Navigate the user back to the login page
    navigate("/login");
  }

  return (
    <button type="button" className="auth-button" onClick={handleLogout}>
      Log Out
    </button>
  );
}

export default Logout;

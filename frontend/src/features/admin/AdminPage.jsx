import React from "react";
import DepartmentsPanel from "./DepartmentsPanel";
import OfficersPanel from "./OfficersPanel";
import "./admin.css";

/**
 * Admin dashboard page with two management panels side by side:
 * one for city departments and one for officer accounts.
 */
function AdminPage() {
  return (
    <div className="admin-page">
      <h1>Admin Dashboard</h1>
      {/* Departments management panel */}
      <DepartmentsPanel />
      {/* Officers management panel */}
      <OfficersPanel />
    </div>
  );
}

export default AdminPage;

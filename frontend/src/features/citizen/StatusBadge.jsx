import React from "react";

// Color mapping for complaint status
function getStatusBadgeStyle(status) {
  switch (status) {
    case "Submitted":
      return { backgroundColor: "#e3f2fd", color: "#0d47a1" };
    case "Under Review":
      return { backgroundColor: "#fff8e1", color: "#f57f17" };
    case "Assigned":
      return { backgroundColor: "#ede7f6", color: "#4a148c" };
    case "In Progress":
      return { backgroundColor: "#e0f2f1", color: "#004d40" };
    case "Resolved":
      return { backgroundColor: "#e8f5e9", color: "#1b5e20" };
    case "Rejected":
      return { backgroundColor: "#ffebee", color: "#b71c1c" };
    default:
      return { backgroundColor: "#eee", color: "#333" };
  }
}

/**
 * Reusable visual badge displaying complaint status with distinct styling.
 */
export default function StatusBadge({ status }) {
  return (
    <span
      className="status-badge"
      style={{
        padding: "4px 8px",
        borderRadius: "4px",
        fontWeight: "bold",
        fontSize: "12px",
        ...getStatusBadgeStyle(status),
      }}
    >
      {status}
    </span>
  );
}

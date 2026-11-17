import React from "react";

/**
 * Renders the chronological status change events of a complaint.
 */
export default function StatusTimeline({ history }) {
  if (!history || history.length === 0) {
    return <p>No status history recorded yet.</p>;
  }

  return (
    <div className="status-timeline">
      <h4>Status Timeline</h4>
      <ul style={{ listStyle: "none", paddingLeft: 0 }}>
        {history.map((item) => (
          <li key={item.id} style={{ marginBottom: "12px", borderLeft: "2px solid #1769aa", paddingLeft: "10px" }}>
            <div>
              <strong>{item.status}</strong>
              <span style={{ fontSize: "12px", color: "#666", marginLeft: "10px" }}>
                {new Date(item.changed_at).toLocaleString()}
              </span>
            </div>
            {item.note && <div style={{ fontSize: "14px", color: "#444" }}>{item.note}</div>}
          </li>
        ))}
      </ul>
    </div>
  );
}

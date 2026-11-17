import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchMyComplaints, fetchHistory } from "./api";
import StatusTimeline from "./StatusTimeline";
import { TOKEN_KEY } from "../../config";
import "./citizen.css";

// Helper for status badge styling
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
 * Citizen dashboard displaying their submitted complaints, badges, and timelines.
 */
export default function MyComplaints() {
  const token = localStorage.getItem(TOKEN_KEY);
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(Boolean(token));
  const [error, setError] = useState("");
  const [selectedComplaintId, setSelectedComplaintId] = useState(null);
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  useEffect(() => {
    if (!token) {
      return;
    }

    async function loadData() {
      try {
        setLoading(true);
        const data = await fetchMyComplaints();
        setComplaints(data);
        setError("");
      } catch {
        setError("Could not load complaints");
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [token]);

  async function handleSelectComplaint(id) {
    if (selectedComplaintId === id) {
      setSelectedComplaintId(null);
      setHistory([]);
      return;
    }

    setSelectedComplaintId(id);
    try {
      setHistoryLoading(true);
      const hist = await fetchHistory(id);
      setHistory(hist);
    } catch {
      setHistory([]);
    } finally {
      setHistoryLoading(false);
    }
  }

  if (!token) {
    return (
      <main className="complaint-page">
        <h2>My Complaints</h2>
        <p>Please log in to continue</p>
        <Link to="/login">Go to Login</Link>
      </main>
    );
  }

  return (
    <main className="complaint-page">
      <h2>My Complaints</h2>

      {loading && <p>Loading complaints...</p>}
      {error && <p role="alert">{error}</p>}

      {!loading && !error && complaints.length === 0 && (
        <p>No complaints yet</p>
      )}

      {!loading && !error && complaints.length > 0 && (
        <div className="complaints-list">
          {complaints.map((c) => (
            <div
              key={c.id}
              className="complaint-card"
              style={{
                border: "1px solid #ccc",
                borderRadius: "6px",
                padding: "16px",
                marginBottom: "16px",
                cursor: "pointer",
              }}
              onClick={() => handleSelectComplaint(c.id)}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <h3 style={{ margin: 0 }}>{c.title}</h3>
                <span
                  className="status-badge"
                  style={{
                    padding: "4px 8px",
                    borderRadius: "4px",
                    fontWeight: "bold",
                    fontSize: "12px",
                    ...getStatusBadgeStyle(c.status),
                  }}
                >
                  {c.status}
                </span>
              </div>
              <p style={{ margin: "8px 0" }}>{c.description}</p>
              <div style={{ fontSize: "13px", color: "#666" }}>
                <span>Category: {c.category_name}</span> |{" "}
                <span>Priority: {c.priority}</span>
              </div>

              {selectedComplaintId === c.id && (
                <div style={{ marginTop: "16px", borderTop: "1px solid #eee", paddingTop: "12px" }}>
                  {c.photo_path && (
                    <div style={{ marginBottom: "12px" }}>
                      <h5>Attached Photo:</h5>
                      <img
                        src={`http://localhost:8000${c.photo_path}`}
                        alt="Complaint evidence"
                        style={{ maxWidth: "300px", maxHeight: "200px", borderRadius: "4px" }}
                      />
                    </div>
                  )}
                  {historyLoading ? <p>Loading timeline...</p> : <StatusTimeline history={history} />}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </main>
  );
}

import React, { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import { fetchMyComplaints, fetchHistory, fetchCategories } from "./api";
import StatusTimeline from "./StatusTimeline";
import FeedbackPanel from "./FeedbackPanel";
import StatusBadge from "./StatusBadge";
import { TOKEN_KEY } from "../../config";
import "./citizen.css";

/**
 * Citizen dashboard displaying their submitted complaints, badges, and timelines.
 */
export default function MyComplaints() {
  const token = localStorage.getItem(TOKEN_KEY);
  const [complaints, setComplaints] = useState([]);
  const [categories, setCategories] = useState([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [loading, setLoading] = useState(Boolean(token));
  const [error, setError] = useState("");
  const [selectedComplaintId, setSelectedComplaintId] = useState(null);
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  const loadData = useCallback(async (filters = {}) => {
    try {
      setLoading(true);
      const data = await fetchMyComplaints(filters);
      setComplaints(data);
      setError("");
    } catch {
      setError("Could not load complaints");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!token) return;

    fetchCategories().then(setCategories).catch(() => {});
  }, [token]);

  useEffect(() => {
    if (!token) return;

    loadData({
      status: statusFilter || undefined,
      category_id: categoryFilter || undefined,
    });
  }, [token, statusFilter, categoryFilter, loadData]);

  function handleClearFilters() {
    setStatusFilter("");
    setCategoryFilter("");
  }

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

      <div className="complaint-filters" style={{ display: "flex", gap: "10px", marginBottom: "16px", alignItems: "center" }}>
        <select
          aria-label="Filter by status"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          style={{ padding: "6px" }}
        >
          <option value="">All Statuses</option>
          <option value="Submitted">Submitted</option>
          <option value="Under Review">Under Review</option>
          <option value="Assigned">Assigned</option>
          <option value="In Progress">In Progress</option>
          <option value="Resolved">Resolved</option>
          <option value="Rejected">Rejected</option>
        </select>

        <select
          aria-label="Filter by category"
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          style={{ padding: "6px" }}
        >
          <option value="">All Categories</option>
          {categories.map((cat) => (
            <option key={cat.id} value={cat.id}>{cat.name}</option>
          ))}
        </select>

        {(statusFilter || categoryFilter) && (
          <button
            type="button"
            onClick={handleClearFilters}
            style={{ padding: "6px 12px" }}
          >
            Clear filters
          </button>
        )}
      </div>

      {loading && <p>Loading complaints...</p>}
      {error && <p role="alert">{error}</p>}

      {!loading && !error && complaints.length === 0 && (
        <p>
          {statusFilter || categoryFilter
            ? "No complaints match these filters"
            : "No complaints yet"}
        </p>
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
                <StatusBadge status={c.status} />
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
                  <FeedbackPanel
                    complaint={c}
                    onComplaintUpdated={() => {
                      fetchMyComplaints().then(setComplaints);
                      fetchHistory(c.id).then(setHistory);
                    }}
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </main>
  );
}

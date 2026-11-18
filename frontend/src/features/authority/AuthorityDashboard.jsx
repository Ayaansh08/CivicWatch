/** Authority Dashboard — lists complaints and lets officers manage them. */
import { useState, useEffect } from "react";
import { TOKEN_KEY } from "../../config";
import {
  fetchComplaints,
  escalateOverdue,
  ALLOWED_NEXT,
} from "./authorityApi";
import AssignForm from "./AssignForm";
import StatusUpdateForm from "./StatusUpdateForm";
import "./authority.css";

// Status options available in the filter dropdown
const STATUS_OPTIONS = [
  "", "Submitted", "Under Review", "Assigned", "In Progress", "Resolved", "Rejected",
];

// Sort options available in the dropdown
const SORT_OPTIONS = [
  { value: "newest", label: "Newest first" },
  { value: "age", label: "Oldest first" },
  { value: "priority", label: "By priority" },
];

/**
 * AuthorityDashboard — main page for authority officers.
 *
 * Shows a table of complaints with filters for status and sort order,
 * plus a detail panel with assign and status-change forms.
 */
function AuthorityDashboard() {
  // Check if user is logged in
  const token = localStorage.getItem(TOKEN_KEY);

  // List of complaints returned from the API
  const [complaints, setComplaints] = useState([]);
  // Loading and error state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  // Active filter values
  const [statusFilter, setStatusFilter] = useState("");
  const [sortOrder, setSortOrder] = useState("newest");
  // The complaint currently shown in the detail panel
  const [selected, setSelected] = useState(null);
  // Escalation result message
  const [escalateMsg, setEscalateMsg] = useState("");

  // Load complaints whenever filters change
  useEffect(() => {
    if (!token) return;
    loadComplaints();
  }, [statusFilter, sortOrder]);

  /** Fetch complaints from the API and update state. */
  async function loadComplaints() {
    setLoading(true);
    setError("");
    try {
      const data = await fetchComplaints(statusFilter, "", sortOrder);
      setComplaints(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  /** Trigger the escalate endpoint and show the result. */
  async function handleEscalate() {
    setEscalateMsg("");
    try {
      const result = await escalateOverdue();
      setEscalateMsg(`Escalated ${result.escalated_count} complaint(s)`);
      loadComplaints();
    } catch (err) {
      setEscalateMsg(err.message);
    }
  }

  // If not logged in, show a prompt instead of the dashboard
  if (!token) {
    return <p>Please log in to continue</p>;
  }

  return (
    <div className="authority-dashboard">
      <h1>Authority Dashboard</h1>

      {/* Filter and sort controls */}
      <div className="controls">
        <label>
          Filter by status
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            {STATUS_OPTIONS.map((s) => (
              <option key={s} value={s}>
                {s || "All"}
              </option>
            ))}
          </select>
        </label>
        <label>
          Sort
          <select
            value={sortOrder}
            onChange={(e) => setSortOrder(e.target.value)}
          >
            {SORT_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </label>
        <button onClick={handleEscalate}>Escalate overdue</button>
        {escalateMsg && <span className="escalate-msg">{escalateMsg}</span>}
      </div>

      {/* Loading / error / empty states */}
      {loading && <p>Loading...</p>}
      {error && <p className="error">{error}</p>}
      {!loading && !error && complaints.length === 0 && (
        <p>No complaints found</p>
      )}

      {/* Complaints table */}
      {complaints.length > 0 && (
        <table className="complaints-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Category</th>
              <th>Status</th>
              <th>Priority</th>
              <th>Department</th>
              <th>Age (days)</th>
            </tr>
          </thead>
          <tbody>
            {complaints.map((c) => {
              // Calculate age in days from created_at
              const age = c.created_at
                ? Math.floor(
                    (Date.now() - new Date(c.created_at).getTime()) /
                      86400000
                  )
                : "—";
              return (
                <tr
                  key={c.id}
                  onClick={() => setSelected(c)}
                  className={selected?.id === c.id ? "selected" : ""}
                >
                  <td>{c.id}</td>
                  <td>{c.title}</td>
                  <td>{c.category_name}</td>
                  <td>
                    <span className={`badge badge-${c.status.replace(" ", "-")}`}>
                      {c.status}
                    </span>
                  </td>
                  <td>{c.priority}</td>
                  <td>{c.department_name || "—"}</td>
                  <td>{age}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}

      {/* Detail panel for selected complaint */}
      {selected && (
        <div className="detail-panel">
          <h2>Complaint #{selected.id}: {selected.title}</h2>
          <p>Status: <strong>{selected.status}</strong></p>

          {/* Show AssignForm only when complaint is Under Review */}
          {selected.status === "Under Review" && (
            <AssignForm
              complaintId={selected.id}
              onSuccess={() => {
                setSelected(null);
                loadComplaints();
              }}
            />
          )}

          {/* Show status update buttons for all other non-final statuses */}
          {ALLOWED_NEXT[selected.status]?.length > 0 &&
            selected.status !== "Under Review" && (
              <StatusUpdateForm
                complaintId={selected.id}
                currentStatus={selected.status}
                onSuccess={() => {
                  setSelected(null);
                  loadComplaints();
                }}
              />
            )}
        </div>
      )}
    </div>
  );
}

export default AuthorityDashboard;

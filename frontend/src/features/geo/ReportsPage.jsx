/**
 * ReportsPage component: displays spatial analytics metrics and breakdown charts.
 */
import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { fetchReport } from "./geoApi";
import BarChart from "./BarChart";
import "./geo.css";

/**
 * Analytics and reporting dashboard page.
 */
function ReportsPage() {
  // Component state for report data, loading indicator, and error message
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch report summary on mount
  useEffect(() => {
    let isMounted = true;

    async function loadReport() {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchReport();
        if (isMounted) {
          setReport(data);
          setLoading(false);
        }
      } catch {
        if (isMounted) {
          setError("Could not load report");
          setLoading(false);
        }
      }
    }

    loadReport();

    return () => {
      isMounted = false;
    };
  }, []);

  // Compute resolved count from by_status distribution
  const resolvedCount = report?.by_status
    ? report.by_status.find((s) => s.status === "Resolved")?.count || 0
    : 0;

  return (
    <div className="reports-page-container" style={{ maxWidth: "900px", margin: "20px auto", padding: "0 16px" }}>
      {/* Page header and navigation link */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <h2>Geospatial Analytics & Reports</h2>
        <Link to="/map" style={{ color: "#0070f3", textDecoration: "none", fontWeight: "bold" }}>
          &larr; Back to Map
        </Link>
      </div>

      {/* State messages */}
      {loading && <p className="status-message">Loading report...</p>}
      {error && <p className="error-message">{error}</p>}
      {!loading && !error && report && report.total === 0 && (
        <p className="empty-message">No data yet</p>
      )}

      {/* Main analytics dashboard content */}
      {!loading && !error && report && report.total > 0 && (
        <div>
          {/* Summary metric cards */}
          <div
            className="summary-cards"
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
              gap: "16px",
              marginBottom: "28px",
            }}
          >
            <div style={{ padding: "16px", backgroundColor: "#f8f9fa", borderRadius: "8px", border: "1px solid #e9ecef" }}>
              <h4 style={{ margin: "0 0 8px 0", color: "#6c757d" }}>Total Complaints</h4>
              <p style={{ margin: 0, fontSize: "28px", fontWeight: "bold", color: "#212529" }}>{report.total}</p>
            </div>

            <div style={{ padding: "16px", backgroundColor: "#f8f9fa", borderRadius: "8px", border: "1px solid #e9ecef" }}>
              <h4 style={{ margin: "0 0 8px 0", color: "#6c757d" }}>Resolved Complaints</h4>
              <p style={{ margin: 0, fontSize: "28px", fontWeight: "bold", color: "#28a745" }}>{resolvedCount}</p>
            </div>

            <div style={{ padding: "16px", backgroundColor: "#f8f9fa", borderRadius: "8px", border: "1px solid #e9ecef" }}>
              <h4 style={{ margin: "0 0 8px 0", color: "#6c757d" }}>Avg Resolution Time</h4>
              <p style={{ margin: 0, fontSize: "28px", fontWeight: "bold", color: "#17a2b8" }}>
                {report.avg_resolution_hours != null ? `${report.avg_resolution_hours} hrs` : "N/A"}
              </p>
            </div>
          </div>

          {/* Breakdown by Status */}
          <div style={{ marginBottom: "28px" }}>
            <h3>Complaints by Status</h3>
            <BarChart
              items={(report.by_status || []).map((s) => ({
                label: s.status,
                value: s.count,
              }))}
            />
          </div>

          {/* Breakdown by Category */}
          <div style={{ marginBottom: "28px" }}>
            <h3>Complaints by Category</h3>
            <BarChart
              items={(report.by_category || []).map((c) => ({
                label: c.category,
                value: c.count,
              }))}
            />
          </div>

          {/* Breakdown by Top Geographic Areas */}
          <div style={{ marginBottom: "28px" }}>
            <h3>Top Geographic Areas</h3>
            <BarChart
              items={(report.by_area || []).map((a) => ({
                label: a.area,
                value: a.count,
              }))}
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default ReportsPage;

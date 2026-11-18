/**
 * Custom hook to manage complaints state, filtering, and sorting (CW-311 refactor).
 */
import { useState, useEffect, useCallback } from "react";
import { fetchComplaints } from "./authorityApi";

/**
 * useComplaints — manages complaint list fetching and filter states.
 *
 * @param {string} token - The auth token from localStorage
 * @returns {object} complaints state and control functions
 */
export function useComplaints(token) {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [sortOrder, setSortOrder] = useState("newest");

  const loadComplaints = useCallback(async () => {
    if (!token) return;
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
  }, [token, statusFilter, sortOrder]);

  useEffect(() => {
    loadComplaints();
  }, [loadComplaints]);

  return {
    complaints,
    loading,
    error,
    statusFilter,
    setStatusFilter,
    sortOrder,
    setSortOrder,
    loadComplaints,
  };
}

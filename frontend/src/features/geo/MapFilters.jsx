/**
 * MapFilters component: filters map complaints by category and status.
 */
import React, { useState, useEffect } from "react";
import { API_URL, TOKEN_KEY } from "../../config";

// Fallback categories if API request fails
const FALLBACK_CATEGORIES = [
  { id: 1, name: "Pothole" },
  { id: 2, name: "Garbage" },
  { id: 3, name: "Water Leakage" },
  { id: 4, name: "Streetlight" },
];

// Valid complaint workflow statuses
const STATUS_OPTIONS = [
  "Submitted",
  "Under Review",
  "Assigned",
  "In Progress",
  "Resolved",
  "Rejected",
];

/**
 * Filter controls bar for category and status filtering.
 *
 * @param {Object} props Component properties containing filters and onFilterChange callback.
 */
function MapFilters({ filters, onFilterChange }) {
  // Local state for loaded categories list
  const [categories, setCategories] = useState([]);

  // Fetch categories on component mount
  useEffect(() => {
    let isMounted = true;

    async function loadCategories() {
      // Retrieve auth token from localStorage
      const token = localStorage.getItem(TOKEN_KEY);
      try {
        const response = await fetch(`${API_URL}/complaints/categories`, {
          headers: {
            Authorization: `Bearer ${token || ""}`,
          },
        });
        if (!response.ok) {
          throw new Error("Failed to fetch categories");
        }
        const data = await response.json();
        if (isMounted) {
          setCategories(data);
        }
      } catch {
        // Fall back to static category list on network or server error
        if (isMounted) {
          setCategories(FALLBACK_CATEGORIES);
        }
      }
    }

    loadCategories();

    return () => {
      isMounted = false;
    };
  }, []);

  // Handle category selection change
  function handleCategoryChange(e) {
    const value = e.target.value;
    onFilterChange({
      ...filters,
      category_id: value ? Number(value) : "",
    });
  }

  // Handle status selection change
  function handleStatusChange(e) {
    const value = e.target.value;
    onFilterChange({
      ...filters,
      status: value,
    });
  }

  // Handle clear filters click
  function handleClear() {
    onFilterChange({
      category_id: "",
      status: "",
    });
  }

  return (
    <div className="map-filters" style={{ display: "flex", gap: "10px", margin: "10px 0", alignItems: "center" }}>
      {/* Category selector */}
      <select
        aria-label="Category"
        value={filters.category_id || ""}
        onChange={handleCategoryChange}
      >
        <option value="">All Categories</option>
        {categories.map((cat) => (
          <option key={cat.id} value={cat.id}>
            {cat.name}
          </option>
        ))}
      </select>

      {/* Status selector */}
      <select
        aria-label="Status"
        value={filters.status || ""}
        onChange={handleStatusChange}
      >
        <option value="">All Statuses</option>
        {STATUS_OPTIONS.map((st) => (
          <option key={st} value={st}>
            {st}
          </option>
        ))}
      </select>

      {/* Clear filters button */}
      <button type="button" onClick={handleClear}>
        Clear filters
      </button>
    </div>
  );
}

export default MapFilters;

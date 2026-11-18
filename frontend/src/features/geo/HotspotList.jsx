/**
 * HotspotList component: displays a summary table of spatial hotspots.
 * Exported for use in authority dashboards and analytics views.
 */
import React from "react";

/**
 * Tabular list of detected complaint hotspots.
 *
 * @param {Object} props Component properties containing hotspots array.
 */
function HotspotList({ hotspots }) {
  // Empty state display
  if (!hotspots || hotspots.length === 0) {
    return <p className="empty-message">No hotspots detected</p>;
  }

  return (
    <div className="hotspot-list-container">
      <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "10px" }}>
        <thead>
          <tr style={{ backgroundColor: "#f0f0f0", textAlign: "left" }}>
            <th style={{ padding: "8px", border: "1px solid #ddd" }}>Rank</th>
            <th style={{ padding: "8px", border: "1px solid #ddd" }}>Count</th>
            <th style={{ padding: "8px", border: "1px solid #ddd" }}>Main Category</th>
            <th style={{ padding: "8px", border: "1px solid #ddd" }}>Centre</th>
          </tr>
        </thead>
        <tbody>
          {hotspots.map((h, index) => (
            <tr key={`hotspot-row-${index}`}>
              <td style={{ padding: "8px", border: "1px solid #ddd" }}>#{index + 1}</td>
              <td style={{ padding: "8px", border: "1px solid #ddd" }}>{h.count}</td>
              <td style={{ padding: "8px", border: "1px solid #ddd" }}>{h.category}</td>
              <td style={{ padding: "8px", border: "1px solid #ddd" }}>
                {h.center_lat}, {h.center_lon}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default HotspotList;

/**
 * BarChart component: renders a lightweight horizontal bar chart using plain divs and CSS widths.
 */
import React from "react";

/**
 * Lightweight bar chart visualization.
 *
 * @param {Object} props Component properties containing items array [{ label, value }].
 */
function BarChart({ items }) {
  // Return null or placeholder if items is empty
  if (!items || items.length === 0) {
    return <p className="empty-message">No data to display</p>;
  }

  // Find maximum value to calculate proportional widths
  const maxValue = Math.max(...items.map((i) => i.value), 1);

  return (
    <div className="bar-chart" style={{ display: "flex", flexDirection: "column", gap: "8px", margin: "10px 0" }}>
      {items.map((item, index) => {
        // Calculate proportional width percentage
        const widthPercent = Math.max(Math.round((item.value / maxValue) * 100), 2);

        return (
          <div
            key={`bar-${index}`}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              fontSize: "14px",
            }}
          >
            {/* Category / Status / Area label */}
            <span style={{ width: "120px", textAlign: "right", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
              {item.label}
            </span>

            {/* Track container */}
            <div style={{ flex: 1, backgroundColor: "var(--surface-hover, #334155)", borderRadius: "4px", height: "20px", overflow: "hidden" }}>
              {/* Proportional filled bar */}
              <div
                data-testid="bar-fill"
                style={{
                  width: `${widthPercent}%`,
                  height: "100%",
                  backgroundColor: "var(--primary, #3b82f6)",
                  borderRadius: "4px",
                  transition: "width 0.3s ease",
                }}
              />
            </div>

            {/* Numerical value */}
            <span style={{ width: "40px", fontWeight: "bold" }}>{item.value}</span>
          </div>
        );
      })}
    </div>
  );
}

export default BarChart;

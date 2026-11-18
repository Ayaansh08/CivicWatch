/**
 * ComplaintsTable — displays table of complaints with selection support (CW-311).
 */

// One day in milliseconds for age calculation
const MS_PER_DAY = 86400000;

/**
 * ComplaintsTable component.
 *
 * @param {object} props
 * @param {Array} props.complaints - list of complaints to show
 * @param {object} props.selected - currently selected complaint
 * @param {function} props.onSelect - callback when a row is clicked
 */
function ComplaintsTable({ complaints, selected, onSelect }) {
  return (
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
            ? Math.floor((Date.now() - new Date(c.created_at).getTime()) / MS_PER_DAY)
            : "—";

          return (
            <tr
              key={c.id}
              onClick={() => onSelect(c)}
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
  );
}

export default ComplaintsTable;

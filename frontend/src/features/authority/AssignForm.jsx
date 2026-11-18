/** Form to assign a complaint to a department with a priority. */
import { useState, useEffect } from "react";
import { fetchDepartments, assignComplaint } from "./authorityApi";

const PRIORITIES = ["Low", "Medium", "High", "Critical"];

/**
 * AssignForm — lets an officer pick a department and priority,
 * then submits the assignment.
 */
function AssignForm({ complaintId, onSuccess }) {
  // Available departments loaded from the API
  const [departments, setDepartments] = useState([]);
  // Currently selected department id
  const [departmentId, setDepartmentId] = useState("");
  // Currently selected priority
  const [priority, setPriority] = useState("Medium");
  // Submission status message
  const [message, setMessage] = useState("");

  useEffect(() => {
    // Load departments when the form mounts
    fetchDepartments()
      .then(setDepartments)
      .catch(() => setMessage("Could not load departments"));
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setMessage("");
    try {
      // Send the assignment request to the API
      await assignComplaint(complaintId, Number(departmentId), priority);
      setMessage("Complaint assigned successfully");
      if (onSuccess) onSuccess();
    } catch (err) {
      setMessage(err.message);
    }
  }

  return (
    <form onSubmit={handleSubmit} aria-label="assign-form">
      <label>
        Department
        <select
          value={departmentId}
          onChange={(e) => setDepartmentId(e.target.value)}
          required
        >
          <option value="">Select department</option>
          {departments.map((d) => (
            <option key={d.id} value={d.id}>
              {d.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        Priority
        <select value={priority} onChange={(e) => setPriority(e.target.value)}>
          {PRIORITIES.map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </select>
      </label>
      <button type="submit">Assign</button>
      {message && <p>{message}</p>}
    </form>
  );
}

export default AssignForm;

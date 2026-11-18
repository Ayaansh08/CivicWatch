/** Form to move a complaint to its next allowed status. */
import { useState } from "react";
import { updateStatus, ALLOWED_NEXT } from "./authorityApi";

/**
 * StatusUpdateForm — shows buttons for each allowed next status
 * and an optional note field.
 */
function StatusUpdateForm({ complaintId, currentStatus, onSuccess }) {
  // Optional note to attach to the status change
  const [note, setNote] = useState("");
  // Feedback message shown after submission
  const [message, setMessage] = useState("");

  // Get the allowed transitions from the local map
  const nextStatuses = ALLOWED_NEXT[currentStatus] || [];

  async function handleUpdate(newStatus) {
    setMessage("");
    try {
      // Send the status update to the API
      await updateStatus(complaintId, newStatus, note);
      setMessage(`Status updated to ${newStatus}`);
      if (onSuccess) onSuccess();
    } catch (err) {
      setMessage(err.message);
    }
  }

  if (nextStatuses.length === 0) {
    // No further actions possible from this status
    return <p>No further actions available.</p>;
  }

  return (
    <div>
      <label>
        Note (optional)
        <input
          value={note}
          onChange={(e) => setNote(e.target.value)}
          placeholder="Add a note..."
        />
      </label>
      {/* Render one button per allowed next status */}
      {nextStatuses.map((s) => (
        <button key={s} onClick={() => handleUpdate(s)}>
          Move to {s}
        </button>
      ))}
      {message && <p>{message}</p>}
    </div>
  );
}

export default StatusUpdateForm;

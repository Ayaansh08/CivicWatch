import React, { useState } from "react";
import { submitFeedback, reopenComplaint } from "./api";

/**
 * Panel shown only for Resolved complaints allowing star rating, comment, and reopening.
 */
export default function FeedbackPanel({ complaint, onComplaintUpdated }) {
  const [rating, setRating] = useState(complaint.rating || 5);
  const [comment, setComment] = useState("");
  const [feedbackSuccess, setFeedbackSuccess] = useState(Boolean(complaint.rating));
  const [feedbackError, setFeedbackError] = useState("");

  const [reopenReason, setReopenReason] = useState("");
  const [showReopenInput, setShowReopenInput] = useState(false);
  const [reopenError, setReopenError] = useState("");
  const [reopenLoading, setReopenLoading] = useState(false);

  if (complaint.status !== "Resolved") {
    return null;
  }

  async function handleFeedbackSubmit(e) {
    e.preventDefault();
    setFeedbackError("");
    try {
      await submitFeedback(complaint.id, Number(rating), comment.trim() || null);
      setFeedbackSuccess(true);
      if (onComplaintUpdated) onComplaintUpdated();
    } catch (err) {
      setFeedbackError(err.message || "Failed to submit feedback");
    }
  }

  async function handleReopenSubmit(e) {
    e.preventDefault();
    if (!reopenReason.trim()) {
      setReopenError("Please give a reason");
      return;
    }
    if (reopenReason.trim().length < 5) {
      setReopenError("Reason must be at least 5 characters");
      return;
    }

    setReopenError("");
    setReopenLoading(true);
    try {
      await reopenComplaint(complaint.id, reopenReason.trim());
      if (onComplaintUpdated) onComplaintUpdated();
    } catch (err) {
      setReopenError(err.message || "Failed to reopen complaint");
    } finally {
      setReopenLoading(false);
    }
  }

  return (
    <div className="feedback-panel" style={{ marginTop: "16px", padding: "12px", background: "#f9f9f9", borderRadius: "6px" }}>
      <h4>Resolution Feedback & Actions</h4>

      {feedbackSuccess ? (
        <p role="status" style={{ color: "#237a36", fontWeight: "bold" }}>Thank you for your feedback</p>
      ) : (
        <form onSubmit={handleFeedbackSubmit} style={{ marginBottom: "16px" }}>
          <div style={{ marginBottom: "8px" }}>
            <label htmlFor={`rating-${complaint.id}`}>Rating (1-5 stars): </label>
            <select
              id={`rating-${complaint.id}`}
              value={rating}
              onChange={(e) => setRating(e.target.value)}
            >
              {[1, 2, 3, 4, 5].map((num) => (
                <option key={num} value={num}>
                  {num} Star{num > 1 ? "s" : ""}
                </option>
              ))}
            </select>
          </div>
          <div style={{ marginBottom: "8px" }}>
            <input
              type="text"
              placeholder="Optional comment"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              style={{ width: "100%", padding: "6px" }}
            />
          </div>
          {feedbackError && <p role="alert" style={{ color: "#c62828" }}>{feedbackError}</p>}
          <button type="submit" style={{ padding: "6px 12px" }}>Submit Feedback</button>
        </form>
      )}

      <div className="reopen-section" style={{ borderTop: "1px solid #ddd", paddingTop: "12px" }}>
        {!showReopenInput ? (
          <button
            type="button"
            onClick={() => setShowReopenInput(true)}
            style={{ background: "#d32f2f", color: "white", padding: "6px 12px", border: "none", borderRadius: "4px" }}
          >
            Reopen Complaint
          </button>
        ) : (
          <form onSubmit={handleReopenSubmit}>
            <div style={{ marginBottom: "8px" }}>
              <label htmlFor={`reason-${complaint.id}`}>Reason for reopening:</label>
              <textarea
                id={`reason-${complaint.id}`}
                value={reopenReason}
                onChange={(e) => setReopenReason(e.target.value)}
                placeholder="Explain why issue is unresolved..."
                style={{ width: "100%", padding: "6px", display: "block" }}
              />
            </div>
            {reopenError && <p role="alert" style={{ color: "#c62828" }}>{reopenError}</p>}
            <button
              type="submit"
              disabled={reopenLoading}
              style={{ background: "#d32f2f", color: "white", padding: "6px 12px", border: "none", borderRadius: "4px", marginRight: "8px" }}
            >
              {reopenLoading ? "Reopening..." : "Confirm Reopen"}
            </button>
            <button
              type="button"
              onClick={() => { setShowReopenInput(false); setReopenError(""); }}
              style={{ padding: "6px 12px" }}
            >
              Cancel
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

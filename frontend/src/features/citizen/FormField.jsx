import React from "react";

/**
 * Reusable form field wrapper rendering a label, input/textarea element, and error message.
 */
export default function FormField({ id, label, error, children }) {
  return (
    <div className="form-field">
      <label htmlFor={id}>{label}</label>
      {children}
      {error && <p role="alert">{error}</p>}
    </div>
  );
}

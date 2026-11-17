import React from "react";

/**
 * Component for selecting and previewing an image file.
 * Validates allowed extensions (.jpg, .jpeg, .png) and max size 2 MB.
 */
export default function PhotoPicker({ file, onFileChange, error, onErrorChange }) {
  // Handle file input changes and validation
  function handleFileSelected(event) {
    const selectedFile = event.target.files && event.target.files[0];
    if (!selectedFile) {
      onFileChange(null);
      if (onErrorChange) onErrorChange("");
      return;
    }

    // Check extension
    const allowed = ["image/jpeg", "image/png", "image/jpg"];
    const ext = selectedFile.name.split(".").pop().toLowerCase();
    if (!allowed.includes(selectedFile.type) && !["jpg", "jpeg", "png"].includes(ext)) {
      if (onErrorChange) onErrorChange("Only JPG or PNG images are allowed");
      onFileChange(null);
      return;
    }

    // Check size: 2 MB limit
    if (selectedFile.size > 2 * 1024 * 1024) {
      if (onErrorChange) onErrorChange("Image must be under 2 MB");
      onFileChange(null);
      return;
    }

    // Valid file
    if (onErrorChange) onErrorChange("");
    onFileChange(selectedFile);
  }

  return (
    <div className="form-field photo-picker">
      <label htmlFor="photo">Attach Photo (optional)</label>
      <input
        id="photo"
        name="photo"
        type="file"
        accept=".jpg,.jpeg,.png,image/jpeg,image/png"
        onChange={handleFileSelected}
      />
      {error && <p role="alert">{error}</p>}
      {file && (
        <div className="photo-preview">
          <img
            src={URL.createObjectURL(file)}
            alt="Preview of selected upload"
            style={{ maxWidth: "200px", maxHeight: "200px", marginTop: "10px", borderRadius: "4px" }}
          />
        </div>
      )}
    </div>
  );
}

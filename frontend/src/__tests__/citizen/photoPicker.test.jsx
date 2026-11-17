import React, { useState } from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import PhotoPicker from "../../features/citizen/PhotoPicker";

function PhotoPickerWrapper() {
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  return <PhotoPicker file={file} onFileChange={setFile} error={error} onErrorChange={setError} />;
}

describe("PhotoPicker", () => {
  beforeAll(() => {
    global.URL.createObjectURL = jest.fn(() => "blob:http://localhost/mock-preview");
  });

  afterAll(() => {
    jest.restoreAllMocks();
  });

  test("shows preview when valid image is selected", () => {
    render(<PhotoPickerWrapper />);

    const input = screen.getByLabelText(/attach photo/i);
    const validFile = new File(["dummy content"], "photo.png", { type: "image/png" });
    fireEvent.change(input, { target: { files: [validFile] } });

    expect(screen.getByRole("img", { name: /preview/i })).toBeInTheDocument();
  });

  test("shows error when non-image file is selected", () => {
    render(<PhotoPickerWrapper />);

    const input = screen.getByLabelText(/attach photo/i);
    const textFile = new File(["dummy text"], "document.txt", { type: "text/plain" });
    fireEvent.change(input, { target: { files: [textFile] } });

    expect(screen.getByText("Only JPG or PNG images are allowed")).toBeInTheDocument();
  });

  test("shows error when image exceeds 2 MB", () => {
    render(<PhotoPickerWrapper />);

    const input = screen.getByLabelText(/attach photo/i);
    const largeFile = new File(["a".repeat(2 * 1024 * 1024 + 10)], "large.png", { type: "image/png" });
    Object.defineProperty(largeFile, "size", { value: 2 * 1024 * 1024 + 10 });
    fireEvent.change(input, { target: { files: [largeFile] } });

    expect(screen.getByText("Image must be under 2 MB")).toBeInTheDocument();
  });
});

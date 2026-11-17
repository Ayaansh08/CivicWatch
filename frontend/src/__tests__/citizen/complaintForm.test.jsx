import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import ComplaintForm from "../../features/citizen/ComplaintForm";

// Mock LocationPicker so Leaflet doesn't fail in JSDOM
jest.mock("../../features/citizen/LocationPicker", () => {
  return function MockLocationPicker({ onLocationChange }) {
    return (
      <div data-testid="location-picker">
        <button
          type="button"
          onClick={() => onLocationChange(28.62, 77.36)}
        >
          Mock Pick Location
        </button>
      </div>
    );
  };
});

beforeEach(() => {
  localStorage.setItem("token", "test-token");

  global.fetch = jest.fn((url) => {
    if (url.includes("/categories")) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve([
          { id: 1, name: "Pothole" },
          { id: 2, name: "Garbage" },
        ]),
      });
    }

    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve({ message: "Complaint submitted" }),
    });
  });
});

afterEach(() => {
  jest.clearAllMocks();
  localStorage.clear();
});

async function fillValidForm() {
  await screen.findByRole("option", { name: "Pothole" });

  fireEvent.change(screen.getByLabelText(/title/i), {
    target: { value: "Road damage" },
  });

  fireEvent.change(screen.getByLabelText(/description/i), {
    target: { value: "Large pothole near the market" },
  });

  fireEvent.change(screen.getByLabelText(/category/i), {
    target: { value: "1" },
  });
}

describe("ComplaintForm", () => {
  test("renders all complaint fields", async () => {
    render(<ComplaintForm />);

    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/category/i)).toBeInTheDocument();
    expect(screen.getByTestId("location-picker")).toBeInTheDocument();

    await screen.findByRole("option", { name: "Pothole" });
  });

  test("shows validation errors when submitted empty", async () => {
    render(<ComplaintForm />);

    fireEvent.click(screen.getByRole("button", { name: /submit/i }));

    expect(screen.getByText("Title is required")).toBeInTheDocument();
    expect(screen.getByText("Description is required")).toBeInTheDocument();
    expect(screen.getByText("Please choose a category")).toBeInTheDocument();

    await screen.findByRole("option", { name: "Pothole" });
  });

  test("loads categories from API", async () => {
    render(<ComplaintForm />);

    expect(await screen.findByRole("option", { name: "Pothole" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Garbage" })).toBeInTheDocument();
  });

  test("submits valid complaint with bearer token", async () => {
    render(<ComplaintForm />);
    await fillValidForm();

    fireEvent.click(screen.getByRole("button", { name: /submit/i }));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        "http://localhost:8000/complaints",
        expect.objectContaining({
          method: "POST",
          headers: expect.objectContaining({
            Authorization: "Bearer test-token",
          }),
        })
      );
    });
  });

  test("shows success message after submission", async () => {
    render(<ComplaintForm />);
    await fillValidForm();

    fireEvent.click(screen.getByRole("button", { name: /submit/i }));

    expect(await screen.findByText("Complaint submitted")).toBeInTheDocument();
  });
});

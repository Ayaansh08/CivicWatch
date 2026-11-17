import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "../../App.jsx";
import { TOKEN_KEY } from "../../config";

describe("Citizen report-to-track flow E2E", () => {
  beforeEach(() => {
    localStorage.setItem(TOKEN_KEY, "test-jwt-token");
  });

  afterEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  test("submits complaint on /report and verifies it appears on /my-complaints", async () => {
    const mockCategories = [{ id: 1, name: "Pothole" }];
    const createdComplaint = {
      id: 99,
      title: "Dangerous pothole on Sector 62 road",
      description: "Severe hazard for cyclists.",
      category_id: 1,
      category_name: "Pothole",
      status: "Submitted",
      priority: "Medium",
    };

    global.fetch = jest.fn((url) => {
      if (url.includes("/categories")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockCategories),
        });
      }
      if (url.includes("/complaints/mine")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([createdComplaint]),
        });
      }
      if (url.endsWith("/complaints")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(createdComplaint),
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({}),
      });
    });

    // 1. Render App at /report
    const { unmount } = render(
      <MemoryRouter initialEntries={["/report"]}>
        <App />
      </MemoryRouter>
    );

    // Wait for categories to load
    await screen.findByRole("option", { name: "Pothole" });

    // Fill form
    fireEvent.change(screen.getByLabelText(/title/i), {
      target: { value: "Dangerous pothole on Sector 62 road" },
    });
    fireEvent.change(screen.getByLabelText(/description/i), {
      target: { value: "Severe hazard for cyclists." },
    });
    fireEvent.change(screen.getByLabelText(/category/i), {
      target: { value: "1" },
    });

    // Submit form
    fireEvent.click(screen.getByRole("button", { name: /submit/i }));

    // Expect "Complaint submitted" confirmation
    expect(await screen.findByText("Complaint submitted")).toBeInTheDocument();

    unmount();

    // 2. Render App at /my-complaints
    render(
      <MemoryRouter initialEntries={["/my-complaints"]}>
        <App />
      </MemoryRouter>
    );

    // Verify title and Submitted badge
    expect(await screen.findByText("Dangerous pothole on Sector 62 road")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Dangerous pothole on Sector 62 road" })).toBeInTheDocument();
    expect(screen.getAllByText("Submitted").length).toBeGreaterThan(0);
  });
});

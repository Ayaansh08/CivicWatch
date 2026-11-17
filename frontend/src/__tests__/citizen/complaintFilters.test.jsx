import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import MyComplaints from "../../features/citizen/MyComplaints";
import { TOKEN_KEY } from "../../config";

describe("MyComplaints filters", () => {
  beforeEach(() => {
    localStorage.setItem(TOKEN_KEY, "test-token");
  });

  afterEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  test("filters complaints by status and category and clears filters", async () => {
    const mockCategories = [
      { id: 1, name: "Pothole" },
      { id: 2, name: "Garbage" },
    ];

    global.fetch = jest.fn((url) => {
      if (url.includes("/categories")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockCategories),
        });
      }
      if (url.includes("status=Resolved")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([]),
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve([
          { id: 1, title: "Pothole road", status: "Submitted", category_name: "Pothole" },
        ]),
      });
    });

    render(
      <MemoryRouter>
        <MyComplaints />
      </MemoryRouter>
    );

    expect(await screen.findByText("Pothole road")).toBeInTheDocument();

    // Select status Resolved
    const statusSelect = screen.getByLabelText("Filter by status");
    fireEvent.change(statusSelect, { target: { value: "Resolved" } });

    // Expect empty filter message
    expect(await screen.findByText("No complaints match these filters")).toBeInTheDocument();

    // Clear filters button appears and resets
    const clearBtn = screen.getByRole("button", { name: /clear filters/i });
    fireEvent.click(clearBtn);

    expect(await screen.findByText("Pothole road")).toBeInTheDocument();
  });
});

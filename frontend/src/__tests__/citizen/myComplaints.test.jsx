import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import MyComplaints from "../../features/citizen/MyComplaints";
import { TOKEN_KEY } from "../../config";

describe("MyComplaints component", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  test("shows please log in message when no token is present", () => {
    render(
      <MemoryRouter>
        <MyComplaints />
      </MemoryRouter>
    );

    expect(screen.getByText("Please log in to continue")).toBeInTheDocument();
  });

  test("shows empty state when complaints list is empty", async () => {
    localStorage.setItem(TOKEN_KEY, "test-token");
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve([]),
      })
    );

    render(
      <MemoryRouter>
        <MyComplaints />
      </MemoryRouter>
    );

    expect(await screen.findByText("No complaints yet")).toBeInTheDocument();
  });

  test("shows error message when fetch fails", async () => {
    localStorage.setItem(TOKEN_KEY, "test-token");
    global.fetch = jest.fn(() => Promise.reject(new Error("Network failed")));

    render(
      <MemoryRouter>
        <MyComplaints />
      </MemoryRouter>
    );

    expect(await screen.findByText("Could not load complaints")).toBeInTheDocument();
  });

  test("renders complaint badge and timeline order when clicked", async () => {
    localStorage.setItem(TOKEN_KEY, "test-token");
    const mockComplaints = [
      {
        id: 10,
        title: "Broken Bench in Park",
        description: "Wooden bench broken.",
        category_name: "Parks",
        status: "In Progress",
        priority: "Low",
        photo_path: "/uploads/bench.png",
      },
    ];

    const mockHistory = [
      { id: 1, status: "Submitted", note: "First created", changed_at: "2026-11-17T10:00:00Z" },
      { id: 2, status: "In Progress", note: "Assigned to worker", changed_at: "2026-11-17T11:00:00Z" },
    ];

    global.fetch = jest.fn((url) => {
      if (url.includes("/history")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockHistory),
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockComplaints),
      });
    });

    render(
      <MemoryRouter>
        <MyComplaints />
      </MemoryRouter>
    );

    expect(await screen.findByText("Broken Bench in Park")).toBeInTheDocument();
    expect(screen.getByText("In Progress")).toBeInTheDocument();

    // Click complaint card to load timeline
    fireEvent.click(screen.getByText("Broken Bench in Park"));

    expect(await screen.findByText("Status Timeline")).toBeInTheDocument();
    expect(screen.getByText("First created")).toBeInTheDocument();
    expect(screen.getByText("Assigned to worker")).toBeInTheDocument();
  });
});

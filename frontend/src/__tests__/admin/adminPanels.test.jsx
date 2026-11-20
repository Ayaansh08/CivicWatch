import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import DepartmentsPanel from "../../features/admin/DepartmentsPanel";
import OfficersPanel from "../../features/admin/OfficersPanel";
import { TOKEN_KEY } from "../../config";

/** Paginated response helper for mocking the departments API. */
function deptPage(items, page = 1, totalPages = 1) {
  return { items, total: items.length, page, size: 20, pages: totalPages };
}

/** Paginated response helper for mocking the officers API. */
function officerPage(items, page = 1, totalPages = 1) {
  return { items, total: items.length, page, size: 20, pages: totalPages };
}

/** Seed a fake token so admin API calls include an Authorization header. */
beforeEach(() => {
  global.fetch = jest.fn();
  localStorage.setItem(TOKEN_KEY, "admin-token");
});

afterEach(() => {
  jest.clearAllMocks();
  localStorage.clear();
});

describe("DepartmentsPanel", () => {
  test("shows the list of departments fetched from the API", async () => {
    // Return two departments on the first GET
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve(
          deptPage([
            { id: 1, name: "Water" },
            { id: 2, name: "Roads" },
          ])
        ),
    });

    render(
      <MemoryRouter>
        <DepartmentsPanel />
      </MemoryRouter>
    );

    // Wait for the departments to appear
    expect(await screen.findByText("Water")).toBeInTheDocument();
    expect(screen.getByText("Roads")).toBeInTheDocument();
  });

  test("shows No departments yet when the list is empty", async () => {
    // Return an empty list
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(deptPage([])),
    });

    render(
      <MemoryRouter>
        <DepartmentsPanel />
      </MemoryRouter>
    );

    expect(await screen.findByText("No departments yet")).toBeInTheDocument();
  });

  test("adding a department calls POST and refreshes the list", async () => {
    // First GET returns empty, POST creates the dept, second GET returns it
    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(deptPage([])),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ id: 1, name: "Parks" }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(deptPage([{ id: 1, name: "Parks" }])),
      });

    render(
      <MemoryRouter>
        <DepartmentsPanel />
      </MemoryRouter>
    );

    // Wait for initial load, then type a name and submit
    await screen.findByText("No departments yet");
    fireEvent.change(screen.getByPlaceholderText("Department name"), {
      target: { value: "Parks" },
    });
    fireEvent.click(screen.getByText("Add"));

    // After the POST, the list should reload and show Parks
    expect(await screen.findByText("Parks")).toBeInTheDocument();
    // Verify POST was called
    const postCall = global.fetch.mock.calls[1];
    expect(postCall[1].method).toBe("POST");
  });

  test("delete asks for confirmation before calling DELETE", async () => {
    // Return one department and mock a successful delete followed by empty list
    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(deptPage([{ id: 1, name: "Water" }])),
      })
      .mockResolvedValueOnce({ ok: true })   // DELETE
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(deptPage([])),
      });

    // Mock window.confirm to return true (user confirms deletion)
    window.confirm = jest.fn(() => true);

    render(
      <MemoryRouter>
        <DepartmentsPanel />
      </MemoryRouter>
    );

    // Wait for the dept to load, then click Delete
    await screen.findByText("Water");
    fireEvent.click(screen.getByText("Delete"));

    // confirm() should have been called once
    expect(window.confirm).toHaveBeenCalledTimes(1);
    // After deletion the list should be empty
    expect(await screen.findByText("No departments yet")).toBeInTheDocument();
  });

  test("shows API error message when adding a department fails", async () => {
    // First GET returns empty list
    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(deptPage([])),
      })
      // POST returns a 400 error
      .mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ detail: "Department name already exists" }),
      });

    render(
      <MemoryRouter>
        <DepartmentsPanel />
      </MemoryRouter>
    );

    await screen.findByText("No departments yet");
    fireEvent.change(screen.getByPlaceholderText("Department name"), {
      target: { value: "Water" },
    });
    fireEvent.click(screen.getByText("Add"));

    // Expect the API error message to appear
    expect(
      await screen.findByText("Department name already exists")
    ).toBeInTheDocument();
  });

  test("Next button requests page 2 from the API", async () => {
    // First GET returns page 1 with totalPages=2
    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve(
            deptPage([{ id: 1, name: "Alpha" }], 1, 2)
          ),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve(
            deptPage([{ id: 2, name: "Beta" }], 2, 2)
          ),
      });

    render(
      <MemoryRouter>
        <DepartmentsPanel />
      </MemoryRouter>
    );

    // Wait for page 1 to load, then click Next
    await screen.findByText("Alpha");
    fireEvent.click(screen.getByText("Next"));

    // Page 2 should be loaded from the API
    expect(await screen.findByText("Beta")).toBeInTheDocument();
    // The second fetch should have included page=2 in the URL
    const secondUrl = global.fetch.mock.calls[1][0];
    expect(secondUrl).toContain("page=2");
  });
});

describe("OfficersPanel", () => {
  test("shows the list of officers fetched from the API", async () => {
    // Return one officer from the GET
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve(
          officerPage([{ id: 1, name: "Raj Kumar", email: "raj@civicwatch.com" }])
        ),
    });

    render(
      <MemoryRouter>
        <OfficersPanel />
      </MemoryRouter>
    );

    expect(await screen.findByText("Raj Kumar")).toBeInTheDocument();
  });

  test("shows No officers yet when the officer list is empty", async () => {
    // Return an empty list
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(officerPage([])),
    });

    render(
      <MemoryRouter>
        <OfficersPanel />
      </MemoryRouter>
    );

    expect(await screen.findByText("No officers yet")).toBeInTheDocument();
  });

  test("officer form shows an error when password is too short", async () => {
    // Return empty list on initial load
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(officerPage([])),
    });

    render(
      <MemoryRouter>
        <OfficersPanel />
      </MemoryRouter>
    );

    await screen.findByText("No officers yet");
    // Type a 3-character password and submit
    fireEvent.change(screen.getByPlaceholderText(/full name/i), {
      target: { value: "New Officer" },
    });
    fireEvent.change(screen.getByPlaceholderText(/email/i), {
      target: { value: "new@civicwatch.com" },
    });
    fireEvent.change(screen.getByPlaceholderText(/password/i), {
      target: { value: "abc" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Create Officer" }));

    // Expect the password validation message
    expect(
      screen.getByText("Password must be at least 6 characters")
    ).toBeInTheDocument();
  });
});

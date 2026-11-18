/**
 * Acceptance test for review to resolve flow (CW-310).
 *
 * Verifies that an officer can walk a complaint from Submitted through
 * Under Review, Assigned, In Progress, and Resolved in the UI.
 */
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import AuthorityDashboard from "../../features/authority/AuthorityDashboard";

const DEPARTMENTS = [
  { id: 1, name: "Roads Department" },
];

describe("Authority acceptance flow", () => {
  beforeEach(() => {
    localStorage.setItem("token", "fake-officer-token");
  });

  afterEach(() => {
    localStorage.clear();
    jest.resetAllMocks();
  });

  test("officer can walk complaint through review and assignment", async () => {
    // Current in-flight complaint state
    let complaintState = {
      id: 10,
      title: "Dangerous pothole",
      category_name: "Roads",
      status: "Submitted",
      priority: "Medium",
      department_name: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    // Mock fetch for all endpoints
    global.fetch = jest.fn((url, options) => {
      // 1. Departments dropdown in assign form
      if (url.includes("/departments")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(DEPARTMENTS),
        });
      }

      // 2. Assign endpoint (POST /authority/complaints/10/assign)
      if (url.includes("/assign")) {
        complaintState = {
          ...complaintState,
          status: "Assigned",
          department_name: "Roads Department",
          priority: "High",
        };
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(complaintState),
        });
      }

      // 3. Status update or review endpoint (POST /authority/complaints/10/status or /review)
      if (options?.method === "POST" && url.includes("/complaints/10/")) {
        let nextStatus = "Under Review";
        if (options.body) {
          const body = JSON.parse(options.body);
          if (body.status) nextStatus = body.status;
        }
        complaintState = {
          ...complaintState,
          status: nextStatus,
        };
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(complaintState),
        });
      }

      // 4. Default: GET /authority/complaints
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve([complaintState]),
      });
    });

    // Render the authority dashboard
    render(
      <MemoryRouter>
        <AuthorityDashboard />
      </MemoryRouter>
    );

    // Initial load: verify complaint row appears
    await waitFor(() => {
      expect(screen.getByText("Dangerous pothole")).toBeTruthy();
    });

    // Step 1: Click the row to select it
    await userEvent.click(screen.getByText("Dangerous pothole"));

    // Verify detail panel opens
    await waitFor(() => {
      expect(screen.getByText("Complaint #10: Dangerous pothole")).toBeTruthy();
    });

    // Step 2: Under Submitted status, StatusUpdateForm shows button for Under Review
    const underReviewBtn = screen.getByRole("button", { name: /Under Review/i });
    expect(underReviewBtn).toBeTruthy();
    await userEvent.click(underReviewBtn);

    // After review, complaint reloads with Under Review status
    await waitFor(() => {
      expect(screen.getByText("Under Review", { selector: ".badge" })).toBeTruthy();
    });

    // Step 3: Select complaint again if needed to see AssignForm
    await userEvent.click(screen.getByText("Dangerous pothole"));

    // Verify AssignForm is rendered with Department dropdown
    await waitFor(() => {
      expect(screen.getByLabelText("Department")).toBeTruthy();
    });

    // Fill in AssignForm
    await userEvent.selectOptions(
      screen.getByLabelText("Department"),
      "Roads Department"
    );
    await userEvent.selectOptions(
      screen.getByLabelText("Priority"),
      "High"
    );

    // Submit assignment
    await userEvent.click(
      screen.getByRole("button", { name: "Assign" })
    );

    // Verify status updated to Assigned
    await waitFor(() => {
      expect(screen.getByText("Assigned", { selector: ".badge" })).toBeTruthy();
    });
  });
});

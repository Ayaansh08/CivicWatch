/**
 * Tests for AssignForm component (CW-305).
 */
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import AssignForm from "../../features/authority/AssignForm";

const FAKE_DEPARTMENTS = [
  { id: 1, name: "Roads Department" },
  { id: 2, name: "Water Department" },
];

beforeEach(() => {
  localStorage.setItem("token", "fake-jwt-token");
  global.fetch = jest.fn((url) => {
    // Return departments for the GET request, success for POST
    if (url.includes("/departments")) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(FAKE_DEPARTMENTS),
      });
    }
    return Promise.resolve({
      ok: true,
      json: () =>
        Promise.resolve({ id: 1, status: "Assigned", department_id: 1, priority: "High" }),
    });
  });
});

afterEach(() => {
  localStorage.clear();
  jest.resetAllMocks();
});

test("assign form renders department options from API", async () => {
  render(<AssignForm complaintId={1} />);
  await waitFor(() => {
    expect(screen.getByText("Roads Department")).toBeTruthy();
  });
});

test("assign form submits department and priority to the API", async () => {
  const onSuccess = jest.fn();
  render(<AssignForm complaintId={1} onSuccess={onSuccess} />);
  await waitFor(() => screen.getByText("Roads Department"));

  // Select a department
  await userEvent.selectOptions(
    screen.getByLabelText("Department"),
    "Roads Department"
  );
  // Select a priority (defaults to Medium, choose High)
  await userEvent.selectOptions(screen.getByLabelText("Priority"), "High");
  // Submit
  await userEvent.click(screen.getByText("Assign"));

  await waitFor(() => {
    // onSuccess callback should have been called after successful submission
    expect(onSuccess).toHaveBeenCalled();
  });
});

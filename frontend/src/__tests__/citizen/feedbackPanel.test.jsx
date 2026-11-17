import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import FeedbackPanel from "../../features/citizen/FeedbackPanel";

describe("FeedbackPanel component", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test("does not render if complaint is not Resolved", () => {
    const complaint = { id: 1, status: "In Progress" };
    const { container } = render(<FeedbackPanel complaint={complaint} />);
    expect(container.firstChild).toBeNull();
  });

  test("renders feedback and reopen buttons when Resolved and submits feedback", async () => {
    const complaint = { id: 1, status: "Resolved", rating: null };
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ message: "Thank you for your feedback" }),
      })
    );

    const onUpdate = jest.fn();
    render(<FeedbackPanel complaint={complaint} onComplaintUpdated={onUpdate} />);

    expect(screen.getByText("Resolution Feedback & Actions")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /submit feedback/i })).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /submit feedback/i }));

    await waitFor(() => {
      expect(screen.getByText("Thank you for your feedback")).toBeInTheDocument();
    });
  });

  test("validates reopen reason requiring non-empty input", () => {
    const complaint = { id: 1, status: "Resolved", rating: 5 };
    render(<FeedbackPanel complaint={complaint} />);

    // Click Reopen button to show form
    fireEvent.click(screen.getByRole("button", { name: /reopen complaint/i }));

    // Submit empty reason
    fireEvent.click(screen.getByRole("button", { name: /confirm reopen/i }));
    expect(screen.getByText("Please give a reason")).toBeInTheDocument();
  });
});

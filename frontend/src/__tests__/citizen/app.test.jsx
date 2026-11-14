import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "../../App.jsx";

describe("CivicWatch application", () => {
  test("renders the CivicWatch home page", () => {
    render(
      <MemoryRouter initialEntries={["/"]}>
        <App />
      </MemoryRouter>
    );

    expect(
      screen.getByRole("heading", { name: "CivicWatch" })
    ).toBeInTheDocument();
  });
});

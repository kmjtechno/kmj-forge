import { render, screen, within } from "@testing-library/react";
import { describe, expect, test } from "vitest";
import App from "../src/App";

describe("Forge Desktop Alpha workspace", () => {
  test("renders the primary engineering panels", () => {
    render(<App />);
    for (const name of ["Project", "Task", "Plan", "Timeline", "Diff", "Terminal", "Tests", "Approvals"]) {
      expect(screen.getByRole("region", { name })).toBeInTheDocument();
    }
  });

  test("keeps routing, context, state and evidence status visible", () => {
    render(<App />);
    const status = screen.getByRole("region", { name: "Agent status" });
    expect(within(status).getByText("FREE_ONLY")).toBeInTheDocument();
    expect(within(status).getByText(/Model/i)).toBeInTheDocument();
    expect(within(status).getByText(/Context/i)).toBeInTheDocument();
    expect(within(status).getByText(/State/i)).toBeInTheDocument();
    expect(within(status).getByText(/Evidence/i)).toBeInTheDocument();
  });

  test("provides project and task inputs without hiding approval state", () => {
    render(<App />);
    expect(screen.getByLabelText("Project path")).toBeInTheDocument();
    expect(screen.getByLabelText("Task objective")).toBeInTheDocument();
    const approvals = screen.getByRole("region", { name: "Approvals" });
    expect(within(approvals).getByText(/Write/i)).toBeInTheDocument();
    expect(within(approvals).getByText(/Terminal/i)).toBeInTheDocument();
    expect(within(approvals).getByText(/Git/i)).toBeInTheDocument();
  });
});

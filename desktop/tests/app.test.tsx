import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";
import App from "../src/App";

function renderAppWithRequest(
  request: (operation: string, payload: Record<string, unknown>) => Promise<unknown>,
) {
  const bridge = {
    request: async (operation: string, payload: Record<string, unknown>) => ({
      protocol_version: "1.0",
      ok: true,
      result: await request(operation, payload),
    }),
  };
  render(<App {...({ bridge } as any)} />);
}

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
    expect(within(status).getByText(/Fallback/i)).toBeInTheDocument();
    expect(within(status).getByText(/Context/i)).toBeInTheDocument();
    expect(within(status).getByText(/State/i)).toBeInTheDocument();
    expect(within(status).getByText(/Evidence/i)).toBeInTheDocument();
  });

  test("provides project and task inputs without hiding approval state", () => {
    render(<App />);
    expect(screen.getByLabelText("Project path")).toBeInTheDocument();
    expect(screen.getByLabelText("Task objective")).toBeInTheDocument();
    const approvals = screen.getByRole("region", { name: "Approvals" });
    expect(within(approvals).getByText("Write — Pending")).toBeInTheDocument();
    expect(within(approvals).getByText("Terminal — Pending")).toBeInTheDocument();
    expect(within(approvals).getByText("Git — Pending")).toBeInTheDocument();
  });

  test("inspects a repository through the Forge bridge and renders context evidence", async () => {
    const request = vi.fn(async (operation: string) => {
      if (operation !== "inspect_repository") throw new Error(`unexpected operation ${operation}`);
      return {
        repository: { root: "/repo", file_count: 12, skipped_files: 1 },
        detection: {
          languages: ["Python", "TypeScript"],
          build_systems: ["pyproject"],
          test_commands: ["python -m unittest"],
        },
        context: {
          relevant_files: ["src/a.py", "tests/test_a.py"],
          symbols: ["run"],
          total_characters: 900,
          naive_characters: 4000,
        },
      };
    });
    renderAppWithRequest(request);

    fireEvent.change(screen.getByLabelText("Project path"), { target: { value: "/repo" } });
    fireEvent.change(screen.getByLabelText("Task objective"), { target: { value: "Fix repository tests" } });
    fireEvent.click(screen.getByRole("button", { name: "Inspect Project" }));

    await waitFor(() =>
      expect(request).toHaveBeenCalledWith(
        "inspect_repository",
        expect.objectContaining({ path: "/repo", objective: "Fix repository tests" }),
      ),
    );
    const project = screen.getByRole("region", { name: "Project" });
    expect(await within(project).findByText(/12 files/i)).toBeInTheDocument();
    expect(within(project).getByText(/Python, TypeScript/i)).toBeInTheDocument();
    expect(within(project).getByText(/src\/a\.py/)).toBeInTheDocument();
    const status = screen.getByRole("region", { name: "Agent status" });
    expect(within(status).getByText(/900 \/ 4000/i)).toBeInTheDocument();
  });

  test("creates and refreshes a persisted Forge run through the bridge", async () => {
    const request = vi.fn(async (operation: string) => {
      if (operation === "run_create") {
        return {
          run_id: "run-42",
          task_id: "desktop-task",
          objective: "Implement alpha",
          state: "planning",
          history: ["planning"],
          approvals: [],
          evidence_count: 1,
        };
      }
      if (operation === "run_status") {
        return {
          run_id: "run-42",
          task_id: "desktop-task",
          objective: "Implement alpha",
          state: "testing",
          history: ["planning", "testing"],
          approvals: [],
          evidence_count: 3,
        };
      }
      throw new Error(`unexpected operation ${operation}`);
    });
    renderAppWithRequest(request);

    fireEvent.change(screen.getByLabelText("Project path"), { target: { value: "/repo" } });
    fireEvent.change(screen.getByLabelText("Task objective"), { target: { value: "Implement alpha" } });
    fireEvent.click(screen.getByRole("button", { name: "Create Run" }));

    await waitFor(() =>
      expect(request).toHaveBeenCalledWith(
        "run_create",
        expect.objectContaining({ objective: "Implement alpha", state_dir: "/repo/.kmj-forge" }),
      ),
    );
    expect(await screen.findByText("run-42")).toBeInTheDocument();
    let status = screen.getByRole("region", { name: "Agent status" });
    expect(within(status).getByText("planning")).toBeInTheDocument();
    expect(within(status).getByText("1")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Refresh Run" }));
    await waitFor(() =>
      expect(request).toHaveBeenCalledWith("run_status", {
        state_dir: "/repo/.kmj-forge",
        run_id: "run-42",
      }),
    );
    status = screen.getByRole("region", { name: "Agent status" });
    expect(await within(status).findByText("testing")).toBeInTheDocument();
    expect(within(status).getByText("3")).toBeInTheDocument();
  });

  test("clears repository-bound run state when the project path changes", async () => {
    const request = vi.fn(async (operation: string) => {
      if (operation !== "run_create") throw new Error(`unexpected operation ${operation}`);
      return {
        run_id: "run-old-project",
        task_id: "desktop-task",
        objective: "Safe change",
        state: "receive",
        history: ["receive"],
        approvals: [],
        evidence_count: 0,
      };
    });
    renderAppWithRequest(request);

    fireEvent.change(screen.getByLabelText("Project path"), { target: { value: "/repo-a" } });
    fireEvent.change(screen.getByLabelText("Task objective"), { target: { value: "Safe change" } });
    fireEvent.click(screen.getByRole("button", { name: "Create Run" }));
    expect(await screen.findByText("run-old-project")).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Project path"), { target: { value: "/repo-b" } });

    expect(screen.queryByText("run-old-project")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Refresh Run" })).toBeDisabled();
  });

  test("limits explicit approvals to Forge Engine protected action classifications", async () => {
    const request = vi.fn(async (operation: string) => {
      if (operation === "run_create") {
        return {
          run_id: "run-7",
          task_id: "desktop-task",
          objective: "Safe change",
          state: "awaiting_approval",
          history: ["planning", "awaiting_approval"],
          approvals: [],
          evidence_count: 1,
        };
      }
      if (operation === "run_approve") {
        return {
          run_id: "run-7",
          task_id: "desktop-task",
          objective: "Safe change",
          state: "awaiting_approval",
          history: ["planning", "awaiting_approval"],
          approvals: ["write"],
          evidence_count: 1,
        };
      }
      throw new Error(`unexpected operation ${operation}`);
    });
    renderAppWithRequest(request);

    const approvalControl = screen.getByLabelText("Approval action");
    expect(approvalControl.tagName).toBe("SELECT");
    expect(within(approvalControl).getByRole("option", { name: "Write files" })).toHaveValue("write");
    expect(within(approvalControl).getByRole("option", { name: "Run terminal commands" })).toHaveValue("terminal");
    expect(within(approvalControl).getByRole("option", { name: "Git changes" })).toHaveValue("git");

    fireEvent.change(screen.getByLabelText("Project path"), { target: { value: "/repo" } });
    fireEvent.change(screen.getByLabelText("Task objective"), { target: { value: "Safe change" } });
    fireEvent.click(screen.getByRole("button", { name: "Create Run" }));
    expect(await screen.findByText("run-7")).toBeInTheDocument();

    fireEvent.change(approvalControl, { target: { value: "write" } });
    fireEvent.click(screen.getByRole("button", { name: "Approve Action" }));

    await waitFor(() =>
      expect(request).toHaveBeenCalledWith("run_approve", {
        state_dir: "/repo/.kmj-forge",
        run_id: "run-7",
        action: "write",
      }),
    );
    expect(await screen.findByText("write")).toBeInTheDocument();
  });
});

import { invoke } from "@tauri-apps/api/core";
import { useMemo, useState, type ReactNode } from "react";
import { createForgeBridge } from "./bridge";

const defaultBridge = createForgeBridge(invoke);
type ForgeBridge = ReturnType<typeof createForgeBridge>;

interface RepositoryInspection {
  repository: { root: string; file_count: number; skipped_files: number };
  detection: { languages: string[]; build_systems: string[]; test_commands: string[] };
  context: {
    relevant_files: string[];
    symbols: string[];
    total_characters: number;
    naive_characters: number;
  };
}

interface RunSummary {
  run_id: string;
  task_id: string;
  objective: string;
  state: string;
  history: string[];
  approvals: string[];
  evidence_count: number;
}

const defaultPlan = ["Classify task", "Discover repository context", "Propose verified change"];
const defaultTimeline = ["Run ready", "Awaiting task"];
const defaultApprovals = ["Write — Pending", "Terminal — Pending", "Git — Pending"];
const protectedApprovalOptions = [
  { value: "write", label: "Write files" },
  { value: "terminal", label: "Run terminal commands" },
  { value: "git", label: "Git changes" },
] as const;

function Panel({ name, children, className = "" }: { name: string; children: ReactNode; className?: string }) {
  return (
    <section className={`panel ${className}`} aria-label={name}>
      <header className="panel-heading">
        <span>{name}</span>
        <span className="panel-dot" aria-hidden="true" />
      </header>
      <div className="panel-body">{children}</div>
    </section>
  );
}

function stateDirectory(projectPath: string) {
  const root = projectPath.trim().replace(/[\\/]+$/, "");
  return root ? `${root}/.kmj-forge` : "";
}

function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : String(error);
}

export default function App({ bridge = defaultBridge }: { bridge?: ForgeBridge }) {
  const [projectPath, setProjectPath] = useState("");
  const [objective, setObjective] = useState("");
  const [inspection, setInspection] = useState<RepositoryInspection | null>(null);
  const [run, setRun] = useState<RunSummary | null>(null);
  const [approvalAction, setApprovalAction] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const stateDir = useMemo(() => stateDirectory(projectPath), [projectPath]);
  const canStart = Boolean(projectPath.trim() && objective.trim());

  function changeProjectPath(nextPath: string) {
    if (nextPath !== projectPath) {
      setInspection(null);
      setRun(null);
      setApprovalAction("");
      setError(null);
    }
    setProjectPath(nextPath);
  }

  async function inspectProject() {
    if (!canStart) return;
    setBusy("inspect");
    setError(null);
    try {
      const response = await bridge.request<RepositoryInspection>("inspect_repository", {
        path: projectPath.trim(),
        objective: objective.trim(),
        task_id: "desktop-inspect",
        character_budget: 32_000,
      });
      setInspection(response.result);
    } catch (cause) {
      setError(errorMessage(cause));
    } finally {
      setBusy(null);
    }
  }

  async function createRun() {
    if (!canStart || !stateDir) return;
    setBusy("create");
    setError(null);
    try {
      const response = await bridge.request<RunSummary>("run_create", {
        task_id: "desktop-task",
        objective: objective.trim(),
        state_dir: stateDir,
      });
      setRun(response.result);
    } catch (cause) {
      setError(errorMessage(cause));
    } finally {
      setBusy(null);
    }
  }

  async function refreshRun() {
    if (!run || !stateDir) return;
    setBusy("refresh");
    setError(null);
    try {
      const response = await bridge.request<RunSummary>("run_status", {
        state_dir: stateDir,
        run_id: run.run_id,
      });
      setRun(response.result);
    } catch (cause) {
      setError(errorMessage(cause));
    } finally {
      setBusy(null);
    }
  }

  async function approveAction() {
    const action = approvalAction.trim();
    if (!run || !stateDir || !action) return;
    setBusy("approve");
    setError(null);
    try {
      const response = await bridge.request<RunSummary>("run_approve", {
        state_dir: stateDir,
        run_id: run.run_id,
        action,
      });
      setRun(response.result);
      setApprovalAction("");
    } catch (cause) {
      setError(errorMessage(cause));
    } finally {
      setBusy(null);
    }
  }

  const timeline = run?.history?.length ? run.history : defaultTimeline;
  const approvals = run?.approvals?.length ? run.approvals : defaultApprovals;
  const contextStatus = inspection
    ? `${inspection.context.total_characters} / ${inspection.context.naive_characters} chars`
    : "0 / 32k";

  return (
    <main className="forge-app">
      <header className="topbar">
        <div className="brand"><strong>KMJ FORGE</strong><span>Desktop Alpha</span></div>
        <section className="agent-status" aria-label="Agent status">
          <span><small>Policy</small><strong>FREE_ONLY</strong></span>
          <span><small>Model</small><strong>Not selected</strong></span>
          <span><small>Context</small><strong>{contextStatus}</strong></span>
          <span><small>State</small><strong>{run?.state ?? "RECEIVE"}</strong></span>
          <span><small>Evidence</small><strong>{run?.evidence_count ?? 0}</strong></span>
          <span><small>Bridge</small><strong>{busy ? "BUSY" : "READY"}</strong></span>
        </section>
      </header>

      {error ? <div className="error-banner" role="alert">{error}</div> : null}

      <div className="workspace-grid">
        <aside className="left-rail">
          <Panel name="Project">
            <label className="field">
              Project path
              <input
                aria-label="Project path"
                placeholder="Open a repository…"
                value={projectPath}
                onChange={(event) => changeProjectPath(event.target.value)}
              />
            </label>
            <div className="panel-actions">
              <button type="button" onClick={inspectProject} disabled={!canStart || busy !== null}>Inspect Project</button>
            </div>
            {inspection ? (
              <div className="project-summary">
                <strong>{inspection.repository.file_count} files</strong>
                <span>{inspection.repository.skipped_files} skipped</span>
                <span>{inspection.detection.languages.length ? inspection.detection.languages.join(", ") : "Language unknown"}</span>
                <span>{inspection.detection.build_systems.length ? inspection.detection.build_systems.join(", ") : "Build system unknown"}</span>
                <ul className="file-list">
                  {inspection.context.relevant_files.map((file) => <li key={file} className="code">{file}</li>)}
                </ul>
              </div>
            ) : (
              <div className="empty-state">Repository evidence appears here after Forge scans the project.</div>
            )}
          </Panel>
        </aside>

        <div className="center-stack">
          <Panel name="Task">
            <label className="field">
              Task objective
              <textarea
                aria-label="Task objective"
                placeholder="Describe the engineering outcome…"
                rows={3}
                value={objective}
                onChange={(event) => setObjective(event.target.value)}
              />
            </label>
            <div className="panel-actions">
              <button type="button" onClick={createRun} disabled={!canStart || busy !== null}>Create Run</button>
              <button type="button" onClick={refreshRun} disabled={!run || busy !== null}>Refresh Run</button>
            </div>
            {run ? (
              <div className="run-summary">
                <span>Run</span><strong className="code">{run.run_id}</strong>
                <span>Task</span><strong className="code">{run.task_id}</strong>
              </div>
            ) : null}
          </Panel>
          <Panel name="Plan">
            <ol className="step-list">{defaultPlan.map((item, index) => <li key={item}><span>{index + 1}</span>{item}</li>)}</ol>
          </Panel>
          <Panel name="Diff" className="diff-panel">
            <div className="empty-state code">No proposed changes yet. Forge engine remains the source of truth for edits and evidence.</div>
          </Panel>
          <div className="bottom-grid">
            <Panel name="Terminal">
              <div className="terminal">$ {busy ? `Forge bridge: ${busy}…` : run ? `Run ${run.run_id} · ${run.state}` : "Forge bridge ready."}</div>
            </Panel>
            <Panel name="Tests">
              <div className="verification-summary">
                <strong>{run?.evidence_count ?? 0}</strong>
                <span>Evidence records</span>
                {inspection?.detection.test_commands.map((command) => <code key={command}>{command}</code>)}
              </div>
            </Panel>
          </div>
        </div>

        <aside className="right-rail">
          <Panel name="Timeline">
            <ul className="timeline">{timeline.map((item, index) => <li key={`${item}-${index}`}>{item}</li>)}</ul>
          </Panel>
          <Panel name="Approvals">
            <ul className="approval-list">
              {approvals.map((item) => <li key={item} className={run?.approvals.includes(item) ? "approved" : ""}>{item}</li>)}
            </ul>
            <label className="field approval-field">
              Approval action
              <select
                aria-label="Approval action"
                value={approvalAction}
                onChange={(event) => setApprovalAction(event.target.value)}
              >
                <option value="">Choose protected action…</option>
                {protectedApprovalOptions.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </label>
            <div className="panel-actions">
              <button type="button" onClick={approveAction} disabled={!run || !approvalAction || busy !== null}>Approve Action</button>
            </div>
          </Panel>
        </aside>
      </div>
    </main>
  );
}

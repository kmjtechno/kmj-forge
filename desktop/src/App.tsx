import type { ReactNode } from "react";

const panels = {
  plan: ["Classify task", "Discover repository context", "Propose verified change"],
  timeline: ["Run ready", "Awaiting task"],
  approvals: ["Write — Pending", "Terminal — Pending", "Git — Pending"],
};

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

export default function App() {
  return (
    <main className="forge-app">
      <header className="topbar">
        <div className="brand"><strong>KMJ FORGE</strong><span>Desktop Alpha</span></div>
        <section className="agent-status" aria-label="Agent status">
          <span><small>Policy</small><strong>FREE_ONLY</strong></span>
          <span><small>Model</small><strong>Not selected</strong></span>
          <span><small>Context</small><strong>0 / 32k</strong></span>
          <span><small>State</small><strong>RECEIVE</strong></span>
          <span><small>Evidence</small><strong>0</strong></span>
        </section>
      </header>

      <div className="workspace-grid">
        <aside className="left-rail">
          <Panel name="Project">
            <label className="field">Project path<input aria-label="Project path" placeholder="Open a repository…" /></label>
            <div className="empty-state">Repository tree appears here after Forge scans the project.</div>
          </Panel>
        </aside>

        <div className="center-stack">
          <Panel name="Task">
            <label className="field">Task objective<textarea aria-label="Task objective" placeholder="Describe the engineering outcome…" rows={3} /></label>
          </Panel>
          <Panel name="Plan">
            <ol className="step-list">{panels.plan.map((item, index) => <li key={item}><span>{index + 1}</span>{item}</li>)}</ol>
          </Panel>
          <Panel name="Diff" className="diff-panel">
            <div className="empty-state code">No proposed changes yet.</div>
          </Panel>
          <div className="bottom-grid">
            <Panel name="Terminal"><div className="terminal">$ Forge terminal output will appear here.</div></Panel>
            <Panel name="Tests"><div className="empty-state">No verification evidence yet.</div></Panel>
          </div>
        </div>

        <aside className="right-rail">
          <Panel name="Timeline">
            <ul className="timeline">{panels.timeline.map((item) => <li key={item}>{item}</li>)}</ul>
          </Panel>
          <Panel name="Approvals">
            <ul className="approval-list">{panels.approvals.map((item) => <li key={item}>{item}</li>)}</ul>
          </Panel>
        </aside>
      </div>
    </main>
  );
}

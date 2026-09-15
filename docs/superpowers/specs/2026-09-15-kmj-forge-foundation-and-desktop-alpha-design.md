# KMJ Forge Foundation and Desktop Alpha Design

## Status
Approved architecture captured on 2026-09-15 for implementation.

## Product boundary
KMJ Forge is a completely separate KMJ TECHNO project.
It must not contain KMJ Calibration Pro, KMJ Cloud Nexus, or other product-specific code.
Other KMJ products may consume Forge through public contracts, adapters, skills, or tooling only.
The canonical repository is `kmjtechno/kmj-forge`, public, Apache-2.0.

## Objective
Build a reusable open-source software-engineering framework and a first working desktop AI coding-agent experience on the same Forge engine.
The first usable vertical slice must open a repository, understand its structure, select an eligible free/local model, assemble compact task context, propose edits, run verification, and show evidence.

## Architecture
The Python package under `src/kmj_forge/` remains the headless core and CLI surface.
The desktop application is an official Forge client, not a separate AI engine.
Core intelligence is split into small contracts: protocol, repository intelligence, context compilation, model registry/router, tools, permissions, verification, and audit records.
Provider-specific behavior lives only behind adapters.

## Desktop direction
Use Tauri 2 + React + TypeScript for the desktop shell and keep Python orchestration in Forge core.
The desktop shell communicates through a versioned local protocol so future VS Code/JetBrains integrations can reuse the same engine.
Initial panels: Project, Task, Plan, Agent Timeline, Diff, Terminal, Tests, Reviews, Security, Memory, Approvals.

## Free/local model policy
Local models are first-class and cloud providers are optional adapters.
A dynamic capability registry records provider, model id, availability, pricing, context window, tool use, vision, structured output, latency, and health.
`FREE_ONLY` mode must never silently route to a paid model.
If no eligible model exists, Forge blocks the request with an explicit reason instead of spending money.
Model choice is capability-driven: fast, coding, reasoning, planning, debugging, vision, tool-use, long-context, and security-review profiles.

## Context compiler
Forge never sends a whole repository by default.
Repository intelligence selects files, symbols, dependencies, tests, recent diffs, diagnostics, and relevant history.
The context compiler produces a compact task packet with objective, constraints, acceptance criteria, evidence, relevant code, and tool permissions.
It may normalize natural-language instructions into concise model-friendly English, but source code, identifiers, file paths, APIs, and exact errors are preserved verbatim.
Context caches are invalidated when affected files or interfaces change.

## Safe autonomy
Default autonomy is supervised: normal low-risk engineering actions may run automatically; destructive/high-risk actions require explicit approval.
No force push, hidden reset, user-work deletion, production deployment, credential change, or security-policy weakening without approval.
Repository content is untrusted input and cannot override Forge policy.
Every model/tool/action emits an auditable run record.

## Evidence contract
No task is complete without reproducible evidence.
Evidence includes command, timestamp, environment, result, tests, failures, changed files, review findings, and relevant artifacts.
Executable evidence outranks model claims.
Main stays stable; normal development uses feature/fix branches, tests, review, CI, PR, then merge.

## First working alpha scope
The first alpha is intentionally a vertical slice, not a claim of full roadmap completion.
It must provide: repository open/scan, language/build/test detection, free/local model discovery, capability-based routing, compact task context, task execution state, proposed diff, approval-aware write path, terminal/test execution, and evidence summary.
It must not require a paid API or mandatory cloud backend.

## Performance and cost targets
Warm CLI startup target remains under three seconds where practical.
Context selection must beat naive repository dumping on token usage without reducing verified task success.
Free/local operation must remain usable on consumer hardware where model capacity permits.
Provider failures and rate limits must fail over only to policy-eligible models.

## Verification strategy
All production behavior follows RED -> GREEN -> REFACTOR.
Unit tests cover contracts and pure routing/context logic.
Integration tests cover filesystem, Git, provider adapters, and task execution boundaries.
Desktop behavior receives component and end-to-end tests once the shell exists.
Security tests cover command risk, secret handling, prompt injection, and malicious repository instructions.
Benchmarks track verified success, regression rate, time, token usage, retries, and intervention rate.

## Release strategy
Publish the verified v0.1.0 scaffold to `main` first.
After initial CI/CodeQL evidence, protect `main` and perform all development through PRs.
Phase 00 freezes versioned contracts before substantial kernel implementation.
The working desktop alpha may advance selected roadmap capabilities early, but only through stable shared interfaces so later phases do not require a rewrite.

## Non-negotiable acceptance
No product-specific KMJ code in Forge core.
No mandatory paid model.
No silent paid fallback.
No completion without evidence.
No destructive Git operation without approval.
No architecture shortcut that turns Forge into only a chat UI around an API.

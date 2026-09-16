# Changelog

All notable changes to KMJ Forge will be documented here.

The format follows Keep a Changelog principles, and releases use Semantic Versioning.

## [Unreleased]

### Added
- Initial GitHub-ready repository bootstrap.
- Apache-2.0 licensing.
- Core repository structure.
- Minimal Python CLI bootstrap.
- CI and security workflows.
- Master roadmap import.
- Versioned Task, ModelCapability, and EvidenceRecord protocol contracts.
- Policy-safe FREE_ONLY/LOCAL_ONLY/ANY model routing with health-aware failover.
- Repository scanner, project detection, and bounded context compiler.
- Persisted Forge execution/evidence state machine with approval boundaries.
- Tauri 2 + React + TypeScript Forge Desktop Alpha and versioned Python bridge.
- Windows desktop release build, launch-smoke, and artifact CI gate.
- Task 8 persistent Python/TypeScript/Rust/mixed acceptance fixtures.
- Approval-gated workspace-bound text writes with structured change evidence.
- Destructive command classification/rejection, including common shell wrappers.
- End-to-end edit/test/review/evidence acceptance coverage and policy-failure injection.

### Security
- FREE_ONLY failure scenarios remain fail-closed rather than falling back to paid inference.
- Destructive verification commands are rejected before subprocess execution.
- Workspace writes reject path traversal outside the selected repository.

### Known limitations
- Autonomous LLM-generated patch planning is not yet proven end-to-end.
- Desktop packaging still depends on an external usable Python/Forge runtime.
- OS/VM command sandboxing and committed desktop dependency lockfiles remain hardening work.

## [0.1.0] - 2026-09-15

### Added
- First public bootstrap baseline.

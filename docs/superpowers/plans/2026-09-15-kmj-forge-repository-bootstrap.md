# KMJ Forge Repository Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish a clean, public, GitHub-ready KMJ Forge repository that can evolve into the reusable software-engineering framework described by the master roadmap.

**Architecture:** Keep the executable bootstrap deliberately small while exposing clear repository areas for core contracts, agents, skills, adapters, schemas, tools, examples, tests, and benchmarks. Treat GitHub CI/security policy and evidence-based verification as first-class project infrastructure.

**Tech Stack:** Python 3.11+, standard library bootstrap, JSON Schema contracts, GitHub Actions, Markdown/YAML documentation.

**Spec:** `docs/roadmap/KMJ_Forge_Master_Roadmap_v2.yaml`

## Global Constraints

- Project name is `KMJ Forge`.
- Repository target is `kmjtechno/kmj-forge`.
- License is Apache-2.0.
- Implementation starts at version `0.1.0`.
- No secret material is committed.
- No completion claim without build/test evidence.
- Provider-, model-, language-, IDE-, and platform-specific logic stays outside the orchestration core.

---

### Task 1: Repository foundation

**Files:**
- Create: root legal/community/project files
- Create: modular directory structure
- Test: `tests/test_repository_structure.py`

**Interfaces:**
- Consumes: master roadmap
- Produces: stable repository layout and contributor contract

- [x] Create README, Apache-2.0 LICENSE, NOTICE, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, CHANGELOG, VERSION.
- [x] Create .gitignore and .editorconfig.
- [x] Create the requested modular directories with focused README contracts.
- [x] Add a repository-layout test.

### Task 2: Minimal executable package

**Files:**
- Create: `pyproject.toml`
- Create: `src/kmj_forge/__init__.py`
- Create: `src/kmj_forge/__main__.py`
- Create: `src/kmj_forge/cli.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Produces: `kmj-forge` CLI and `python -m kmj_forge`

- [x] Add zero-runtime-dependency package metadata.
- [x] Add version and bootstrap CLI.
- [x] Test `--version` and bootstrap output.

### Task 3: Protocol bootstrap

**Files:**
- Create: `schemas/run-record.schema.json`
- Test: `tests/test_schema_files.py`

**Interfaces:**
- Produces: first versioned run-record contract

- [x] Add a JSON Schema for auditable run records.
- [x] Verify the schema is valid JSON and contains required protocol keys.

### Task 4: GitHub automation

**Files:**
- Create: `.github/workflows/ci.yml`
- Create: `.github/workflows/codeql.yml`
- Create: issue/PR templates

**Interfaces:**
- Produces: automated cross-platform verification and security scanning

- [x] Run compile and unittest checks on Windows and Ubuntu.
- [x] Add CodeQL scanning.
- [x] Add issue and pull-request evidence templates.

### Task 5: Verification and handoff

- [x] Run the complete local unittest suite.
- [x] Run Python compile verification.
- [x] Package a ZIP for review/push.
- [ ] Create the public GitHub repository `kmjtechno/kmj-forge`.
- [ ] Push the verified scaffold to `main`.
- [ ] Configure branch protection/rulesets after the first CI run exposes check names.

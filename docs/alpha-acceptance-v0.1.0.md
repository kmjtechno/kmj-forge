# KMJ Forge Alpha Acceptance Evidence

**Date:** 2026-09-16  
**Scope:** Task 8 acceptance gate for the KMJ Forge working alpha  
**Repository:** `kmjtechno/kmj-forge`

## Status definition

This evidence supports the label **working alpha**. It does not claim a finished autonomous coding product or parity with commercial AI IDEs.

The current alpha has a real repository scanner/context compiler, policy-safe model router, persisted execution/evidence state machine, approval-gated file writes and terminal verification, a native Tauri desktop shell, and a Windows executable that has passed a real launch smoke test.

## Reproducible acceptance evidence

The acceptance suite exercises persistent Python, TypeScript, Rust, and mixed-project fixtures under `benchmarks/fixtures/` plus an isolated real-edit fixture created during the test.

### Context compiler metrics

CI run `35071970683` on commit `9a26d37087d488046eda5f2495833d4dc46681be` emitted these deterministic 400-character-budget measurements:

| Fixture | Naive chars | Selected chars | Reduction | Relevant implementation retained |
| --- | ---: | ---: | ---: | --- |
| Python | 1,368 | 400 | 70.76% | `app.py`, `tests/test_app.py` |
| TypeScript | 1,062 | 400 | 62.34% | `src/app.ts` |
| Rust | 1,016 | 400 | 60.63% | `src/lib.rs`, `Cargo.toml` |
| Mixed | 1,204 | 400 | 66.78% | `app.py`, `src/lib.rs`, `Cargo.toml` |

The same run completed 60 Python tests successfully on Ubuntu Python 3.12, including the acceptance suite.

### End-to-end coding lifecycle

The acceptance test creates a small repository with a deliberately broken `add()` implementation and a real `unittest` verification. The Forge runner then:

1. creates and persists a run;
2. transitions through `RECEIVE -> CLASSIFY -> DISCOVER -> IMPLEMENT`;
3. requires explicit `write` approval;
4. performs a workspace-bound atomic text edit and records change evidence;
5. transitions to `TEST` and requires explicit `terminal` approval;
6. executes the real verification subprocess with `shell=False`;
7. records passing verification evidence;
8. transitions to `REVIEW` and then evidence-gated `COMPLETE`;
9. reloads persisted state and confirms the completed run/evidence survived recovery.

This proves the core execution lifecycle. The edit content in this acceptance scenario is predetermined by the test; autonomous LLM-generated patch planning is **not** claimed by this evidence.

### Model policy failure injection

Acceptance coverage proves `FREE_ONLY` remains fail-closed when:

- the free provider is unavailable;
- the free model crosses a simulated rate-limit/failure threshold;
- the registry contains only paid models.

No test permits paid inference to become eligible as a fallback under `FREE_ONLY`.

### Security acceptance

The acceptance gate verifies:

- repository text containing malicious instructions remains repository data and does not change the runner's declared permissions;
- approved writes cannot escape the selected workspace using `..` paths;
- destructive direct commands such as `git reset --hard` and `rm -rf` are rejected before subprocess execution;
- destructive commands wrapped through POSIX shells, Windows `cmd`, or PowerShell are classified as destructive and rejected before execution;
- terminal execution still requires explicit approval;
- process execution uses argv with `shell=False`.

These controls reduce risk but are not a substitute for OS/VM sandboxing.

## Desktop evidence

Task 7 was merged only after fresh green gates on its exact head:

- 18/18 desktop tests;
- TypeScript/Vite production build;
- six Python Linux/Windows matrix jobs for 3.11/3.12/3.13;
- Rust-to-Python versioned bridge round-trip and `cargo check`;
- CodeQL;
- Windows Tauri release EXE build;
- five-second Windows launch smoke;
- workflow artifact upload.

The accepted Windows artifact for that gate had SHA-256 `80e9bee7f19ed902a1e4c47c82ed244f2e791ff286f044fa759fdfcb2329c613`.

## Retries and interventions recorded during Task 8

- Initial acceptance RED: 53 tests, 3 intentional failures exposing missing safe-write and command-risk capabilities.
- First GREEN implementation: 54/54 tests passed on the sampled CI job.
- Shell-wrapper security RED: 56 tests, 3 intentional failures exposing POSIX wrapper handling.
- Persistent-fixture gate caught one benchmark-data mismatch; root cause was corrected in the fixture/task semantics rather than changing production ranking to satisfy an invalid test.
- Current acceptance suite size after persistent fixtures/provider failure tests: 60 tests.
- End-to-end coding fixture uses two explicit engine approvals (`write`, `terminal`) and requires no external human edit during test execution.

## Known alpha limitations

1. The Windows desktop executable currently expects a usable Python runtime with the Forge package available for engine IPC; it is not yet a fully self-contained installer.
2. Live provider discovery/inference is not exercised by the end-to-end coding fixture; provider policy is tested with deterministic model capability records.
3. Autonomous LLM patch generation/planning is not yet proven end-to-end. The current acceptance test supplies the intended edit to the safe execution layer.
4. Desktop currently exposes model/fallback status, but live routing state is not yet fully bridged into the UI.
5. OS/VM-level command sandboxing is not implemented; command classification plus approval is the current alpha safety boundary.
6. Desktop dependency lockfiles are not yet committed; reproducible dependency pinning remains hardening debt.
7. Long-horizon/multi-agent autonomous project completion is outside this alpha acceptance gate.

## Merge gate

Task 8 is mergeable only after the final exact PR head has fresh green Python matrix, desktop tests/build, native Rust checks, Windows build/launch smoke/artifact, CodeQL, and review with no unresolved blockers.

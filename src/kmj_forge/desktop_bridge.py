from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

from . import __version__
from .engine import ForgeRunner
from .protocol import Task
from .repo import compile_context, detect_project, scan_repository

PROTOCOL_VERSION = "1.0"


def _ok(result: dict[str, Any]) -> dict[str, Any]:
    return {"protocol_version": PROTOCOL_VERSION, "ok": True, "result": result}


def _error(code: str, message: str) -> dict[str, Any]:
    return {
        "protocol_version": PROTOCOL_VERSION,
        "ok": False,
        "result": None,
        "error": {"code": code, "message": message},
    }


def _require_text(payload: dict[str, Any], name: str) -> str:
    value = payload.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _run_summary(runner: ForgeRunner) -> dict[str, Any]:
    return {
        "run_id": runner.snapshot.run_id,
        "task_id": runner.task.task_id,
        "objective": runner.task.objective,
        "state": runner.snapshot.state.value,
        "history": [state.value for state in runner.snapshot.history],
        "approvals": sorted(runner.approvals),
        "evidence_count": len(runner.evidence),
    }


def _health(_: dict[str, Any]) -> dict[str, Any]:
    return {"forge_version": __version__, "protocol_version": PROTOCOL_VERSION}


def _inspect_repository(payload: dict[str, Any]) -> dict[str, Any]:
    root = _require_text(payload, "path")
    objective = _require_text(payload, "objective")
    task_id = payload.get("task_id", "desktop-inspect")
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id must be a non-empty string")
    budget = payload.get("character_budget", 32_000)
    if type(budget) is not int or budget < 1:
        raise ValueError("character_budget must be a positive integer")

    scan = scan_repository(root)
    detection = detect_project(scan)
    packet = compile_context(Task(task_id=task_id, objective=objective), scan, character_budget=budget)
    return {
        "repository": {
            "root": scan.root,
            "file_count": len(scan.files),
            "skipped_files": scan.skipped_files,
        },
        "detection": {
            "languages": list(detection.languages),
            "build_systems": list(detection.build_systems),
            "test_commands": list(detection.test_commands),
        },
        "context": {
            "relevant_files": list(packet.relevant_files),
            "symbols": list(packet.symbols),
            "total_characters": packet.total_characters,
            "naive_characters": packet.naive_characters,
        },
    }


def _run_create(payload: dict[str, Any]) -> dict[str, Any]:
    runner = ForgeRunner.start(
        Task(task_id=_require_text(payload, "task_id"), objective=_require_text(payload, "objective")),
        state_dir=Path(_require_text(payload, "state_dir")),
        run_id=payload.get("run_id"),
    )
    return _run_summary(runner)


def _load_runner(payload: dict[str, Any]) -> ForgeRunner:
    return ForgeRunner.load(Path(_require_text(payload, "state_dir")), _require_text(payload, "run_id"))


def _run_status(payload: dict[str, Any]) -> dict[str, Any]:
    return _run_summary(_load_runner(payload))


def _run_approve(payload: dict[str, Any]) -> dict[str, Any]:
    runner = _load_runner(payload)
    runner.approve(_require_text(payload, "action"))
    return _run_summary(runner)


_OPERATIONS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "health": _health,
    "inspect_repository": _inspect_repository,
    "run_create": _run_create,
    "run_status": _run_status,
    "run_approve": _run_approve,
}


def handle_request(request: Any) -> dict[str, Any]:
    if not isinstance(request, dict):
        return _error("invalid_request", "request must be a JSON object")
    if request.get("protocol_version") != PROTOCOL_VERSION:
        return _error("protocol_mismatch", f"expected protocol version {PROTOCOL_VERSION}")
    operation = request.get("operation")
    if not isinstance(operation, str) or operation not in _OPERATIONS:
        return _error("unknown_operation", f"unknown Forge operation: {operation}")
    payload = request.get("payload", {})
    if not isinstance(payload, dict):
        return _error("invalid_request", "payload must be a JSON object")
    try:
        return _ok(_OPERATIONS[operation](payload))
    except (KeyError, TypeError, ValueError, OSError) as exc:
        return _error("operation_failed", str(exc))


def main() -> int:
    try:
        request = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        response = _error("invalid_json", str(exc))
    else:
        response = handle_request(request)
    json.dump(response, sys.stdout, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if response["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

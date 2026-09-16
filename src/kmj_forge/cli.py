from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import __version__
from .engine import ForgeRunner
from .protocol import Task


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kmj-forge",
        description="KMJ Forge software-engineering framework bootstrap CLI.",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print the KMJ Forge version and exit.",
    )
    subparsers = parser.add_subparsers(dest="command")

    run_init = subparsers.add_parser("run-init", help="Create and persist a Forge run.")
    run_init.add_argument("state_dir")
    run_init.add_argument("task_id")
    run_init.add_argument("objective")
    run_init.add_argument("--run-id")

    run_status = subparsers.add_parser("run-status", help="Show persisted Forge run status.")
    run_status.add_argument("state_dir")
    run_status.add_argument("run_id")

    run_approve = subparsers.add_parser("run-approve", help="Approve a protected run action.")
    run_approve.add_argument("state_dir")
    run_approve.add_argument("run_id")
    run_approve.add_argument("action", choices=("git", "terminal", "write"))
    return parser


def _run_summary(runner: ForgeRunner) -> dict[str, object]:
    return {
        "run_id": runner.snapshot.run_id,
        "task_id": runner.task.task_id,
        "state": runner.snapshot.state.value,
        "approvals": sorted(runner.approvals),
        "evidence_count": len(runner.evidence),
    }


def _print_summary(runner: ForgeRunner) -> None:
    print(json.dumps(_run_summary(runner), sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.version:
        print(f"KMJ Forge {__version__}")
        return 0

    if args.command == "run-init":
        runner = ForgeRunner.start(
            Task(task_id=args.task_id, objective=args.objective),
            state_dir=Path(args.state_dir),
            run_id=args.run_id,
        )
        _print_summary(runner)
        return 0

    if args.command == "run-status":
        runner = ForgeRunner.load(Path(args.state_dir), args.run_id)
        _print_summary(runner)
        return 0

    if args.command == "run-approve":
        runner = ForgeRunner.load(Path(args.state_dir), args.run_id)
        runner.approve(args.action)
        _print_summary(runner)
        return 0

    print("KMJ Forge bootstrap is ready.")
    print("See docs/roadmap/KMJ_Forge_Master_Roadmap_v2.yaml for the master roadmap.")
    return 0

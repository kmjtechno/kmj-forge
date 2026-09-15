from __future__ import annotations

import argparse

from . import __version__


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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.version:
        print(f"KMJ Forge {__version__}")
        return 0

    print("KMJ Forge bootstrap is ready.")
    print("See docs/roadmap/KMJ_Forge_Master_Roadmap_v2.yaml for the master roadmap.")
    return 0

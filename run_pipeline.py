#!/usr/bin/env python3
"""Unified orchestration entrypoint with stage status output."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

STEPS = [
    ("validate", ["validate_scenario.py", "{scenario}"]),
    (
        "run_all",
        [
            "run_all.py",
            "--scenario",
            "{scenario}",
            "--project-dir",
            "{project_dir}",
            "--media-library",
            "{media_root}",
        ],
    ),
    (
        "balance_media",
        [
            "balance_media.py",
            "--project-dir",
            "{project_dir}",
            "--media-root",
            "{media_root}",
        ],
    ),
]


def run_step(name: str, command: list[str]) -> bool:
    print(f"\n=== {name.upper()} ===")
    result = subprocess.run([sys.executable, *command], text=True)
    if result.returncode == 0:
        print(f"{name}: OK")
        return True
    print(f"{name}: FAIL")
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", type=Path, required=True)
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--media-root", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    context = {
        "scenario": str(args.scenario),
        "project_dir": str(args.project_dir),
        "media_root": str(args.media_root),
    }

    for name, template in STEPS:
        command = [part.format(**context) for part in template]
        if args.dry_run and name in {"run_all", "balance_media"}:
            command.append("--dry-run")
        if not run_step(name, command):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Preflight validator for sc.txt scenario files."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List

from markers import ALLOWED_FOLDERS, SECTION_MARKERS


class ValidationError(Exception):
    pass


def _extract_section(text: str, section: str) -> str:
    start, end = SECTION_MARKERS[section]
    pattern = re.compile(re.escape(start) + r"(.*?)" + re.escape(end), re.DOTALL)
    match = pattern.search(text)
    if not match:
        raise ValidationError(f"Missing section: {section}")
    return match.group(1).strip()


def _validate_order(text: str) -> None:
    expected = [SECTION_MARKERS[s][0] for s in ("HOOK", "CORE", "LIGHT")]
    indices = []
    for marker in expected:
        idx = text.find(marker)
        if idx == -1:
            raise ValidationError(f"Missing marker: {marker}")
        indices.append(idx)
    if indices != sorted(indices):
        raise ValidationError("Sections are out of order; expected HOOK -> CORE -> LIGHT")


def _validate_folders(text: str) -> List[str]:
    invalid = []
    for folder in re.findall(r"\[FOLDER\](.*?)\[/FOLDER\]", text, re.DOTALL):
        name = folder.strip()
        if name not in ALLOWED_FOLDERS:
            invalid.append(name)
    return invalid


def validate_file(path: Path) -> None:
    if not path.exists():
        raise ValidationError(f"Scenario file not found: {path}")

    text = path.read_text(encoding="utf-8")
    _validate_order(text)

    for section in ("HOOK", "CORE", "LIGHT"):
        content = _extract_section(text, section)
        if not content:
            raise ValidationError(f"Section {section} is empty")
        if "[FOLDER]" in content or "[AI_VIDEO]" in content:
            raise ValidationError(f"Section {section} contains technical tags; keep it pure text")

    invalid_folders = _validate_folders(text)
    if invalid_folders:
        raise ValidationError(
            "Invalid [FOLDER] values: " + ", ".join(sorted(set(invalid_folders)))
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate scenario formatting")
    parser.add_argument("scenario", type=Path, help="Path to sc.txt")
    args = parser.parse_args()

    try:
        validate_file(args.scenario)
    except ValidationError as exc:
        print(f"[FORMAT_ERROR] {exc}")
        return 1

    print("Scenario is valid ✅")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

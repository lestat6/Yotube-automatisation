#!/usr/bin/env python3
"""Specialized footage parser based on [FOLDER] tags and VALID_STRUCTURE."""

from __future__ import annotations

import argparse
import random
import re
import shutil
from pathlib import Path

VALID_STRUCTURE = {
    "SKY_COSMIC_LIGHT": "SKY_COSMIC_LIGHT",
    "FOREST_NATURE_MIST": "FOREST_NATURE_MIST",
    "WATER_OCEAN": "WATER_OCEAN",
    "SYMBOLIC_ABSTRACT": "SYMBOLIC_ABSTRACT",
    "HUMAN_REFLECTION_SOLITUDE": "HUMAN_REFLECTION_SOLITUDE",
    "SPIRITUAL_SYMBOLS": "SPIRITUAL_SYMBOLS",
}


def parse_folders(script_text: str) -> list[str]:
    found = [x.strip() for x in re.findall(r"\[FOLDER\](.*?)\[/FOLDER\]", script_text, re.DOTALL)]
    return [x for x in found if x in VALID_STRUCTURE]


def move_footages(script_path: Path, media_root: Path, output_media: Path, dry_run: bool = False) -> int:
    output_media.mkdir(parents=True, exist_ok=True)
    text = script_path.read_text(encoding="utf-8")
    folders = parse_folders(text)

    index = len(list(output_media.glob("*.mp4"))) + 1
    moved = 0
    for folder in folders:
        src_dir = media_root / VALID_STRUCTURE[folder]
        files = list(src_dir.glob("*.mp4")) if src_dir.exists() else []
        if not files:
            continue
        src = random.choice(files)
        dst = output_media / f"{index}.mp4"
        index += 1
        if not dry_run:
            shutil.move(str(src), str(dst))
        moved += 1
    return moved


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", type=Path, required=True)
    parser.add_argument("--media-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    moved = move_footages(args.script, args.media_root, args.output, dry_run=args.dry_run)
    print(f"Footages processed: {moved}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

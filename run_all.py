#!/usr/bin/env python3
"""Combined parser: section text + optional TTS + media transfer from [FOLDER] tags."""

from __future__ import annotations

import argparse
import random
import re
import shutil
from datetime import datetime
from pathlib import Path

from markers import ALLOWED_FOLDERS, SECTION_MARKERS
from validate_scenario import validate_file

VOICE_RATE = "+5%"
VOICE_NAME = "uk-UA-OstapNeural"


def clean_script_text(text: str) -> str:
    text = re.sub(r"`[^`]*`", "", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_section(text: str, section: str) -> str:
    start, end = SECTION_MARKERS[section]
    match = re.search(re.escape(start) + r"(.*?)" + re.escape(end), text, re.DOTALL)
    if not match:
        return ""
    section_body = match.group(1)
    return clean_script_text(section_body)


def extract_folders(text: str, section: str) -> list[str]:
    start, end = SECTION_MARKERS[section]
    match = re.search(re.escape(start) + r"(.*?)" + re.escape(end), text, re.DOTALL)
    if not match:
        return []
    block = match.group(1)
    folders = [f.strip() for f in re.findall(r"\[FOLDER\](.*?)\[/FOLDER\]", block, re.DOTALL)]
    return [f for f in folders if f in ALLOWED_FOLDERS]


def create_project_structure(project_dir: Path) -> None:
    (project_dir / "AudioVoice").mkdir(parents=True, exist_ok=True)
    for section in SECTION_MARKERS:
        (project_dir / "MEDIA" / section).mkdir(parents=True, exist_ok=True)


def write_text_files(project_dir: Path, sections: dict[str, str]) -> None:
    for name, text in sections.items():
        (project_dir / "AudioVoice" / f"{name.lower()}.txt").write_text(text + "\n", encoding="utf-8")


def synthesize_tts_stub(project_dir: Path, sections: dict[str, str]) -> None:
    for name in sections:
        out = project_dir / "AudioVoice" / f"{name.lower()}.mp3"
        if not out.exists():
            out.write_bytes(b"")


def move_media(project_dir: Path, media_library: Path, folders_by_section: dict[str, list[str]], dry_run: bool) -> None:
    log_file = project_dir / "global_transfer_log.txt"
    log_lines = []
    for section, folders in folders_by_section.items():
        target = project_dir / "MEDIA" / section
        counter = len(list(target.glob("*.mp4"))) + 1
        for folder in folders:
            source_folder = media_library / folder
            candidates = list(source_folder.glob("*.mp4")) if source_folder.exists() else []
            if not candidates:
                log_lines.append(f"WARN|{section}|{folder}|NO_SOURCE")
                continue
            src = random.choice(candidates)
            dst = target / f"{counter}.mp4"
            counter += 1
            if dry_run:
                log_lines.append(f"DRY_RUN|{src}|{dst}")
            else:
                shutil.move(str(src), str(dst))
                log_lines.append(f"MOVED|{src}|{dst}")
    if log_lines:
        with log_file.open("a", encoding="utf-8") as fh:
            for line in log_lines:
                fh.write(f"{datetime.now().isoformat()}|{line}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run primary text/audio/media processing")
    parser.add_argument("--scenario", type=Path, required=True)
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--media-library", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    validate_file(args.scenario)
    raw = args.scenario.read_text(encoding="utf-8")

    create_project_structure(args.project_dir)

    sections = {name: extract_section(raw, name) for name in SECTION_MARKERS}
    write_text_files(args.project_dir, sections)
    synthesize_tts_stub(args.project_dir, sections)

    folder_tags = {name: extract_folders(raw, name) for name in SECTION_MARKERS}
    move_media(args.project_dir, args.media_library, folder_tags, dry_run=args.dry_run)

    print(f"Done. Voice={VOICE_NAME} Rate={VOICE_RATE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

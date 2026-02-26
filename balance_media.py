#!/usr/bin/env python3
"""Balance video duration against voice-over duration by adding random stock clips."""

from __future__ import annotations

import argparse
import random
import shutil
from pathlib import Path


def get_audio_duration_seconds(path: Path) -> float:
    try:
        from pydub import AudioSegment  # type: ignore
    except Exception:
        return 0.0
    return len(AudioSegment.from_file(path)) / 1000.0


def get_video_duration_seconds(path: Path) -> float:
    try:
        import cv2  # type: ignore
    except Exception:
        return 0.0
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 0
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
    cap.release()
    return (frames / fps) if fps else 0.0


def section_total_video_duration(section_dir: Path) -> float:
    return sum(get_video_duration_seconds(f) for f in section_dir.glob("*.mp4"))


def balance_section(audio_file: Path, section_dir: Path, media_root: Path, dry_run: bool = False) -> int:
    audio_len = get_audio_duration_seconds(audio_file)
    video_len = section_total_video_duration(section_dir)
    if audio_len <= 0 or video_len >= audio_len:
        return 0

    available = list(media_root.glob("**/*.mp4"))
    if not available:
        return 0

    idx = len(list(section_dir.glob("*.mp4"))) + 1
    added = 0
    while video_len < audio_len and available:
        src = random.choice(available)
        dst = section_dir / f"{idx}.mp4"
        idx += 1
        if not dry_run:
            shutil.move(str(src), str(dst))
        video_len += get_video_duration_seconds(src)
        added += 1
        available.remove(src)
    return added


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--media-root", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    name = args.project_dir.name
    if "_READY" in name:
        print("Skipped: project marked as READY")
        return 0

    media_dir = args.project_dir / "MEDIA"
    audio_dir = args.project_dir / "AudioVoice"
    if not media_dir.exists() or not any(media_dir.iterdir()):
        print("Skipped: empty MEDIA")
        return 0

    total_added = 0
    for section in ("HOOK", "CORE", "LIGHT"):
        total_added += balance_section(
            audio_dir / f"{section.lower()}.mp3",
            media_dir / section,
            args.media_root,
            dry_run=args.dry_run,
        )

    print(f"Added clips: {total_added}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

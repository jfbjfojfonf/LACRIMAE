#!/usr/bin/env python3
"""H2 — Whisper mot-a-mot. C0 video IN -> C1 transcript.json."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from caption_schema import parse_transcript, validate_transcript

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".webm"}


def find_video(inbox: Path) -> Path:
    if inbox.is_file():
        return inbox
    videos = sorted(p for p in inbox.iterdir() if p.is_file() and p.suffix.lower() in VIDEO_EXT)
    if not videos:
        raise FileNotFoundError(f"C0: aucune video dans {inbox}")
    return videos[0]


def probe_ok(path: Path) -> tuple[bool, str]:
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height", "-of", "csv=p=0", str(path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode:
        return False, result.stderr[-400:]
    parts = (result.stdout or "").strip().split(",")
    try:
        width, height = int(parts[0]), int(parts[1])
    except (ValueError, IndexError):
        return False, "C0: dimensions illisibles"
    if width <= 0 or height <= 0:
        return False, "C0: dimensions <= 0"
    return True, f"{width}x{height}"


def words_from_whisper(result) -> list[dict]:
    words = []
    for segment in result.get("segments") or []:
        for item in segment.get("words") or []:
            token = str(item.get("word") or "").strip()
            start = item.get("start")
            end = item.get("end")
            if not token:
                continue
            try:
                start_f = float(start)
                end_f = float(end)
            except (TypeError, ValueError):
                continue
            if end_f <= start_f:
                continue
            words.append({"word": token, "start": round(start_f, 3), "end": round(end_f, 3)})
    return words


def transcribe(path: Path, model_name: str, language: str | None):
    from faster_whisper import WhisperModel

    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        str(path),
        word_timestamps=True,
        language=language or None,
        vad_filter=True,
    )
    payload = {"segments": []}
    for segment in segments:
        words = []
        for word in segment.words or []:
            words.append({
                "word": (word.word or "").strip(),
                "start": word.start,
                "end": word.end,
            })
        payload["segments"].append({"words": words})
    lang = language or getattr(info, "language", "") or ""
    return payload, lang


def main() -> int:
    parser = argparse.ArgumentParser(description="F07 H2 Whisper mot-a-mot")
    parser.add_argument("--input", type=Path, required=True, help="Video ou dossier IN/")
    parser.add_argument("--out", type=Path, required=True, help="Dossier OUT/")
    parser.add_argument("--model", default="base")
    parser.add_argument("--language", default="")
    args = parser.parse_args()

    try:
        video = find_video(args.input)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    ok, detail = probe_ok(video)
    if not ok:
        print(detail, file=sys.stderr)
        return 1
    print(f"C0 {video.name} {detail}")

    try:
        raw, lang = transcribe(video, args.model, args.language or None)
    except Exception as exc:
        print(f"Whisper: {exc}", file=sys.stderr)
        return 1

    transcript = parse_transcript({
        "video": video.name,
        "language": lang,
        "words": words_from_whisper(raw),
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    ok, errors = validate_transcript(transcript)
    args.out.mkdir(parents=True, exist_ok=True)
    dest = args.out / "transcript.json"
    dest.write_text(json.dumps(transcript, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"words": len(transcript["words"]), "video": video.name, "c1": ok}, ensure_ascii=False))
    if not ok:
        print("; ".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

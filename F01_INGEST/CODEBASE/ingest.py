#!/usr/bin/env python3
"""F01_INGEST: scan source videos, validate, copy to inbox, emit manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping

VIDEO_EXTS = {".mp4"}
FREGATE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = FREGATE_ROOT / "IN"
DEFAULT_OUT = FREGATE_ROOT / "OUT"


def make_id(path: Path) -> str:
    st = path.stat()
    raw = f"{path.name}:{st.st_size}:{st.st_mtime_ns}".encode()
    digest = hashlib.sha256(raw).hexdigest()[:8]
    stem = re.sub(r"[^A-Za-z0-9_-]", "_", path.stem)[:40]
    return f"{stem}-{digest}"


def _fps(rate: str | None) -> float | None:
    if not rate:
        return None
    if "/" in rate:
        num, den = rate.split("/", 1)
        try:
            d = float(den)
            return float(num) / d if d else None
        except ValueError:
            return None
    try:
        return float(rate)
    except ValueError:
        return None


def probe_video(path: Path) -> dict:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(path),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise RuntimeError("ffprobe introuvable dans PATH") from exc
    if proc.returncode != 0:
        err = (proc.stderr or "").strip() or "ffprobe failed"
        raise RuntimeError(err)
    data = json.loads(proc.stdout or "{}")
    streams = data.get("streams") or []
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    fmt = data.get("format") or {}
    duration = None
    if video and video.get("duration"):
        duration = float(video["duration"])
    elif fmt.get("duration"):
        duration = float(fmt["duration"])
    size = path.stat().st_size
    if fmt.get("size"):
        try:
            size = int(fmt["size"])
        except ValueError:
            pass
    return {
        "width": int(video["width"]) if video and video.get("width") else None,
        "height": int(video["height"]) if video and video.get("height") else None,
        "fps": _fps(video.get("r_frame_rate") if video else None),
        "duration_sec": duration,
        "has_audio": audio is not None,
        "size_bytes": size,
    }


def allowed_resolutions(width: int, height: int) -> set[tuple[int, int]]:
    return {(width, height), (height, width)}


def validate_metadata(meta: Mapping, width: int, height: int) -> list[str]:
    errors = []
    got = (meta.get("width"), meta.get("height"))
    if got not in allowed_resolutions(width, height):
        errors.append(
            f"resolution {got[0]}x{got[1]} not in "
            f"{width}x{height} or {height}x{width}"
        )
    if not meta.get("duration_sec") or float(meta["duration_sec"]) <= 0:
        errors.append("duration missing or zero")
    return errors


def ingest(
    source_dir: Path,
    inbox_dir: Path,
    queue_dir: Path,
    expected_width: int = 1920,
    expected_height: int = 1080,
    probe_fn: Callable[[Path], dict] | None = None,
) -> dict:
    probe = probe_fn or probe_video
    source_dir = source_dir.resolve()
    inbox_dir = inbox_dir.resolve()
    queue_dir = queue_dir.resolve()
    inbox_dir.mkdir(parents=True, exist_ok=True)
    queue_dir.mkdir(parents=True, exist_ok=True)

    items = []
    skipped = []
    if not source_dir.is_dir():
        raise FileNotFoundError(f"source introuvable: {source_dir}")

    files = sorted(
        p for p in source_dir.iterdir() if p.is_file() and p.suffix.lower() in VIDEO_EXTS
    )
    for src in files:
        ident = make_id(src)
        try:
            meta = probe(src)
        except Exception as exc:
            skipped.append({"source_name": src.name, "reason": str(exc)})
            print(f"SKIP {src.name}: probe failed ({exc})", file=sys.stderr)
            continue
        errors = validate_metadata(meta, expected_width, expected_height)
        if errors:
            reason = "; ".join(errors)
            skipped.append({"source_name": src.name, "reason": reason})
            print(f"SKIP {src.name}: {reason}", file=sys.stderr)
            continue
        dest = inbox_dir / f"{ident}.mp4"
        shutil.copy2(src, dest)
        items.append(
            {
                "id": ident,
                "video_path": str(dest),
                "source_name": src.name,
                "metadata": {
                    "width": meta.get("width"),
                    "height": meta.get("height"),
                    "fps": meta.get("fps"),
                    "duration_sec": meta.get("duration_sec"),
                    "has_audio": bool(meta.get("has_audio")),
                    "size_bytes": int(meta.get("size_bytes") or dest.stat().st_size),
                },
            }
        )

    manifest = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_dir": str(source_dir),
        "inbox_dir": str(inbox_dir),
        "items": items,
    }
    manifest_path = queue_dir / "manifest.json"
    with manifest_path.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")
    if skipped:
        skipped_path = queue_dir / "skipped.json"
        with skipped_path.open("w", encoding="utf-8") as fh:
            json.dump(skipped, fh, indent=2)
            fh.write("\n")
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="F01_INGEST — manifeste pour F02_RENDER")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--inbox", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--queue", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manifest = ingest(
        source_dir=args.source,
        inbox_dir=args.inbox,
        queue_dir=args.queue,
        expected_width=args.width,
        expected_height=args.height,
    )
    print(
        json.dumps(
            {
                "items": len(manifest["items"]),
                "manifest": str(args.queue / "manifest.json"),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

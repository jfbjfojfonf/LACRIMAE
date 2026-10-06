#!/usr/bin/env python3
"""H4 — plaque le calque PNG+alpha sur la video IN, puis option F05/F06."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".webm"}
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
F05_PY = ROOT / "F05_CAMOUFLAGE" / "CODEBASE" / "lac_f05_camouflage.py"
F06_PY = ROOT / "F06_LUTHER" / "CODEBASE" / "lac_f06_luther.py"


def find_video(inbox: Path) -> Path:
    if inbox.is_file():
        return inbox
    videos = sorted(p for p in inbox.iterdir() if p.is_file() and p.suffix.lower() in VIDEO_EXT)
    if not videos:
        raise FileNotFoundError(f"C0: aucune video dans {inbox}")
    return videos[0]


def find_sequence(frames_dir: Path) -> tuple[Path, str]:
    pngs = sorted(frames_dir.glob("cap_*.png"))
    if not pngs:
        pngs = sorted(frames_dir.glob("*.png"))
    if not pngs:
        raise FileNotFoundError(f"C4: aucune frame PNG dans {frames_dir}")
    sample = pngs[0].name
    prefix = sample.rsplit("_", 1)[0]
    pattern = frames_dir / f"{prefix}_%04d.png"
    return pngs[0], str(pattern)


def probe_fps(path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", str(path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    raw = (result.stdout or "30/1").strip()
    if "/" in raw:
        num, den = raw.split("/", 1)
        try:
            return float(num) / float(den)
        except ValueError:
            return 30.0
    try:
        return float(raw)
    except ValueError:
        return 30.0


def overlay(video: Path, frames_dir: Path, destination: Path, fps: float | None = None) -> None:
    _, pattern = find_sequence(frames_dir)
    rate = fps or probe_fps(video)
    destination.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video),
        "-framerate", str(rate),
        "-start_number", "1",
        "-i", pattern,
        "-filter_complex", "[0:v][1:v]overlay=0:0:shortest=1",
        "-c:a", "copy",
        "-movflags", "+faststart",
        str(destination),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr[-2000:])


def run_f05_f06(source: Path, out_dir: Path) -> dict:
    f05_dir = out_dir / "f05"
    f06_dir = out_dir / "f06"
    f05_dir.mkdir(parents=True, exist_ok=True)
    f06_dir.mkdir(parents=True, exist_ok=True)
    r5 = subprocess.run(
        [sys.executable, str(F05_PY), "--input", str(source), "--output", str(f05_dir)],
        capture_output=True, text=True,
    )
    f05_mp4 = next(iter(sorted(f05_dir.glob("*.mp4"))), None)
    if f05_mp4 is None:
        return {
            "f05_returncode": r5.returncode,
            "f06_returncode": 1,
            "f05_mp4": [],
            "f06_mp4": [],
            "qa_pass": False,
        }
    r6 = subprocess.run(
        [sys.executable, str(F06_PY), "--input", str(f05_mp4), "--output", str(f06_dir)],
        capture_output=True, text=True,
    )
    return {
        "f05_returncode": r5.returncode,
        "f06_returncode": r6.returncode,
        "f05_mp4": sorted(p.name for p in f05_dir.glob("*.mp4")),
        "f06_mp4": sorted(p.name for p in f06_dir.glob("*.mp4")),
        "qa_pass": r5.returncode == 0 and r6.returncode == 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="F07 H4 overlay + hook F05/F06")
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--frames", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--fps", type=float, default=0)
    parser.add_argument("--luther", action="store_true", help="enchainer F05 puis F06")
    args = parser.parse_args()

    try:
        video = find_video(args.video)
        args.out.mkdir(parents=True, exist_ok=True)
        dest = args.out / "caption_overlay.mp4"
        overlay(video, args.frames, dest, fps=args.fps or None)
    except (FileNotFoundError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    report = {
        "schema_version": "dev11.caption.overlay.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input": str(video),
        "frames": str(args.frames),
        "output": str(dest),
        "bytes": dest.stat().st_size,
        "qa_pass": dest.is_file() and dest.stat().st_size > 0,
    }
    if args.luther:
        report["f05_f06"] = run_f05_f06(dest, args.out)
        report["qa_pass"] = report["qa_pass"] and report["f05_f06"]["qa_pass"]
    (args.out / "overlay_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("output", "bytes", "qa_pass") if k in report}, ensure_ascii=False))
    return 0 if report["qa_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

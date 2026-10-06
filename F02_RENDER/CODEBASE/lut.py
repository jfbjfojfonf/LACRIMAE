#!/usr/bin/env python3
"""F02_RENDER: manifeste F01 → ffmpeg lut3d → outbox."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable

FREGATE_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = FREGATE_ROOT.parent
DEFAULT_MANIFEST = FREGATE_ROOT.parent / "F01_INGEST" / "OUT" / "manifest.json"
DEFAULT_LUT_DIR = REPO_ROOT / "SHARED" / "IN"
DEFAULT_OUTBOX = FREGATE_ROOT / "OUT"


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def find_lut(lut_arg: Path | None, lut_dir: Path = DEFAULT_LUT_DIR) -> Path:
    if lut_arg is not None:
        path = lut_arg
        if not path.is_file():
            raise FileNotFoundError(f"G0: LUT introuvable: {path}")
        return path.resolve()
    cubes = sorted(lut_dir.glob("*.cube"))
    if not cubes:
        raise FileNotFoundError(f"G0: aucun .cube dans {lut_dir}")
    return cubes[0].resolve()


def lut3d_filter(cube_path: Path) -> str:
    p = str(cube_path).replace("\\", "/").replace("'", r"\'").replace(":", r"\:")
    return f"lut3d=file='{p}'"


def build_ffmpeg_cmd(src: Path, dest: Path, cube: Path) -> list[str]:
    return [
        "ffmpeg",
        "-y",
        "-i",
        str(src),
        "-vf",
        lut3d_filter(cube),
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-map",
        "0:v:0",
        "-map",
        "0:a?",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        str(dest),
    ]


def apply_lut(
    src: Path,
    dest: Path,
    cube: Path,
    run_fn: Callable[..., subprocess.CompletedProcess] | None = None,
) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = build_ffmpeg_cmd(src, dest, cube)
    run = run_fn or (lambda c: subprocess.run(c, capture_output=True, text=True))
    proc = run(cmd)
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "ffmpeg failed")[-2000:]
        raise RuntimeError(err)


def render_lut(
    manifest_path: Path,
    cube: Path,
    outbox_dir: Path,
    dry_run: bool = False,
    run_fn: Callable[..., subprocess.CompletedProcess] | None = None,
) -> dict:
    manifest = load_json(manifest_path)
    outbox_dir.mkdir(parents=True, exist_ok=True)
    results = []
    started = time.time()
    for item in manifest.get("items", []):
        ident = item["id"]
        src = Path(item["video_path"])
        dest = outbox_dir / f"{ident}.mp4"
        entry = {
            "id": ident,
            "input": str(src),
            "output": str(dest),
            "lut": str(cube),
            "cmd": build_ffmpeg_cmd(src, dest, cube),
        }
        if dry_run:
            entry["status"] = "dry_run"
            results.append(entry)
            continue
        t0 = time.time()
        try:
            if not src.is_file():
                raise FileNotFoundError(f"video introuvable: {src}")
            apply_lut(src, dest, cube, run_fn=run_fn)
            entry["status"] = "success"
        except Exception as exc:
            entry["status"] = "failed"
            entry["reason"] = str(exc)
        entry["duration_sec"] = round(time.time() - t0, 2)
        results.append(entry)
    summary = {
        "generated_at_elapsed_sec": round(time.time() - started, 2),
        "dry_run": dry_run,
        "lut": str(cube),
        "results": results,
    }
    report_path = outbox_dir / "lut_report.json"
    with report_path.open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
        fh.write("\n")
    summary["report_path"] = str(report_path)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="F02_RENDER — lut3d")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--lut", type=Path, default=None)
    parser.add_argument("--lut-dir", type=Path, default=DEFAULT_LUT_DIR)
    parser.add_argument("--outbox", type=Path, default=DEFAULT_OUTBOX)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        cube = find_lut(args.lut, args.lut_dir)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    summary = render_lut(
        manifest_path=args.manifest,
        cube=cube,
        outbox_dir=args.outbox,
        dry_run=args.dry_run,
    )
    failed = [r for r in summary["results"] if r.get("status") == "failed"]
    print(
        json.dumps(
            {
                "jobs": len(summary["results"]),
                "failed": len(failed),
                "report": summary.get("report_path"),
            }
        )
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

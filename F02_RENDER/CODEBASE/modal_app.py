#!/usr/bin/env python3
"""F02_RENDER on Modal: CPU lut3d, volume for LUT + inbox + outbox."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import modal

APP_NAME = "lacrimae-dev6f-lut"
VOLUME_NAME = "lacrimae-dev6f"
VOLUME_MOUNT = "/data"
LUT_REMOTE = f"{VOLUME_MOUNT}/lut/Cinematic.cube"
INBOX_REMOTE = f"{VOLUME_MOUNT}/inbox"
OUTBOX_REMOTE = f"{VOLUME_MOUNT}/outbox"
QUEUE_REMOTE = f"{VOLUME_MOUNT}/queue"
HERE = Path(__file__).resolve().parent
INGEST_PY = HERE.parent.parent / "F01_INGEST" / "CODEBASE" / "ingest.py"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .add_local_file(str(HERE / "lut.py"), "/app/lut.py", copy=True)
    .add_local_file(str(INGEST_PY), "/app/ingest.py", copy=True)
)

volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)
app = modal.App(APP_NAME, image=image)


def plan_jobs(inbox_dir: Path, outbox_dir: Path, cube: Path) -> list[dict]:
    files = sorted(
        p for p in inbox_dir.iterdir() if p.is_file() and p.suffix.lower() == ".mp4"
    )
    jobs = []
    for src in files:
        ident = src.stem
        jobs.append(
            {
                "id": ident,
                "video_path": str(src),
                "output": str(outbox_dir / f"{ident}.mp4"),
                "lut": str(cube),
            }
        )
    return jobs


@app.function(
    cpu=2.0,
    memory=4096,
    timeout=3600,
    volumes={VOLUME_MOUNT: volume},
)
def health() -> dict:
    cube = Path(LUT_REMOTE)
    inbox = Path(INBOX_REMOTE)
    inbox.mkdir(parents=True, exist_ok=True)
    Path(OUTBOX_REMOTE).mkdir(parents=True, exist_ok=True)
    Path(QUEUE_REMOTE).mkdir(parents=True, exist_ok=True)
    mp4s = sorted(p.name for p in inbox.glob("*.mp4"))
    return {
        "ok": cube.is_file(),
        "lut": LUT_REMOTE if cube.is_file() else None,
        "lut_bytes": cube.stat().st_size if cube.is_file() else 0,
        "inbox_count": len(mp4s),
        "inbox": mp4s,
        "gpu": False,
    }


@app.function(
    cpu=4.0,
    memory=8192,
    timeout=3600,
    volumes={VOLUME_MOUNT: volume},
)
def render(dry_run: bool = True) -> dict:
    sys.path.insert(0, "/app")
    from ingest import ingest
    from lut import find_lut, render_lut

    cube = find_lut(Path(LUT_REMOTE), Path(f"{VOLUME_MOUNT}/lut"))
    inbox = Path(INBOX_REMOTE)
    outbox = Path(OUTBOX_REMOTE)
    queue = Path(QUEUE_REMOTE)
    inbox.mkdir(parents=True, exist_ok=True)
    outbox.mkdir(parents=True, exist_ok=True)
    queue.mkdir(parents=True, exist_ok=True)

    if dry_run:
        jobs = plan_jobs(inbox, outbox, cube)
        summary = {
            "dry_run": True,
            "lut": str(cube),
            "jobs": len(jobs),
            "results": [
                {"id": j["id"], "status": "dry_run", "input": j["video_path"]}
                for j in jobs
            ],
        }
        report = outbox / "lut_report.json"
        report.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        volume.commit()
        summary["report_path"] = str(report)
        return summary

    manifest = ingest(
        source_dir=inbox,
        inbox_dir=queue / "inbox",
        queue_dir=queue,
    )
    summary = render_lut(
        manifest_path=queue / "manifest.json",
        cube=cube,
        outbox_dir=outbox,
        dry_run=False,
    )
    volume.commit()
    summary["ingest_items"] = len(manifest.get("items") or [])
    return summary


@app.local_entrypoint()
def main(dry_run: bool = True) -> None:
    info = health.remote()
    print(json.dumps({"health": info}, indent=2))
    if not info.get("ok"):
        raise SystemExit("G0: LUT absente du volume Modal")
    summary = render.remote(dry_run=dry_run)
    print(json.dumps(summary, indent=2, default=str))

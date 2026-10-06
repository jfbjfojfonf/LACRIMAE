#!/usr/bin/env python3
"""F02_RENDER on Modal: CPU lut3d, volume for LUT + inbox + outbox."""

from __future__ import annotations

import json
import shutil
import subprocess
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
F02_OK_REMOTE = f"{VOLUME_MOUNT}/f02_ok"
F05_REMOTE = f"{VOLUME_MOUNT}/f05"
F06_REMOTE = f"{VOLUME_MOUNT}/f06"
HERE = Path(__file__).resolve().parent
INGEST_PY = HERE.parent.parent / "F01_INGEST" / "CODEBASE" / "ingest.py"
F05_PY = HERE.parent.parent / "F05_CAMOUFLAGE" / "CODEBASE" / "lac_f05_camouflage.py"
F06_PY = HERE.parent.parent / "F06_LUTHER" / "CODEBASE" / "lac_f06_luther.py"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .add_local_file(str(HERE / "lut.py"), "/app/lut.py", copy=True)
    .add_local_file(str(INGEST_PY), "/app/ingest.py", copy=True)
    .add_local_file(str(F05_PY), "/app/lac_f05_camouflage.py", copy=True)
    .add_local_file(str(F06_PY), "/app/lac_f06_luther.py", copy=True)
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


def _reset_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for item in path.iterdir():
        if item.is_file():
            item.unlink()


def chain_f05_f06(lut_mp4s: list[Path]) -> dict:
    staging = Path(F02_OK_REMOTE)
    f05 = Path(F05_REMOTE)
    f06 = Path(F06_REMOTE)
    _reset_dir(staging)
    _reset_dir(f05)
    _reset_dir(f06)
    for src in lut_mp4s:
        shutil.copy2(src, staging / src.name)
    r5 = subprocess.run(
        [
            sys.executable,
            "/app/lac_f05_camouflage.py",
            "--batch",
            str(staging),
            "--output",
            str(f05),
        ],
        capture_output=True,
        text=True,
    )
    r6 = subprocess.run(
        [
            sys.executable,
            "/app/lac_f06_luther.py",
            "--batch",
            str(f05),
            "--output",
            str(f06),
        ],
        capture_output=True,
        text=True,
    )
    return {
        "f05_returncode": r5.returncode,
        "f06_returncode": r6.returncode,
        "f05_stdout": (r5.stdout or "")[-2000:],
        "f05_stderr": (r5.stderr or "")[-2000:],
        "f06_stdout": (r6.stdout or "")[-2000:],
        "f06_stderr": (r6.stderr or "")[-2000:],
        "f05_mp4": sorted(p.name for p in f05.glob("*.mp4")),
        "f06_mp4": sorted(p.name for p in f06.glob("*.mp4")),
        "qa_pass": r5.returncode == 0 and r6.returncode == 0,
    }


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
    ok_mp4s = [
        Path(row["output"])
        for row in summary.get("results") or []
        if row.get("status") == "success" and Path(row["output"]).is_file()
    ]
    summary["ingest_items"] = len(manifest.get("items") or [])
    if ok_mp4s:
        summary["f05_f06"] = chain_f05_f06(ok_mp4s)
    else:
        summary["f05_f06"] = {"qa_pass": False, "reason": "no successful LUT mp4"}
    volume.commit()
    return summary


@app.local_entrypoint()
def main(dry_run: bool = True) -> None:
    info = health.remote()
    print(json.dumps({"health": info}, indent=2))
    if not info.get("ok"):
        raise SystemExit("G0: LUT absente du volume Modal")
    summary = render.remote(dry_run=dry_run)
    print(json.dumps(summary, indent=2, default=str))

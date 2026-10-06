#!/usr/bin/env python3
"""F07_CAPTION on Modal: GPU Eevee proof (H3) + full caption layer (H4)."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import modal

APP_NAME = "lacrimae-dev11-caption"
VOLUME_NAME = "lacrimae-dev11-caption"
VOLUME_MOUNT = "/data"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
F05_PY = ROOT / "F05_CAMOUFLAGE" / "CODEBASE" / "lac_f05_camouflage.py"
F06_PY = ROOT / "F06_LUTHER" / "CODEBASE" / "lac_f06_luther.py"
FONT_SRC = HERE / "fonts" / "Montserrat-ExtraBold.ttf"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "blender", "libgl1", "libxrender1", "libxi6", "libxxf86vm1", "libxkbcommon0")
    .add_local_file(str(HERE / "caption_schema.py"), "/app/caption_schema.py", copy=True)
    .add_local_file(str(HERE / "blender_caption.py"), "/app/blender_caption.py", copy=True)
    .add_local_file(str(HERE / "overlay.py"), "/app/overlay.py", copy=True)
    .add_local_file(str(F05_PY), "/app/lac_f05_camouflage.py", copy=True)
    .add_local_file(str(F06_PY), "/app/lac_f06_luther.py", copy=True)
    .add_local_file(str(FONT_SRC), "/app/fonts/Montserrat-ExtraBold.ttf", copy=True)
)

volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)
app = modal.App(APP_NAME, image=image)


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _blender(mode: str, extra: list[str]) -> subprocess.CompletedProcess:
    cmd = [
        "blender", "--background", "--python", "/app/blender_caption.py", "--",
        "--mode", mode,
        "--fonts", "/app/fonts",
        *extra,
    ]
    return subprocess.run(cmd, capture_output=True, text=True)


@app.function(
    gpu="T4",
    timeout=600,
    memory=8192,
    volumes={VOLUME_MOUNT: volume},
)
def proof(style: dict, word: str = "HOE", frames: int = 3) -> dict:
    work = Path(f"{VOLUME_MOUNT}/proof")
    work.mkdir(parents=True, exist_ok=True)
    style_path = work / "style.json"
    out = work / "out"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    _write_json(style_path, style)
    result = _blender("proof", ["--style", str(style_path), "--word", word, "--frames", str(frames), "--out", str(out)])
    pngs = sorted(p.name for p in out.glob("proof_*.png"))
    summary = {
        "qa_pass": result.returncode == 0 and bool(pngs),
        "word": word,
        "frames": pngs,
        "stdout": (result.stdout or "")[-2000:],
        "stderr": (result.stderr or "")[-2000:],
        "returncode": result.returncode,
    }
    _write_json(out / "proof_remote.json", summary)
    volume.commit()
    return summary


@app.function(
    gpu="T4",
    timeout=3600,
    memory=16384,
    volumes={VOLUME_MOUNT: volume},
)
def render_caption(style: dict, transcript: dict, luther: bool = True) -> dict:
    work = Path(f"{VOLUME_MOUNT}/render")
    inbox = Path(f"{VOLUME_MOUNT}/inbox")
    work.mkdir(parents=True, exist_ok=True)
    inbox.mkdir(parents=True, exist_ok=True)
    videos = sorted(p for p in inbox.glob("*.mp4"))
    if not videos:
        return {"qa_pass": False, "reason": "C0: inbox Modal vide"}
    video = videos[0]
    style_path = work / "style.json"
    transcript_path = work / "transcript.json"
    layer = work / "layer"
    overlay_out = work / "overlay"
    if layer.exists():
        shutil.rmtree(layer)
    layer.mkdir(parents=True, exist_ok=True)
    overlay_out.mkdir(parents=True, exist_ok=True)
    _write_json(style_path, style)
    _write_json(transcript_path, transcript)
    result = _blender(
        "render",
        ["--style", str(style_path), "--transcript", str(transcript_path), "--out", str(layer)],
    )
    frames = layer / "frames"
    overlay_mp4 = overlay_out / "caption_overlay.mp4"
    ov = subprocess.run(
        [
            sys.executable, "/app/overlay.py",
            "--video", str(video),
            "--frames", str(frames),
            "--out", str(overlay_out),
        ],
        capture_output=True, text=True,
    )
    summary = {
        "blender_returncode": result.returncode,
        "overlay_returncode": ov.returncode,
        "video": video.name,
        "overlay": overlay_mp4.name if overlay_mp4.is_file() else None,
        "blender_stderr": (result.stderr or "")[-2000:],
        "overlay_stderr": (ov.stderr or "")[-2000:],
        "qa_pass": result.returncode == 0 and ov.returncode == 0 and overlay_mp4.is_file(),
    }
    if luther and overlay_mp4.is_file():
        f05 = work / "f05"
        f06 = work / "f06"
        f05.mkdir(parents=True, exist_ok=True)
        f06.mkdir(parents=True, exist_ok=True)
        r5 = subprocess.run(
            [sys.executable, "/app/lac_f05_camouflage.py", "--input", str(overlay_mp4), "--output", str(f05)],
            capture_output=True, text=True,
        )
        f05_mp4 = next(iter(sorted(f05.glob("*.mp4"))), None)
        r6 = subprocess.run(
            [sys.executable, "/app/lac_f06_luther.py", "--input", str(f05_mp4), "--output", str(f06)],
            capture_output=True, text=True,
        ) if f05_mp4 else type("R", (), {"returncode": 1})()
        summary["f05_f06"] = {
            "f05_returncode": r5.returncode,
            "f06_returncode": r6.returncode,
            "f06_mp4": sorted(p.name for p in f06.glob("*.mp4")),
            "qa_pass": r5.returncode == 0 and r6.returncode == 0,
        }
        summary["qa_pass"] = summary["qa_pass"] and summary["f05_f06"]["qa_pass"]
    volume.commit()
    return summary


@app.local_entrypoint()
def main(mode: str = "proof", word: str = "HOE") -> None:
    style_path = HERE.parent.parent / "OUT" / "style.json"
    default_style = HERE / "styles" / "s1.json"
    transcript_path = HERE.parent.parent / "OUT" / "transcript.json"
    if style_path.is_file():
        style = json.loads(style_path.read_text(encoding="utf-8"))
    elif default_style.is_file():
        style = json.loads(default_style.read_text(encoding="utf-8"))
    else:
        style = {}
    if mode == "proof":
        summary = proof.remote(style=style, word=word)
        print(json.dumps(summary, indent=2, default=str))
        return
    if not transcript_path.is_file():
        raise SystemExit("C1: F07_CAPTION/OUT/transcript.json manquant")
    transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
    summary = render_caption.remote(style=style, transcript=transcript, luther=True)
    print(json.dumps(summary, indent=2, default=str))

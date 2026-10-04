"""Modal app lacrimae-dev11-oculus. GHA orchestre. Modal execute. P-CI-1."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import uuid
import urllib.request
import zipfile
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import modal

APP_NAME = "lacrimae-dev11-oculus"
STAGES = ("bootstrap", "oculus", "sanguinor", "calix", "full")
TIMEOUTS_S = {"oculus": 600, "sanguinor": 300, "calix": 900, "full": 1800, "bootstrap": 300}
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "face_landmarker/face_landmarker/float16/1/face_landmarker.task"
)
MODEL_NAME = "face_landmarker.task"
STEM_RE = re.compile(r"[^a-zA-Z0-9._-]+")

REPO_LOCAL = Path(__file__).resolve().parent.parent
REMOTE_REPO = Path("/lacrimae")
REMOTE_MODELS = Path("/models")
REMOTE_CAMPAIGN = Path("/campaign")

app = modal.App(APP_NAME)

models_vol = modal.Volume.from_name("lacrimae-dev11-models", create_if_missing=True)
campaign_vol = modal.Volume.from_name("lacrimae-dev11-campaign", create_if_missing=True)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "libgl1", "libglib2.0-0", "libgomp1")
    .pip_install("mediapipe>=0.10.14", "numpy>=1.26.0")
    .add_local_dir(
        str(REPO_LOCAL),
        remote_path=str(REMOTE_REPO),
        copy=True,
        ignore=[
            "**/.git/**",
            "**/*.mp4",
            "**/*.task",
            "**/__pycache__/**",
            "**/.pytest_cache/**",
        ],
    )
)


def _py() -> str:
    return sys.executable


def _copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _copy_tree_files(src: Path, dst: Path, skip_stems: set[str] | None = None) -> int:
    dst.mkdir(parents=True, exist_ok=True)
    n = 0
    if not src.is_dir():
        return 0
    skip = skip_stems or set()
    for item in src.iterdir():
        if not item.is_file() or item.name == ".gitkeep":
            continue
        if item.stem in skip:
            print(f"skip HOLD {item.name}", file=sys.stderr)
            continue
        shutil.copy2(item, dst / item.name)
        n += 1
    return n


def _safe_stem(name: str) -> str:
    stem = Path(name).stem
    cleaned = STEM_RE.sub("_", stem).strip("._-")
    return cleaned or "clip"


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _ensure_job_request(target: str) -> None:
    dest = REMOTE_REPO / "F01_OCULUS" / "IN" / "job_request.json"
    camp = REMOTE_CAMPAIGN / "IN" / "job_request.json"
    example = REMOTE_REPO / "F01_OCULUS" / "IN" / "job_request.example.json"
    if camp.is_file():
        _copy_file(camp, dest)
    elif not dest.is_file():
        _copy_file(example, dest)
    data = _read_json(dest)
    if target in ("face", "nose", "eyes"):
        data["target"] = target
    data["schema"] = "dev11.job_request.v1"
    data["max_num_faces"] = 1
    _write_json(dest, data)
    _copy_file(dest, camp)


def _place_model_for_f01(src: Path) -> None:
    dest = REMOTE_REPO / "F01_OCULUS" / "CODEBASE" / "models" / MODEL_NAME
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() or dest.is_symlink():
        return
    try:
        dest.symlink_to(src)
    except OSError:
        shutil.copy2(src, dest)


def _ensure_model() -> dict[str, Any]:
    dest = REMOTE_MODELS / MODEL_NAME
    if dest.is_file() and dest.stat().st_size > 1_000_000:
        _place_model_for_f01(dest)
        return {"status": "present", "bytes": dest.stat().st_size, "path": str(dest)}
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".part")
    print(f"F01 model download {MODEL_URL}", file=sys.stderr)
    urllib.request.urlretrieve(MODEL_URL, tmp)
    tmp.replace(dest)
    models_vol.commit()
    _place_model_for_f01(dest)
    return {"status": "downloaded", "bytes": dest.stat().st_size, "path": str(dest)}


def _held_stems() -> set[str]:
    for path in (
        REMOTE_CAMPAIGN / "OUT" / "oculus_report.json",
        REMOTE_REPO / "F01_OCULUS" / "OUT" / "oculus_report.json",
    ):
        if not path.is_file():
            continue
        try:
            data = _read_json(path)
        except json.JSONDecodeError:
            continue
        held = data.get("held") or []
        return {str(s) for s in held}
    return set()


def _ingest_object_uri(object_uri: str) -> list[str]:
    clips_dir = REMOTE_CAMPAIGN / "IN" / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)
    if not object_uri:
        return sorted(p.name for p in clips_dir.glob("*.mp4"))
    parsed = urlparse(object_uri)
    raw_name = Path(parsed.path).name or "clip.mp4"
    tmp_dir = Path("/tmp") / f"dev11_ingest_{uuid.uuid4().hex}"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_file = tmp_dir / raw_name
    print(f"ingest {object_uri}", file=sys.stderr)
    urllib.request.urlretrieve(object_uri, tmp_file)
    written: list[str] = []
    existing = {p.stem for p in clips_dir.glob("*.mp4")}

    def place(src: Path, preferred: str) -> None:
        stem = _safe_stem(preferred)
        candidate = stem
        n = 2
        while candidate in existing:
            candidate = f"{stem}_{n}"
            n += 1
        existing.add(candidate)
        dest = clips_dir / f"{candidate}.mp4"
        shutil.copy2(src, dest)
        written.append(dest.name)

    suffix = tmp_file.suffix.lower()
    if suffix == ".zip":
        with zipfile.ZipFile(tmp_file) as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                name = Path(info.filename).name
                if not name.lower().endswith(".mp4"):
                    continue
                if ".." in Path(info.filename).parts:
                    continue
                extracted = tmp_dir / name
                extracted.write_bytes(zf.read(info))
                place(extracted, name)
    elif suffix == ".mp4":
        place(tmp_file, raw_name)
    else:
        raise RuntimeError(f"object_uri suffix non supporté: {suffix or '(vide)'}")
    campaign_vol.commit()
    return written


def _sync_campaign_in() -> None:
    src_clips = REMOTE_CAMPAIGN / "IN" / "clips"
    held = _held_stems()
    _copy_tree_files(src_clips, REMOTE_REPO / "F01_OCULUS" / "IN" / "clips")
    land = REMOTE_CAMPAIGN / "OUT" / "landmarks"
    cam = REMOTE_CAMPAIGN / "OUT" / "camera_path"
    _copy_tree_files(land, REMOTE_REPO / "F01_OCULUS" / "OUT" / "landmarks")
    _copy_tree_files(land, REMOTE_REPO / "F02_SANGUINOR" / "IN" / "landmarks", skip_stems=held)
    _copy_tree_files(cam, REMOTE_REPO / "F02_SANGUINOR" / "OUT" / "camera_path")
    _copy_tree_files(cam, REMOTE_REPO / "F03_CALIX" / "IN" / "camera_path")
    camp_clips = list((REMOTE_CAMPAIGN / "IN" / "clips").glob("*.mp4"))
    if camp_clips:
        _copy_tree_files(src_clips, REMOTE_REPO / "F02_SANGUINOR" / "IN" / "clips", skip_stems=held)
        _copy_tree_files(src_clips, REMOTE_REPO / "F03_CALIX" / "IN" / "clips")
    for name in ("oculus_report.json",):
        src = REMOTE_CAMPAIGN / "OUT" / name
        if src.is_file():
            _copy_file(src, REMOTE_REPO / "F01_OCULUS" / "OUT" / name)
    for name in ("sanguinor_report.json",):
        src = REMOTE_CAMPAIGN / "OUT" / name
        if src.is_file():
            _copy_file(src, REMOTE_REPO / "F02_SANGUINOR" / "OUT" / name)
    for name in ("calix_manifest.json", "calix_report.json"):
        src = REMOTE_CAMPAIGN / "OUT" / name
        if src.is_file():
            _copy_file(src, REMOTE_REPO / "F03_CALIX" / "OUT" / name)
    tracked = REMOTE_CAMPAIGN / "OUT" / "tracked"
    if tracked.is_dir():
        _copy_tree_files(tracked, REMOTE_REPO / "F03_CALIX" / "OUT" / "tracked")


def _persist_campaign_out() -> None:
    out = REMOTE_CAMPAIGN / "OUT"
    out.mkdir(parents=True, exist_ok=True)
    _copy_tree_files(
        REMOTE_REPO / "F01_OCULUS" / "OUT" / "landmarks",
        out / "landmarks",
    )
    _copy_tree_files(
        REMOTE_REPO / "F02_SANGUINOR" / "OUT" / "camera_path",
        out / "camera_path",
    )
    _copy_tree_files(
        REMOTE_REPO / "F03_CALIX" / "OUT" / "tracked",
        out / "tracked",
    )
    for src in (
        REMOTE_REPO / "F01_OCULUS" / "OUT" / "oculus_report.json",
        REMOTE_REPO / "F02_SANGUINOR" / "OUT" / "sanguinor_report.json",
        REMOTE_REPO / "F03_CALIX" / "OUT" / "calix_manifest.json",
        REMOTE_REPO / "F03_CALIX" / "OUT" / "calix_report.json",
    ):
        if src.is_file():
            _copy_file(src, out / src.name)
    campaign_vol.commit()


def _load_report(path: Path) -> Any | None:
    if not path.is_file():
        return None
    try:
        return _read_json(path)
    except json.JSONDecodeError:
        return {"error": "json invalide", "path": str(path)}


def _run(cmd: list[str]) -> int:
    print("+", " ".join(cmd), file=sys.stderr)
    return subprocess.call(cmd, cwd=str(REMOTE_REPO))


def _custos(frigate: str, mode: str) -> int:
    return _run(
        [
            _py(),
            str(REMOTE_REPO / "LAC_CUSTOS.py"),
            "--frigate",
            frigate,
            "--mode",
            mode,
            "--root",
            str(REMOTE_REPO),
        ]
    )


def _engine(frigate: str) -> int:
    engines = {
        "F01_OCULUS": REMOTE_REPO / "F01_OCULUS" / "CODEBASE" / "f01_oculus.py",
        "F02_SANGUINOR": REMOTE_REPO / "F02_SANGUINOR" / "CODEBASE" / "f02_sanguinor.py",
        "F03_CALIX": REMOTE_REPO / "F03_CALIX" / "CODEBASE" / "f03_calix.py",
    }
    cmd = [
        _py(),
        str(engines[frigate]),
        "--in",
        str(REMOTE_REPO / frigate / "IN"),
        "--out",
        str(REMOTE_REPO / frigate / "OUT"),
    ]
    if frigate == "F02_SANGUINOR":
        cmd.extend(["--config", str(REMOTE_REPO / "CONFIG" / "camera_defaults.json")])
    return _run(cmd)


def _run_full() -> int:
    return _run([_py(), str(REMOTE_REPO / "LAC_RUN.py"), "run"])


def _collect() -> dict[str, Any]:
    tracked_dir = REMOTE_REPO / "F03_CALIX" / "OUT" / "tracked"
    tracked = sorted(p.name for p in tracked_dir.glob("*.mp4")) if tracked_dir.is_dir() else []
    return {
        "oculus_report": _load_report(REMOTE_REPO / "F01_OCULUS" / "OUT" / "oculus_report.json"),
        "sanguinor_report": _load_report(
            REMOTE_REPO / "F02_SANGUINOR" / "OUT" / "sanguinor_report.json"
        ),
        "calix_report": _load_report(REMOTE_REPO / "F03_CALIX" / "OUT" / "calix_report.json"),
        "calix_manifest": _load_report(REMOTE_REPO / "F03_CALIX" / "OUT" / "calix_manifest.json"),
        "tracked": tracked,
        "model": str(REMOTE_MODELS / MODEL_NAME),
        "model_present": (REMOTE_MODELS / MODEL_NAME).is_file(),
    }


@app.function(
    image=image,
    volumes={"/models": models_vol, "/campaign": campaign_vol},
    timeout=1800,
    cpu=2.0,
    memory=8192,
)
def run_stage(stage: str, object_uri: str = "", target: str = "face") -> dict[str, Any]:
    os.chdir(str(REMOTE_REPO))
    if stage not in STAGES:
        return {"stage": stage, "exit_code": 2, "error": f"stage inconnu: {stage}"}
    result: dict[str, Any] = {"stage": stage, "app": APP_NAME, "timeouts_s": TIMEOUTS_S}
    try:
        result["model"] = _ensure_model()
        if stage == "bootstrap":
            result["exit_code"] = 0
            return result
        ingested = _ingest_object_uri(object_uri)
        result["ingested"] = ingested
        _ensure_job_request(target)
        _sync_campaign_in()
        code = 0
        if stage == "full":
            code = _run_full()
        elif stage == "oculus":
            code = _custos("F01_OCULUS", "check-in")
            if code == 0:
                code = _engine("F01_OCULUS")
            if code == 0:
                code = _custos("F01_OCULUS", "check-out")
        elif stage == "sanguinor":
            code = _custos("F02_SANGUINOR", "check-in")
            if code == 0:
                code = _engine("F02_SANGUINOR")
            if code == 0:
                code = _custos("F02_SANGUINOR", "check-out")
        elif stage == "calix":
            code = _custos("F03_CALIX", "check-in")
            if code == 0:
                code = _engine("F03_CALIX")
            if code == 0:
                code = _custos("F03_CALIX", "check-out")
        _persist_campaign_out()
        result["exit_code"] = int(code)
        result.update(_collect())
        return result
    except Exception as exc:
        result["exit_code"] = 1
        result["error"] = str(exc)
        try:
            _persist_campaign_out()
            result.update(_collect())
        except Exception:
            pass
        return result


@app.local_entrypoint()
def main(stage: str = "full", object_uri: str = "", target: str = "face") -> None:
    if stage not in STAGES:
        raise SystemExit(f"stage inconnu: {stage}. Choix: {', '.join(STAGES)}")
    if target not in ("face", "nose", "eyes"):
        raise SystemExit(f"target invalide: {target}")
    print(
        f"{APP_NAME} stage={stage} target={target} uri={'yes' if object_uri else 'no'}",
        file=sys.stderr,
    )
    payload = run_stage.remote(stage, object_uri, target)
    print(json.dumps(payload, indent=2, default=str))
    code = int(payload.get("exit_code", 1))
    if code != 0:
        raise SystemExit(code)

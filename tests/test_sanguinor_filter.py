"""Groupe 2 — deadzone / 1€ / hold-last / clamp, sans video."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODE = ROOT / "F02_SANGUINOR" / "CODEBASE"
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

from camera import build_camera_path, crop_for, load_config  # noqa: E402
from one_euro import OneEuroFilter  # noqa: E402

CFG = json.loads((ROOT / "CONFIG" / "camera_defaults.json").read_text())


def _land(frames: list[dict], width: int = 1080, height: int = 1920) -> dict:
    return {
        "schema": "dev11.landmarks.v1",
        "stem": "clip_001",
        "source_clip": "clips/clip_001.mp4",
        "target": "face",
        "width": width,
        "height": height,
        "fps": 30,
        "frame_count": len(frames),
        "frames": frames,
    }


def test_one_euro_no_nan() -> None:
    filt = OneEuroFilter(mincutoff=1.0, beta=0.007)
    y = None
    for i in range(30):
        y = filt(i / 30.0, 0.5 + (0.01 if i % 2 else -0.01))
        assert y == y
    assert y is not None


def test_deadzone_camera_immobile() -> None:
    frames = []
    for i in range(8):
        frames.append(
            {
                "i": i,
                "t_s": i / 30.0,
                "detected": True,
                "target": {"x": 0.50 + 0.001 * (i % 2), "y": 0.40},
                "bbox": {"x": 0.3, "y": 0.2, "w": 0.4, "h": 0.3},
            }
        )
    path = build_camera_path(_land(frames), CFG)
    cxs = [f["cx"] for f in path["frames"]]
    assert max(cxs) - min(cxs) < 1e-9
    assert all(f["held"] is False for f in path["frames"])


def test_hold_last_no_jump_to_center() -> None:
    frames = [
        {"i": 0, "t_s": 0.0, "detected": True, "target": {"x": 0.62, "y": 0.31}, "bbox": None},
        {"i": 1, "t_s": 0.033, "detected": True, "target": {"x": 0.62, "y": 0.31}, "bbox": None},
        {"i": 2, "t_s": 0.066, "detected": False, "target": None, "bbox": None},
        {"i": 3, "t_s": 0.099, "detected": False, "target": None, "bbox": None},
    ]
    path = build_camera_path(_land(frames), CFG)
    assert path["frames"][2]["held"] is True
    assert path["frames"][3]["held"] is True
    assert path["frames"][2]["cx"] == path["frames"][1]["cx"]
    assert path["frames"][3]["cy"] == path["frames"][1]["cy"]
    assert path["frames"][2]["cx"] != 0.5


def test_crop_always_in_bounds() -> None:
    for cx, cy, zoom in ((0.0, 0.0, 1.0), (1.0, 1.0, 1.8), (0.5, 0.5, 1.2), (0.9, 0.1, 1.5)):
        crop = crop_for(1080, 1920, cx, cy, zoom, 0.5)
        assert crop["x"] >= 0 and crop["y"] >= 0
        assert crop["x"] + crop["w"] <= 1080
        assert crop["y"] + crop["h"] <= 1920
        assert crop["w"] * 16 == crop["h"] * 9


def test_zoom_never_below_one() -> None:
    frames = [
        {"i": 0, "t_s": 0.0, "detected": True, "target": {"x": 0.5, "y": 0.4}, "bbox": {"x": 0.1, "y": 0.1, "w": 0.8, "h": 0.9}},
        {"i": 1, "t_s": 0.033, "detected": True, "target": {"x": 0.5, "y": 0.4}, "bbox": {"x": 0.1, "y": 0.1, "w": 0.8, "h": 0.9}},
    ]
    path = build_camera_path(_land(frames), CFG)
    assert all(f["zoom"] >= 1.0 for f in path["frames"])


def test_load_config_overrides() -> None:
    cfg = load_config(CFG, {"deadzone_norm": 0.01})
    assert cfg["deadzone_norm"] == 0.01
    assert cfg["zoom_min"] == CFG["zoom_min"]


def test_engine_writes_path(tmp_path: Path, monkeypatch) -> None:
    import subprocess

    land = json.loads((ROOT / "tests" / "fixtures" / "landmarks.valid.json").read_text())
    in_dir = tmp_path / "IN"
    out_dir = tmp_path / "OUT"
    (in_dir / "landmarks").mkdir(parents=True)
    (in_dir / "clips").mkdir()
    (in_dir / "landmarks" / "clip_001.json").write_text(json.dumps(land), encoding="utf-8")
    cmd = [
        sys.executable,
        str(CODE / "f02_sanguinor.py"),
        "--in",
        str(in_dir),
        "--out",
        str(out_dir),
        "--config",
        str(ROOT / "CONFIG" / "camera_defaults.json"),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    out = json.loads((out_dir / "camera_path" / "clip_001.json").read_text())
    assert out["schema"] == "dev11.camera_path.v1"
    assert out["frame_count"] == 3
    assert out["frames"][2]["held"] is True
    report = json.loads((out_dir / "sanguinor_report.json").read_text())
    assert report["schema"] == "dev11.sanguinor_report.v1"
    assert report["stems"][0]["verdict"] == "PASS"

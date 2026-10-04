#!/usr/bin/env python3
"""F02 SANGUINOR — landmarks.v1 → camera_path.v1. Zéro MediaPipe."""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from camera import build_camera_path, load_config  # noqa: E402


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def jitter_median(frames: list[dict[str, Any]]) -> float:
    deltas: list[float] = []
    prev = None
    for frame in frames:
        cx, cy = float(frame["cx"]), float(frame["cy"])
        if prev is not None:
            deltas.append(((cx - prev[0]) ** 2 + (cy - prev[1]) ** 2) ** 0.5)
        prev = (cx, cy)
    if not deltas:
        return 0.0
    return float(statistics.median(deltas))


def run_stem(land_path: Path, cfg: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    land = _read_json(land_path)
    path = build_camera_path(land, cfg)
    held_n = sum(1 for f in path["frames"] if f.get("held"))
    return path, {
        "stem": path.get("stem"),
        "jitter_median_norm": jitter_median(path["frames"]),
        "held_frames": held_n,
        "verdict": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="F02 SANGUINOR — camera path")
    parser.add_argument("--in", dest="in_dir", required=True)
    parser.add_argument("--out", dest="out_dir", required=True)
    parser.add_argument("--config", dest="config", default="CONFIG/camera_defaults.json")
    args = parser.parse_args()
    in_dir = Path(args.in_dir)
    out_dir = Path(args.out_dir)
    cfg_raw = _read_json(Path(args.config))
    req_path = in_dir / "camera_request.json"
    overrides = None
    campaign_id = None
    if req_path.is_file():
        req = _read_json(req_path)
        campaign_id = req.get("campaign_id")
        overrides = req.get("overrides") if isinstance(req.get("overrides"), dict) else None
    cfg = load_config(cfg_raw, overrides)
    land_dir = in_dir / "landmarks"
    out_cam = out_dir / "camera_path"
    out_cam.mkdir(parents=True, exist_ok=True)
    stems: list[dict[str, Any]] = []
    held: list[str] = []
    refused: list[str] = []
    files = sorted(p for p in land_dir.glob("*.json") if p.name != ".gitkeep")
    if not files:
        print("F02: aucun landmarks IN", file=sys.stderr)
        return 1
    for land_path in files:
        try:
            path, row = run_stem(land_path, cfg)
            _write_json(out_cam / f"{land_path.stem}.json", path)
            stems.append(row)
        except Exception as exc:
            refused.append(land_path.stem)
            print(f"F02 REFUS {land_path.stem}: {exc}", file=sys.stderr)
    report = {
        "schema": "dev11.sanguinor_report.v1",
        "campaign_id": campaign_id,
        "stems": stems,
        "held": held,
        "refused": refused,
    }
    _write_json(out_dir / "sanguinor_report.json", report)
    return 1 if refused else 0


if __name__ == "__main__":
    raise SystemExit(main())

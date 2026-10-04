#!/usr/bin/env python3
"""F01 OCULUS — MediaPipe Face Landmarker si dispo, sinon HOLD detect=false.

Lit uniquement --in. Ecrit uniquement --out. Jamais une sœur OUT.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SHARED = ROOT / "SHARED" / "CODEBASE"
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))

from ffmpeg_io import FFmpegMissing, iter_rgb_frames, probe  # noqa: E402

LANDMARK_IDS = {
    "face_center": ["oval_mean"],
    "nose": [4],
    "eyes": [468, 473],
}
FACE_OVAL = (
    10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
    397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
    172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109,
)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _mean_xy(points: list[tuple[float, float]]) -> tuple[float, float]:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def _bbox(points: list[tuple[float, float]]) -> dict[str, float]:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    return {"x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0}


def _lm_xy(lm: Any) -> tuple[float, float]:
    return float(lm.x), float(lm.y)


def target_from_landmarks(lms: list[Any], target: str) -> tuple[dict[str, float], dict[str, float]]:
    oval = [_lm_xy(lms[i]) for i in FACE_OVAL if i < len(lms)]
    if not oval:
        oval = [_lm_xy(p) for p in lms]
    bbox = _bbox(oval)
    if target == "nose" and len(lms) > 4:
        x, y = _lm_xy(lms[4])
    elif target == "eyes":
        pts = []
        for idx in (468, 473, 33, 263):
            if idx < len(lms):
                pts.append(_lm_xy(lms[idx]))
        if not pts:
            x, y = _mean_xy(oval)
        else:
            x, y = _mean_xy(pts)
    else:
        x, y = _mean_xy(oval)
    x = min(1.0, max(0.0, x))
    y = min(1.0, max(0.0, y))
    return {"x": x, "y": y}, bbox


def try_landmarker(job: dict[str, Any]) -> Any | None:
    try:
        import mediapipe as mp  # type: ignore
        from mediapipe.tasks import python as mp_python  # type: ignore
        from mediapipe.tasks.python import vision  # type: ignore
    except Exception:
        return None
    model = Path(__file__).resolve().parent / "models" / "face_landmarker.task"
    env_model = Path.cwd() / "models" / "face_landmarker.task"
    for candidate in (model, env_model, Path("/models/face_landmarker.task")):
        if candidate.is_file():
            model = candidate
            break
    else:
        print("F01: modele face_landmarker.task absent — HOLD detected=false", file=sys.stderr)
        return None
    BaseOptions = mp_python.BaseOptions
    FaceLandmarker = vision.FaceLandmarker
    FaceLandmarkerOptions = vision.FaceLandmarkerOptions
    VisionRunningMode = vision.RunningMode
    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(model)),
        running_mode=VisionRunningMode.VIDEO,
        num_faces=int(job.get("max_num_faces") or 1),
        min_face_detection_confidence=float(job.get("min_detection_confidence") or 0.5),
        min_face_presence_confidence=float(job.get("min_detection_confidence") or 0.5),
        min_tracking_confidence=float(job.get("min_tracking_confidence") or 0.5),
        output_face_blendshapes=False,
        output_facial_transformation_matrixes=False,
    )
    return FaceLandmarker.create_from_options(options)


def detect_frames_mediapipe(
    clip: Path,
    meta: dict[str, Any],
    job: dict[str, Any],
    landmarker: Any,
) -> list[dict[str, Any]]:
    import numpy as np  # type: ignore
    import mediapipe as mp  # type: ignore

    width, height = meta["width"], meta["height"]
    fps = meta["fps"] or 30.0
    sample_n = max(1, int(job.get("sample_every_n_frames") or 1))
    target = job.get("target") or "face"
    frames: list[dict[str, Any]] = []
    i = 0
    mp_image_mod = mp.Image
    mp_format = mp.ImageFormat.SRGB
    for raw in iter_rgb_frames(clip, width, height):
        t_s = i / fps if fps else 0.0
        detected = False
        tgt = None
        bbox = None
        if i % sample_n == 0:
            arr = np.frombuffer(raw, dtype=np.uint8).reshape((height, width, 3)).copy()
            ts_ms = int(round(t_s * 1000))
            try:
                result = landmarker.detect_for_video(mp_image_mod(image_format=mp_format, data=arr), ts_ms)
            except Exception:
                result = None
            if result and result.face_landmarks:
                lms = result.face_landmarks[0]
                tgt, bbox = target_from_landmarks(lms, target)
                detected = True
        frames.append({"i": i, "t_s": round(t_s, 6), "detected": detected, "target": tgt, "bbox": bbox})
        i += 1
    return frames


def hold_frames(meta: dict[str, Any]) -> list[dict[str, Any]]:
    fps = meta["fps"] or 30.0
    duration = meta["duration_s"] or 0.0
    count = meta["frame_count"]
    if not count:
        count = int(math.floor(duration * fps + 0.5)) if fps and duration else 0
    count = max(0, int(count))
    frames = []
    for i in range(count):
        t_s = i / fps if fps else 0.0
        frames.append({"i": i, "t_s": round(t_s, 6), "detected": False, "target": None, "bbox": None})
    return frames


def detect_ratio(frames: list[dict[str, Any]]) -> float:
    if not frames:
        return 0.0
    return sum(1 for f in frames if f.get("detected")) / len(frames)


def longest_gap(frames: list[dict[str, Any]]) -> int:
    gap = longest = 0
    for frame in frames:
        if frame.get("detected"):
            gap = 0
        else:
            gap += 1
            longest = max(longest, gap)
    return longest


def process_clip(clip: Path, job: dict[str, Any], landmarker: Any) -> dict[str, Any]:
    meta = probe(clip)
    target = job.get("target") or "face"
    if landmarker is not None:
        frames = detect_frames_mediapipe(clip, meta, job, landmarker)
    else:
        frames = hold_frames(meta)
        if not frames:
            frames = [{"i": 0, "t_s": 0.0, "detected": False, "target": None, "bbox": None}]
    return {
        "schema": "dev11.landmarks.v1",
        "stem": clip.stem,
        "source_clip": f"clips/{clip.name}",
        "target": target,
        "landmark_ids": LANDMARK_IDS,
        "width": meta["width"],
        "height": meta["height"],
        "fps": meta["fps"],
        "frame_count": len(frames),
        "duration_s": meta["duration_s"],
        "frames": frames,
        "video_codec": meta.get("video_codec"),
        "backend": "mediapipe" if landmarker is not None else "hold",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="F01 OCULUS — landmarks")
    parser.add_argument("--in", dest="in_dir", required=True)
    parser.add_argument("--out", dest="out_dir", required=True)
    args = parser.parse_args()
    in_dir = Path(args.in_dir)
    out_dir = Path(args.out_dir)
    job_path = in_dir / "job_request.json"
    if not job_path.is_file():
        print("F01: job_request.json absent", file=sys.stderr)
        return 1
    job = _read_json(job_path)
    clips = sorted(p for p in (in_dir / "clips").glob("*.mp4"))
    if not clips:
        print("F01: aucun clip", file=sys.stderr)
        return 1
    try:
        landmarker = try_landmarker(job)
    except FFmpegMissing as exc:
        print(f"F01: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"F01: landmarker init fail, HOLD: {exc}", file=sys.stderr)
        landmarker = None
    out_lm = out_dir / "landmarks"
    out_lm.mkdir(parents=True, exist_ok=True)
    stems: list[dict[str, Any]] = []
    held: list[str] = []
    refused: list[str] = []
    min_ratio = 0.85
    for clip in clips:
        try:
            data = process_clip(clip, job, landmarker)
        except Exception as exc:
            refused.append(clip.stem)
            print(f"F01 REFUS {clip.stem}: {exc}", file=sys.stderr)
            continue
        _write_json(out_lm / f"{clip.stem}.json", data)
        ratio = detect_ratio(data["frames"])
        gap = longest_gap(data["frames"])
        verdict = "PASS"
        if ratio < min_ratio:
            verdict = "HOLD"
            held.append(clip.stem)
        stems.append(
            {
                "stem": clip.stem,
                "detected_ratio": round(ratio, 4),
                "longest_gap_frames": gap,
                "verdict": verdict,
                "backend": data.get("backend"),
            }
        )
    report = {
        "schema": "dev11.oculus_report.v1",
        "campaign_id": job.get("campaign_id"),
        "stems": stems,
        "held": held,
        "refused": refused,
    }
    _write_json(out_dir / "oculus_report.json", report)
    if landmarker is not None:
        try:
            landmarker.close()
        except Exception:
            pass
    return 1 if refused else 0


if __name__ == "__main__":
    raise SystemExit(main())

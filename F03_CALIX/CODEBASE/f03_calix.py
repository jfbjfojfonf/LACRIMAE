#!/usr/bin/env python3
"""F03 CALIX — applique camera_path. Crop 9:16 + audio copy. Pas de detection."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Iterator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SHARED = ROOT / "SHARED" / "CODEBASE"
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))

from ffmpeg_io import FFmpegMissing, iter_rgb_frames, probe, encode_rgb_stream  # noqa: E402


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def crop_scale_frame(raw: bytes, src_w: int, src_h: int, crop: dict[str, int], out_w: int, out_h: int) -> bytes:
    x, y, w, h = int(crop["x"]), int(crop["y"]), int(crop["w"]), int(crop["h"])
    if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > src_w or y + h > src_h:
        raise RuntimeError(f"crop illegal: {crop} source {src_w}x{src_h}")
    src = memoryview(raw)
    row = src_w * 3
    cropped = bytearray(w * h * 3)
    for row_i in range(h):
        src_off = ((y + row_i) * src_w + x) * 3
        dst_off = row_i * w * 3
        cropped[dst_off : dst_off + w * 3] = src[src_off : src_off + w * 3]
    if w == out_w and h == out_h:
        return bytes(cropped)
    try:
        import numpy as np  # type: ignore
    except Exception as exc:
        raise RuntimeError("numpy requis pour scale") from exc
    img = np.frombuffer(cropped, dtype=np.uint8).reshape((h, w, 3))
    ys = (np.arange(out_h) * (h / out_h)).astype(np.int32)
    xs = (np.arange(out_w) * (w / out_w)).astype(np.int32)
    ys = np.clip(ys, 0, h - 1)
    xs = np.clip(xs, 0, w - 1)
    scaled = img[ys[:, None], xs[None, :], :]
    return scaled.tobytes()


def apply_path(clip: Path, path_data: dict[str, Any], out_mp4: Path) -> dict[str, Any]:
    meta = probe(clip)
    width, height = meta["width"], meta["height"]
    fps = float(path_data.get("fps") or meta["fps"] or 30.0)
    out_w = int(path_data.get("output_width") or 1080)
    out_h = int(path_data.get("output_height") or 1920)
    frames_path = path_data["frames"]
    src_iter = iter_rgb_frames(clip, width, height)

    def gen() -> Iterator[bytes]:
        for i, raw in enumerate(src_iter):
            if i >= len(frames_path):
                break
            crop = frames_path[i]["crop"]
            yield crop_scale_frame(raw, width, height, crop, out_w, out_h)

    has_audio = bool(meta.get("has_audio"))
    encode_rgb_stream(out_mp4, gen(), out_w, out_h, fps, clip if has_audio else None, has_audio)
    return {
        "stem": path_data.get("stem") or clip.stem,
        "file": f"tracked/{out_mp4.name}",
        "duration_s": meta.get("duration_s"),
        "audio": "copy" if has_audio else "none",
        "sha256": sha256_file(out_mp4),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="F03 CALIX — crop + mux")
    parser.add_argument("--in", dest="in_dir", required=True)
    parser.add_argument("--out", dest="out_dir", required=True)
    args = parser.parse_args()
    in_dir = Path(args.in_dir)
    out_dir = Path(args.out_dir)
    camp = None
    req = in_dir / "calix_request.json"
    if req.is_file():
        camp = _read_json(req).get("campaign_id")
    paths = sorted(p for p in (in_dir / "camera_path").glob("*.json"))
    if not paths:
        print("F03: aucun camera_path", file=sys.stderr)
        return 1
    tracked = out_dir / "tracked"
    tracked.mkdir(parents=True, exist_ok=True)
    stems: list[dict[str, Any]] = []
    refused: list[str] = []
    try:
        for path_file in paths:
            data = _read_json(path_file)
            clip = in_dir / "clips" / f"{path_file.stem}.mp4"
            if not clip.is_file():
                refused.append(path_file.stem)
                print(f"F03 REFUS {path_file.stem}: clip absent", file=sys.stderr)
                continue
            out_mp4 = tracked / f"{path_file.stem}.mp4"
            try:
                row = apply_path(clip, data, out_mp4)
                row["verdict"] = "PASS"
                stems.append(row)
            except (FFmpegMissing, RuntimeError) as exc:
                refused.append(path_file.stem)
                print(f"F03 REFUS {path_file.stem}: {exc}", file=sys.stderr)
    except FFmpegMissing as exc:
        print(f"F03: {exc}", file=sys.stderr)
        return 1
    if refused:
        for p in tracked.glob("*.mp4"):
            pass
        manifest = {
            "schema": "dev11.calix_manifest.v1",
            "campaign_id": camp,
            "output_width": 1080,
            "output_height": 1920,
            "stems": stems,
        }
        _write_json(out_dir / "calix_manifest.json", manifest)
        report = {
            "schema": "dev11.calix_report.v1",
            "campaign_id": camp,
            "stems": stems,
            "held": [],
            "refused": refused,
        }
        _write_json(out_dir / "calix_report.json", report)
        return 1
    if not stems:
        print("F03: zero stem", file=sys.stderr)
        return 1
    out_w = 1080
    out_h = 1920
    first = _read_json(paths[0])
    out_w = int(first.get("output_width") or out_w)
    out_h = int(first.get("output_height") or out_h)
    manifest = {
        "schema": "dev11.calix_manifest.v1",
        "campaign_id": camp,
        "output_width": out_w,
        "output_height": out_h,
        "stems": [{k: s[k] for k in ("stem", "file", "duration_s", "audio", "sha256") if k in s} for s in stems],
    }
    _write_json(out_dir / "calix_manifest.json", manifest)
    report = {
        "schema": "dev11.calix_report.v1",
        "campaign_id": camp,
        "stems": stems,
        "held": [],
        "refused": refused,
    }
    _write_json(out_dir / "calix_report.json", report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

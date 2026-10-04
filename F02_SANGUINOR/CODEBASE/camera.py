#!/usr/bin/env python3
"""Camera virtuelle 9:16 : deadzone, 1€, hold-last, zoom, clamp."""
from __future__ import annotations

from typing import Any

from one_euro import OneEuroFilter


def load_config(raw: dict[str, Any], overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    cfg = dict(raw)
    if overrides:
        cfg.update({k: v for k, v in overrides.items() if v is not None})
    return cfg


def max_916_k(width: int, height: int) -> int:
    k = min(width // 9, height // 16)
    if k % 2:
        k -= 1
    return max(2, k)


def crop_for(width: int, height: int, cx: float, cy: float, zoom: float, y_anchor: float) -> dict[str, int]:
    zoom = max(1.0, float(zoom))
    k_max = max_916_k(width, height)
    k = int(k_max / zoom)
    if k % 2:
        k -= 1
    k = max(2, k)
    cw, ch = 9 * k, 16 * k
    while (cw > width or ch > height) and k >= 2:
        k -= 2
        cw, ch = 9 * k, 16 * k
    if k < 2:
        k = 2
        cw, ch = 9 * k, 16 * k
        cw = min(cw, width - (width % 2))
        ch = min(ch, height - (height % 2))
    cx_px = float(cx) * width
    cy_px = float(cy) * height
    x = int(round(cx_px - cw / 2.0))
    y = int(round(cy_px - y_anchor * ch))
    x = max(0, min(x, width - cw))
    y = max(0, min(y, height - ch))
    return {"x": x, "y": y, "w": cw, "h": ch}


def zoom_from_bbox(bbox: dict[str, Any] | None, zoom_min: float, zoom_max: float) -> float:
    if not isinstance(bbox, dict):
        return zoom_min
    h = bbox.get("h")
    if not isinstance(h, (int, float)) or h <= 0:
        return zoom_min
    face_h = float(h)
    desired = 0.42 / face_h
    return max(zoom_min, min(zoom_max, desired))


def build_camera_path(landmarks: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    frames_in = landmarks["frames"]
    width = int(landmarks["width"])
    height = int(landmarks["height"])
    target_name = landmarks.get("target") or "face"
    y_anchor = 0.5
    if target_name == "eyes":
        y_anchor = float(cfg.get("eyes_y_anchor", 0.33))
    deadzone = float(cfg.get("deadzone_norm", 0.04))
    zoom_min = float(cfg.get("zoom_min", 1.0))
    zoom_max = float(cfg.get("zoom_max", 1.85))
    zoom_delta = float(cfg.get("zoom_max_delta_per_s", 0.35))
    hold_last = bool(cfg.get("hold_last", True))
    fx = OneEuroFilter(
        mincutoff=float(cfg.get("one_euro_mincutoff", 1.0)),
        beta=float(cfg.get("one_euro_beta", 0.007)),
        dcutoff=float(cfg.get("one_euro_dcutoff", 1.0)),
    )
    fy = OneEuroFilter(
        mincutoff=float(cfg.get("one_euro_mincutoff", 1.0)),
        beta=float(cfg.get("one_euro_beta", 0.007)),
        dcutoff=float(cfg.get("one_euro_dcutoff", 1.0)),
    )
    out_frames: list[dict[str, Any]] = []
    cam_x: float | None = None
    cam_y: float | None = None
    last_zoom = zoom_min
    last_t = 0.0
    for frame in frames_in:
        t = float(frame.get("t_s") or 0.0)
        dt = max(1e-6, t - last_t) if out_frames else 1e-6
        detected = bool(frame.get("detected"))
        held = False
        raw_x: float | None = None
        raw_y: float | None = None
        if detected:
            tgt = frame.get("target") or {}
            raw_x = float(tgt["x"])
            raw_y = float(tgt["y"])
        elif hold_last and cam_x is not None and cam_y is not None:
            held = True
            raw_x, raw_y = cam_x, cam_y
        else:
            held = True
            raw_x, raw_y = 0.5, 0.5
        if cam_x is None or cam_y is None:
            cam_x, cam_y = raw_x, raw_y
            fx(t, raw_x)
            fy(t, raw_y)
        elif held:
            pass
        else:
            dist = ((raw_x - cam_x) ** 2 + (raw_y - cam_y) ** 2) ** 0.5
            if dist <= deadzone:
                fx(t, cam_x)
                fy(t, cam_y)
            else:
                cam_x = fx(t, raw_x)
                cam_y = fy(t, raw_y)
        want_zoom = zoom_from_bbox(frame.get("bbox") if detected else None, zoom_min, zoom_max)
        max_step = zoom_delta * dt
        if want_zoom > last_zoom + max_step:
            last_zoom = last_zoom + max_step
        elif want_zoom < last_zoom - max_step:
            last_zoom = last_zoom - max_step
        else:
            last_zoom = want_zoom
        last_zoom = max(zoom_min, min(zoom_max, last_zoom))
        crop = crop_for(width, height, cam_x, cam_y, last_zoom, y_anchor)
        out_frames.append(
            {
                "i": int(frame.get("i", len(out_frames))),
                "t_s": t,
                "cx": cam_x,
                "cy": cam_y,
                "zoom": last_zoom,
                "crop": crop,
                "held": held,
            }
        )
        last_t = t
    return {
        "schema": "dev11.camera_path.v1",
        "stem": landmarks.get("stem"),
        "source_clip": landmarks.get("source_clip"),
        "target": target_name,
        "width": width,
        "height": height,
        "output_width": int(cfg.get("output_width", 1080)),
        "output_height": int(cfg.get("output_height", 1920)),
        "fps": landmarks.get("fps"),
        "frame_count": len(out_frames),
        "frames": out_frames,
    }

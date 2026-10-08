#!/usr/bin/env python3
"""Contrats F07_CAPTION : transcript / style s1 / proof. Zero I/O reseau."""
from __future__ import annotations

from pathlib import Path

MOTION_VALUES = ("pop-in", "bounce", "slide")
CANVAS_VALUES = ("9:16", "16:9", "1:1")
CANVAS_SIZE = {
    "9:16": (1080, 1920),
    "16:9": (1920, 1080),
    "1:1": (1080, 1080),
}
DEFAULT_FONT = "Montserrat-ExtraBold.ttf"
STYLE_SCHEMA = "dev11.caption.style.v1"
TRANSCRIPT_SCHEMA = "dev11.caption.transcript.v1"
PROOF_SCHEMA = "dev11.caption.proof.v1"


def _clamp(value, lo: float, hi: float, default: float) -> float:
    try:
        n = float(value)
    except (TypeError, ValueError):
        return default
    if n != n:
        return default
    return min(hi, max(lo, n))


def _str(value, default: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default


def normalize_style(raw: dict | None) -> dict:
    src = raw if isinstance(raw, dict) else {}
    position = src.get("position") if isinstance(src.get("position"), dict) else {}
    outline = src.get("outline") if isinstance(src.get("outline"), dict) else {}
    glow = src.get("glow") if isinstance(src.get("glow"), dict) else {}
    motion = src.get("motion") if src.get("motion") in MOTION_VALUES else "pop-in"
    canvas = src.get("canvas") if src.get("canvas") in CANVAS_VALUES else "9:16"
    return {
        "schema_version": STYLE_SCHEMA,
        "id": _str(src.get("id"), "s1"),
        "font": _str(src.get("font"), DEFAULT_FONT),
        "position": {
            "x_pct": _clamp(position.get("x_pct"), 0, 100, 50),
            "y_pct": _clamp(position.get("y_pct"), 0, 100, 78),
        },
        "size": int(_clamp(src.get("size"), 12, 240, 72)),
        "color": _str(src.get("color"), "#FFFFFF"),
        "outline": {
            "width": _clamp(outline.get("width"), 0, 24, 4),
            "color": _str(outline.get("color"), "#000000"),
        },
        "glow": {
            "intensity": _clamp(glow.get("intensity"), 0, 5, 1.2),
            "color": _str(glow.get("color"), "#FFFFFF"),
        },
        "motion": motion,
        "motion_speed": round(_clamp(src.get("motion_speed"), 0.25, 3.0, 1.0), 2),
        "canvas": canvas,
    }


def parse_transcript(raw: dict | None) -> dict:
    src = raw if isinstance(raw, dict) else {}
    words = []
    for item in src.get("words") or []:
        if not isinstance(item, dict):
            continue
        word = str(item.get("word") or "").strip()
        try:
            start = float(item.get("start"))
            end = float(item.get("end"))
        except (TypeError, ValueError):
            continue
        if not word or end <= start:
            continue
        key = word.rstrip(".,!?;:").lower()
        if words:
            prev = words[-1]
            prev_key = prev["word"].rstrip(".,!?;:").lower()
            if key == prev_key and start <= prev["end"] + 0.05:
                prev["end"] = max(prev["end"], end)
                continue
        words.append({"word": word, "start": start, "end": end})
    return {
        "schema_version": TRANSCRIPT_SCHEMA,
        "video": _str(src.get("video"), ""),
        "language": _str(src.get("language"), ""),
        "words": words,
    }


def iter_couples(words: list) -> list[tuple]:
    out = []
    n = len(words)
    for i in range(0, n, 2):
        left = words[i]
        right = words[i + 1] if i + 1 < n else None
        if i + 2 < n:
            hide = words[i + 2]["start"]
        elif right:
            hide = max(left["end"], right["end"])
        else:
            hide = left["end"]
        out.append((left, right, hide))
    return out


def caption_couple(words: list, time_sec: float) -> dict:
    if not words:
        return {"left": None, "right": None, "spoken": None, "index": -1}
    if time_sec < words[0]["start"]:
        return {
            "left": words[0],
            "right": words[1] if len(words) > 1 else None,
            "spoken": None,
            "index": 0,
        }
    n = len(words)
    for i, (left, right, hide) in enumerate(iter_couples(words)):
        idx = i * 2
        if time_sec >= left["start"] and time_sec < hide:
            spoken = "right" if right and time_sec >= right["start"] else "left"
            return {"left": left, "right": right, "spoken": spoken, "index": idx}
    i = n - 2 if n % 2 == 0 else n - 1
    if i < 0:
        i = 0
    left = words[i]
    right = words[i + 1] if i + 1 < n else None
    return {
        "left": left,
        "right": right,
        "spoken": "right" if right else "left",
        "index": i,
    }


def validate_transcript(data: dict) -> tuple[bool, list[str]]:
    parsed = parse_transcript(data)
    errors = []
    if not parsed["words"]:
        errors.append("C1: aucun mot valide (word + start < end)")
    return not errors, errors


def validate_style(data: dict) -> tuple[bool, list[str]]:
    style = normalize_style(data)
    errors = []
    if style["motion"] not in MOTION_VALUES:
        errors.append("C2: motion hors enum")
    if style["canvas"] not in CANVAS_VALUES:
        errors.append("C2: canvas inconnu")
    return not errors, errors


def build_proof_request(style: dict, word: str, video: str = "", frames: int = 3) -> dict:
    return {
        "schema_version": PROOF_SCHEMA,
        "style": normalize_style(style),
        "word": _str(word, "HOE"),
        "video": _str(video, ""),
        "frames": int(_clamp(frames, 1, 3, 3)),
    }


def resolve_font(style: dict, fonts_dir: Path) -> Path:
    name = Path(normalize_style(style)["font"]).name
    candidate = fonts_dir / name
    if candidate.is_file():
        return candidate
    fallback = fonts_dir / DEFAULT_FONT
    if fallback.is_file():
        return fallback
    raise FileNotFoundError(f"font introuvable: {name}")


def hex_to_rgba(color: str) -> tuple[float, float, float, float]:
    raw = (color or "#FFFFFF").lstrip("#")
    if len(raw) == 3:
        raw = "".join(ch * 2 for ch in raw)
    if len(raw) != 6:
        raw = "FFFFFF"
    r = int(raw[0:2], 16) / 255.0
    g = int(raw[2:4], 16) / 255.0
    b = int(raw[4:6], 16) / 255.0
    return (r, g, b, 1.0)

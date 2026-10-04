from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODE = ROOT / "F03_CALIX" / "CODEBASE"
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

from f03_calix import crop_scale_frame  # noqa: E402


def test_crop_illegal_raises() -> None:
    raw = bytes(1080 * 1920 * 3)
    try:
        crop_scale_frame(raw, 1080, 1920, {"x": 0, "y": 120, "w": 1080, "h": 1920}, 1080, 1920)
    except RuntimeError as exc:
        assert "illegal" in str(exc)
    else:
        raise AssertionError("expected illegal crop")


def test_crop_identity_1080x1920() -> None:
    w, h = 16, 16
    raw = bytes(range(256)) * ((w * h * 3 + 255) // 256)
    raw = raw[: w * h * 3]
    out = crop_scale_frame(raw, w, h, {"x": 0, "y": 0, "w": w, "h": h}, w, h)
    assert out == raw

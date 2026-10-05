# Tests F03_PICTOR — parite LOOK / P-ZOOM ZERO (sans Remotion)
# Run: pytest -q F03_PICTOR/tests/test_pictor_look.py
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREVIEW = ROOT / "F03_PREVIEW" / "CODEBASE" / "src" / "preview" / "_purPackComposition.jsx"
PICTOR = ROOT / "F03_PICTOR" / "CODEBASE" / "src" / "PurLook.jsx"
FORBIDDEN = ("zoompan", "breathing_zoom", "swell")


def test_pictor_imports_preview_composition():
    text = PICTOR.read_text(encoding="utf-8")
    assert "_purPackComposition" in text
    assert "muted={muted}" in text
    assert "fonts/Montserrat-ExtraBold.ttf" in text


def test_preview_look_has_three_styles_only():
    text = PREVIEW.read_text(encoding="utf-8")
    assert "blur" in text and "split" in text and "reframing" in text
    assert "ranking" not in text.lower()


def test_p_zoom_zero_on_look_sources():
    for path in (PREVIEW, PICTOR):
        lowered = path.read_text(encoding="utf-8").lower()
        for token in FORBIDDEN:
            assert token.lower() not in lowered, f"{token} in {path}"

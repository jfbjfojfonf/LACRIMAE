import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "CODEBASE"))
import caption_schema  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_normalize_style_defaults():
    style = caption_schema.normalize_style({})
    assert style["id"] == "s1"
    assert style["motion"] == "pop-in"
    assert style["canvas"] == "9:16"
    assert style["position"]["y_pct"] == 78


def test_normalize_style_rejects_free_motion():
    style = caption_schema.normalize_style({"motion": "spiral-camera"})
    assert style["motion"] == "pop-in"


def test_parse_transcript_drops_bad_cues():
    parsed = caption_schema.parse_transcript({
        "words": [
            {"word": "HOE", "start": 0.2, "end": 0.7},
            {"word": "", "start": 1, "end": 2},
            {"word": "BAD", "start": 5, "end": 4},
            {"word": "NOW", "start": "x", "end": 2},
        ]
    })
    assert [w["word"] for w in parsed["words"]] == ["HOE"]


def test_fixture_transcript_c1():
    data = json.loads((FIXTURES / "transcript_sample.json").read_text(encoding="utf-8"))
    ok, errors = caption_schema.validate_transcript(data)
    assert ok, errors


def test_s1_style_c2():
    data = json.loads((Path(__file__).resolve().parent.parent / "CODEBASE" / "styles" / "s1.json").read_text(encoding="utf-8"))
    ok, errors = caption_schema.validate_style(data)
    assert ok, errors
    assert data["id"] == "s1"


def test_proof_request_one_word():
    req = caption_schema.build_proof_request({}, "HOE")
    assert req["word"] == "HOE"
    assert req["frames"] == 3
    assert req["style"]["id"] == "s1"


def test_hex_to_rgba():
    assert caption_schema.hex_to_rgba("#FFFFFF")[0] == 1.0
    assert caption_schema.hex_to_rgba("00FF00")[1] == 1.0

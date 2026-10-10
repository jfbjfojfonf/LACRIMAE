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
    assert style["motion_speed"] == 1.0
    assert style["canvas"] == "9:16"
    assert style["position"]["y_pct"] == 78


def test_normalize_style_motion_speed_clamp():
    assert caption_schema.normalize_style({"motion_speed": 9})["motion_speed"] == 3.0
    assert caption_schema.normalize_style({"motion_speed": 0})["motion_speed"] == 0.25


def test_normalize_style_rejects_free_motion():
    style = caption_schema.normalize_style({"motion": "spiral-camera"})
    assert style["motion"] == "pop-in"


def test_parse_transcript_merges_adjacent_duplicates():
    parsed = caption_schema.parse_transcript({
        "words": [
            {"word": "run", "start": 7.66, "end": 8.22},
            {"word": "run", "start": 8.22, "end": 8.44},
            {"word": "He's", "start": 12.39, "end": 12.87},
        ]
    })
    assert [w["word"] for w in parsed["words"]] == ["run", "He's"]
    assert parsed["words"][0]["end"] == 8.44


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


def test_motion_windows_caps_short_word():
    attack, settle = caption_schema.motion_windows(0.25, 0.2)
    assert settle <= 0.2 * 0.9 + 1e-9
    assert attack < settle


def test_caption_couple_steps_by_two():
    words = [
        {"word": "A", "start": 0.0, "end": 0.3},
        {"word": "B", "start": 0.3, "end": 0.6},
        {"word": "C", "start": 0.6, "end": 0.9},
        {"word": "D", "start": 0.9, "end": 1.2},
    ]
    first = caption_schema.caption_couple(words, 0.1)
    assert first["left"]["word"] == "A"
    assert first["right"]["word"] == "B"
    assert first["spoken"] == "left"
    second = caption_schema.caption_couple(words, 0.4)
    assert second["left"]["word"] == "A"
    assert second["right"]["word"] == "B"
    assert second["spoken"] == "right"
    nxt = caption_schema.caption_couple(words, 0.7)
    assert nxt["left"]["word"] == "C"
    assert nxt["right"]["word"] == "D"
    assert nxt["spoken"] == "left"


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

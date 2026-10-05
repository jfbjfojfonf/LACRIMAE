# Tests F04_HEISENBERG (unitaires, sans ffmpeg requis pour le plan)
# Run: pytest -q F04_HEISENBERG/tests/test_heisenberg.py
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "CODEBASE"))
import heisenberg as hz  # noqa: E402


def test_angle_of_strips_pur_prefix():
    assert hz.angle_of({"source_id": "pur_A01"}) == "A01"
    assert hz.angle_of({"angle_id": "A02"}) == "A02"


def test_plan_skips_merges_jump_cuts():
    entry = {
        "duration_seconds": 10,
        "cuts": [
            {"type": "breath_cut", "moment_sec": 1.0},
            {"type": "idea_cut", "moment_sec": 1.04},
            {"type": "smash_cut", "moment_sec": 5.0},
        ],
    }
    skips = hz.plan_skips(entry)
    assert skips
    assert skips[0][0] == 1.0
    assert skips[0][1] > 1.08
    assert all(s[0] != 5.0 for s in skips)


def test_punch_in_is_cut_not_animation():
    entry = {
        "duration_seconds": 8,
        "cuts": [],
        "punch_ins": [{"in_sec": 2.0, "out_sec": 2.4, "scale": 1.15}],
    }
    segments = hz.plan_segments(entry)
    modes = [s["mode"] for s in segments]
    assert "punch_in_cut" in modes
    punch = next(s for s in segments if s["mode"] == "punch_in_cut")
    assert punch["in_sec"] == 2.0
    assert punch["out_sec"] == 2.4
    assert punch["scale"] == 1.15
    normals = [s for s in segments if s["mode"] == "normal"]
    assert normals[0]["out_sec"] == 2.0
    assert any(s["in_sec"] == 2.4 for s in normals)


def test_jump_cut_removed_from_timeline():
    entry = {
        "duration_seconds": 5,
        "cuts": [{"type": "breath_cut", "moment_sec": 2.0}],
        "punch_ins": [],
    }
    segments = hz.plan_segments(entry)
    covered = sum(s["out_sec"] - s["in_sec"] for s in segments)
    assert covered < 5.0
    assert all(not (s["in_sec"] < 2.04 < s["out_sec"]) for s in segments)


def test_source_to_output_accounts_for_skips():
    entry = {
        "duration_seconds": 5,
        "cuts": [{"type": "breath_cut", "moment_sec": 1.0}],
        "punch_ins": [],
    }
    segments = hz.plan_segments(entry)
    before = hz.source_to_output(0.5, segments)
    after = hz.source_to_output(2.0, segments)
    assert before == pytest.approx(0.5)
    assert after < 2.0


def test_assert_no_zoom_rejects_zoompan():
    with pytest.raises(RuntimeError, match="P-ZOOM ZERO"):
        hz.assert_no_zoom("scale=1080:1920,zoompan=z=1.2")


def test_build_filter_uses_crop_not_zoompan():
    segs = [
        {"in_sec": 0.0, "out_sec": 1.0, "mode": "normal", "scale": 1.0},
        {"in_sec": 1.0, "out_sec": 1.3, "mode": "punch_in_cut", "scale": 1.2},
        {"in_sec": 1.3, "out_sec": 2.0, "mode": "normal", "scale": 1.0},
    ]
    graph, extra = hz.build_filter(segs, 1080, 1920, False, [], [], 30)
    assert "zoompan" not in graph
    assert "crop=" in graph
    assert extra == 0
    hz.assert_no_zoom(graph)


def test_broll_flash_only_on_entry():
    segs = [{"in_sec": 0.0, "out_sec": 3.0, "mode": "normal", "scale": 1.0}]
    broll = [{"out_in_sec": 1.0, "out_out_sec": 1.4, "flash_in": True}]
    graph, extra = hz.build_filter(segs, 1080, 1920, False, broll, [], 30)
    assert extra == 1
    assert "drawbox" in graph
    assert graph.count("drawbox") == 1


def test_duck_windows_sfx_and_smash():
    windows = hz.duck_windows(
        [{"out_sec": 1.0}],
        [{"out_in_sec": 2.0, "out_out_sec": 2.5, "duck": True}],
        [4.0],
    )
    assert windows[0][0] == pytest.approx(1.0)
    assert any(a == pytest.approx(2.0) and b == pytest.approx(2.5) for a, b in windows)
    assert any(a == pytest.approx(4.0) for a, b in windows)


def test_build_filter_ducks_voice_under_sfx():
    segs = [{"in_sec": 0.0, "out_sec": 3.0, "mode": "normal", "scale": 1.0}]
    sfx = [{"out_sec": 1.0, "volume": 0.5}]
    graph, extra = hz.build_filter(segs, 1080, 1920, True, [], sfx, 30, [2.0])
    assert extra == 1
    assert "volume=0.35" in graph
    assert "amix=" in graph

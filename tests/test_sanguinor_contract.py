from __future__ import annotations

import json
from pathlib import Path

from tests.conftest import touch_mp4, write_json
from LAC_CUSTOS import run_custos, validate_camera_path, Verdict


FIXTURES = Path(__file__).resolve().parent / "fixtures"
CFG = {
    "zoom_min": 1.0,
    "jitter_median_norm_max": 0.02,
    "deadzone_norm": 0.04,
    "detected_ratio_min": 0.5,
    "gap_amber_frames": 12,
}


def test_camera_path_valid() -> None:
    v = Verdict()
    data = json.loads((FIXTURES / "camera_path.valid.json").read_text())
    validate_camera_path(data, v, CFG, "clip_001")
    assert not v.refused


def test_camera_path_crop_overflow() -> None:
    v = Verdict()
    data = json.loads((FIXTURES / "camera_path.valid.json").read_text())
    data["frames"][0]["crop"] = {"x": 0, "y": 120, "w": 1080, "h": 1920}
    validate_camera_path(data, v, CFG, "clip_001")
    assert v.refused
    assert any("P-SG-4" in e for e in v.errors)


def test_camera_path_zoom_below_one() -> None:
    v = Verdict()
    data = json.loads((FIXTURES / "camera_path.valid.json").read_text())
    data["frames"][0]["zoom"] = 0.5
    validate_camera_path(data, v, CFG, "clip_001")
    assert v.refused
    assert any("P-SG-3" in e for e in v.errors)


def test_f02_check_out_hold_last(campaign_root: Path) -> None:
    land = json.loads((FIXTURES / "landmarks.valid.json").read_text())
    path = json.loads((FIXTURES / "camera_path.valid.json").read_text())
    write_json(campaign_root / "F02_SANGUINOR" / "IN" / "landmarks" / "clip_001.json", land)
    touch_mp4(campaign_root / "F02_SANGUINOR" / "IN" / "clips" / "clip_001.mp4")
    write_json(campaign_root / "F02_SANGUINOR" / "OUT" / "camera_path" / "clip_001.json", path)
    write_json(
        campaign_root / "F02_SANGUINOR" / "OUT" / "sanguinor_report.json",
        {
            "schema": "dev11.sanguinor_report.v1",
            "campaign_id": "fixture",
            "stems": [{"stem": "clip_001", "jitter_median_norm": 0.0, "held_frames": 1, "verdict": "PASS"}],
            "held": [],
            "refused": [],
        },
    )
    v = run_custos(campaign_root, "F02_SANGUINOR", "check-out")
    assert not v.refused


def test_f02_hold_last_jump_refused(campaign_root: Path) -> None:
    land = json.loads((FIXTURES / "landmarks.valid.json").read_text())
    path = json.loads((FIXTURES / "camera_path.valid.json").read_text())
    path["frames"][2]["cx"] = 0.9
    path["frames"][2]["cy"] = 0.9
    write_json(campaign_root / "F02_SANGUINOR" / "IN" / "landmarks" / "clip_001.json", land)
    touch_mp4(campaign_root / "F02_SANGUINOR" / "IN" / "clips" / "clip_001.mp4")
    write_json(campaign_root / "F02_SANGUINOR" / "OUT" / "camera_path" / "clip_001.json", path)
    write_json(
        campaign_root / "F02_SANGUINOR" / "OUT" / "sanguinor_report.json",
        {"schema": "dev11.sanguinor_report.v1", "stems": [], "held": [], "refused": []},
    )
    v = run_custos(campaign_root, "F02_SANGUINOR", "check-out")
    assert v.refused
    assert any("P-SG-7" in e for e in v.errors)

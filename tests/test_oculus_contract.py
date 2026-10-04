from __future__ import annotations

import json
from pathlib import Path

from tests.conftest import touch_mp4, write_json
from LAC_CUSTOS import run_custos, validate_job_request, validate_landmarks, Verdict


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_job_request_valid() -> None:
    v = Verdict()
    data = json.loads((FIXTURES / "job_request.valid.json").read_text())
    validate_job_request(data, v)
    assert not v.refused


def test_job_request_bad_target() -> None:
    v = Verdict()
    validate_job_request({"schema": "dev11.job_request.v1", "target": "ear"}, v)
    assert v.refused
    assert any("P-OC-1" in e for e in v.errors)


def test_landmarks_valid() -> None:
    v = Verdict()
    data = json.loads((FIXTURES / "landmarks.valid.json").read_text())
    validate_landmarks(data, v, {"detected_ratio_min": 0.5, "gap_amber_frames": 12}, "clip_001")
    assert not v.refused
    assert not v.holds


def test_landmarks_hold_low_detect() -> None:
    v = Verdict()
    data = json.loads((FIXTURES / "landmarks.valid.json").read_text())
    for frame in data["frames"]:
        frame["detected"] = False
        frame["target"] = None
    validate_landmarks(data, v, {"detected_ratio_min": 0.85, "gap_amber_frames": 12}, "clip_001")
    assert not v.refused
    assert v.holds
    assert any("P-OC-14" in h for h in v.holds)


def test_f01_check_in_missing_clips(campaign_root: Path) -> None:
    write_json(
        campaign_root / "F01_OCULUS" / "IN" / "job_request.json",
        json.loads((FIXTURES / "job_request.valid.json").read_text()),
    )
    v = run_custos(campaign_root, "F01_OCULUS", "check-in")
    assert v.refused
    assert any("P-OC-2" in e for e in v.errors)


def test_f01_check_in_pass_with_empty_mp4(campaign_root: Path) -> None:
    write_json(
        campaign_root / "F01_OCULUS" / "IN" / "job_request.json",
        json.loads((FIXTURES / "job_request.valid.json").read_text()),
    )
    touch_mp4(campaign_root / "F01_OCULUS" / "IN" / "clips" / "clip_001.mp4")
    v = run_custos(campaign_root, "F01_OCULUS", "check-in")
    assert not v.refused


def test_f01_check_out_pair(campaign_root: Path) -> None:
    touch_mp4(campaign_root / "F01_OCULUS" / "IN" / "clips" / "clip_001.mp4")
    write_json(
        campaign_root / "F01_OCULUS" / "OUT" / "landmarks" / "clip_001.json",
        json.loads((FIXTURES / "landmarks.valid.json").read_text()),
    )
    write_json(
        campaign_root / "F01_OCULUS" / "OUT" / "oculus_report.json",
        {
            "schema": "dev11.oculus_report.v1",
            "campaign_id": "fixture",
            "stems": [{"stem": "clip_001", "detected_ratio": 0.66, "longest_gap_frames": 1, "verdict": "PASS"}],
            "held": [],
            "refused": [],
        },
    )
    v = run_custos(campaign_root, "F01_OCULUS", "check-out")
    assert not v.refused

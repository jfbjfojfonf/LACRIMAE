from __future__ import annotations

import json
from pathlib import Path

from tests.conftest import touch_mp4, write_json
from LAC_CUSTOS import run_custos, validate_calix_manifest, Verdict


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_manifest_valid() -> None:
    v = Verdict()
    data = json.loads((FIXTURES / "calix_manifest.valid.json").read_text())
    validate_calix_manifest(data, v, {"clip_001"})
    assert not v.refused


def test_manifest_missing_stem_refus() -> None:
    v = Verdict()
    data = json.loads((FIXTURES / "calix_manifest.valid.json").read_text())
    validate_calix_manifest(data, v, {"clip_001", "clip_002"})
    assert v.refused
    assert any("P-CX-6" in e for e in v.errors)


def test_f03_check_out_strict_aggregation(campaign_root: Path) -> None:
    path = json.loads((FIXTURES / "camera_path.valid.json").read_text())
    write_json(campaign_root / "F03_CALIX" / "IN" / "camera_path" / "clip_001.json", path)
    touch_mp4(campaign_root / "F03_CALIX" / "IN" / "clips" / "clip_001.mp4")
    write_json(
        campaign_root / "F03_CALIX" / "OUT" / "calix_manifest.json",
        json.loads((FIXTURES / "calix_manifest.valid.json").read_text()),
    )
    write_json(
        campaign_root / "F03_CALIX" / "OUT" / "calix_report.json",
        {"schema": "dev11.calix_report.v1", "stems": [], "held": [], "refused": []},
    )
    v = run_custos(campaign_root, "F03_CALIX", "check-out")
    assert v.refused
    assert any("P-CX-1" in e for e in v.errors)
    assert any("P-CX-6" in e for e in v.errors)


def test_f03_check_out_pass_with_placeholder_mp4(campaign_root: Path) -> None:
    path = json.loads((FIXTURES / "camera_path.valid.json").read_text())
    write_json(campaign_root / "F03_CALIX" / "IN" / "camera_path" / "clip_001.json", path)
    touch_mp4(campaign_root / "F03_CALIX" / "IN" / "clips" / "clip_001.mp4")
    touch_mp4(campaign_root / "F03_CALIX" / "OUT" / "tracked" / "clip_001.mp4")
    write_json(
        campaign_root / "F03_CALIX" / "OUT" / "calix_manifest.json",
        json.loads((FIXTURES / "calix_manifest.valid.json").read_text()),
    )
    write_json(
        campaign_root / "F03_CALIX" / "OUT" / "calix_report.json",
        {"schema": "dev11.calix_report.v1", "stems": [], "held": [], "refused": []},
    )
    v = run_custos(campaign_root, "F03_CALIX", "check-out")
    assert not v.refused

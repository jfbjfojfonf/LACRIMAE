from __future__ import annotations

import json
from pathlib import Path

from tests.conftest import touch_mp4, write_json
from LAC_CUSTOS import run_custos
from LAC_RUN import copy_tree_files


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_copy_skips_held_stems(tmp_path: Path) -> None:
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    (src / "clip_001.json").write_text("{}", encoding="utf-8")
    (src / "clip_bad.json").write_text("{}", encoding="utf-8")
    n = copy_tree_files(src, dst, skip_stems={"clip_bad"})
    assert n == 1
    assert (dst / "clip_001.json").is_file()
    assert not (dst / "clip_bad.json").exists()


def test_f01_checkout_records_held_stem(campaign_root: Path) -> None:
    land = json.loads((FIXTURES / "landmarks.valid.json").read_text())
    for frame in land["frames"]:
        frame["detected"] = False
        frame["target"] = None
    touch_mp4(campaign_root / "F01_OCULUS" / "IN" / "clips" / "clip_001.mp4")
    write_json(campaign_root / "F01_OCULUS" / "OUT" / "landmarks" / "clip_001.json", land)
    write_json(
        campaign_root / "F01_OCULUS" / "OUT" / "oculus_report.json",
        {"schema": "dev11.oculus_report.v1", "stems": [], "held": ["clip_001"], "refused": []},
    )
    v = run_custos(campaign_root, "F01_OCULUS", "check-out")
    assert not v.refused
    assert "clip_001" in v.held_stems

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def repo_root() -> Path:
    return ROOT


@pytest.fixture
def campaign_root(tmp_path: Path) -> Path:
    root = tmp_path / "campaign"
    for rel in (
        "F01_OCULUS/IN/clips",
        "F01_OCULUS/OUT/landmarks",
        "F02_SANGUINOR/IN/clips",
        "F02_SANGUINOR/IN/landmarks",
        "F02_SANGUINOR/OUT/camera_path",
        "F02_SANGUINOR/CODEBASE",
        "F03_CALIX/IN/clips",
        "F03_CALIX/IN/camera_path",
        "F03_CALIX/OUT/tracked",
        "F01_OCULUS/CODEBASE",
        "F03_CALIX/CODEBASE",
        "CONFIG",
    ):
        (root / rel).mkdir(parents=True)
    shutil.copy2(ROOT / "CONFIG" / "camera_defaults.json", root / "CONFIG" / "camera_defaults.json")
    for name in ("F01_OCULUS", "F02_SANGUINOR", "F03_CALIX"):
        src = ROOT / name / "CODEBASE"
        dst = root / name / "CODEBASE"
        if src.is_dir():
            for py in src.glob("*.py"):
                shutil.copy2(py, dst / py.name)
    return root


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def touch_mp4(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"")

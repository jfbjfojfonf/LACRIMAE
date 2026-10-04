from __future__ import annotations

from LAC_CUSTOS import run_custos


def test_no_sister_out_in_engines(repo_root) -> None:
    for frigate in ("F01_OCULUS", "F02_SANGUINOR", "F03_CALIX"):
        v = run_custos(repo_root, frigate, "check-in")
        assert not any("P-ISO-1" in e for e in v.errors)


def test_engine_stub_does_not_cite_sister_out(repo_root) -> None:
    forbidden = {
        "F01_OCULUS": ("F02_SANGUINOR/OUT", "F03_CALIX/OUT"),
        "F02_SANGUINOR": ("F01_OCULUS/OUT", "F03_CALIX/OUT"),
        "F03_CALIX": ("F01_OCULUS/OUT", "F02_SANGUINOR/OUT"),
    }
    for frigate, needles in forbidden.items():
        text = (repo_root / frigate / "CODEBASE" / {
            "F01_OCULUS": "f01_oculus.py",
            "F02_SANGUINOR": "f02_sanguinor.py",
            "F03_CALIX": "f03_calix.py",
        }[frigate]).read_text(encoding="utf-8")
        for needle in needles:
            assert needle not in text

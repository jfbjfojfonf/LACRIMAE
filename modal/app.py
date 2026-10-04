"""Modal app lacrimae-dev11-oculus. Stages : skeleton jusqu'aux secrets + modele."""
from __future__ import annotations

APP_NAME = "lacrimae-dev11-oculus"
STAGES = ("oculus", "sanguinor", "calix")
TIMEOUTS_S = {"oculus": 600, "sanguinor": 300, "calix": 900}


def stage_oculus() -> None:
    raise SystemExit("stage_oculus: forger image CPU + volume face_landmarker.task")


def stage_sanguinor() -> None:
    raise SystemExit("stage_sanguinor: python F02_SANGUINOR/CODEBASE/f02_sanguinor.py")


def stage_calix() -> None:
    raise SystemExit("stage_calix: python F03_CALIX/CODEBASE/f03_calix.py (+ffmpeg)")


def main() -> None:
    raise SystemExit(
        f"{APP_NAME} skeleton. Stages={STAGES} timeouts={TIMEOUTS_S}. "
        "Ne pas decoder de MP4 campagne hors Modal."
    )


if __name__ == "__main__":
    main()

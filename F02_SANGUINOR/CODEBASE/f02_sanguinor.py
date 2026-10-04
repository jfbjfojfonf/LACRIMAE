#!/usr/bin/env python3
"""F02 SANGUINOR — moteur non forge (Groupe 2)."""
from __future__ import annotations

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="F02 SANGUINOR — camera path")
    parser.add_argument("--in", dest="in_dir", required=True)
    parser.add_argument("--out", dest="out_dir", required=True)
    parser.add_argument("--config", dest="config", default="CONFIG/camera_defaults.json")
    parser.parse_args()
    print("F02_SANGUINOR: moteur non forge. Groupe 2. Ad Victoriam.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

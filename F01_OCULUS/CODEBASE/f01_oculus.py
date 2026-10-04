#!/usr/bin/env python3
"""F01 OCULUS — moteur non forge (Groupe 1)."""
from __future__ import annotations

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="F01 OCULUS — landmarks")
    parser.add_argument("--in", dest="in_dir", required=True)
    parser.add_argument("--out", dest="out_dir", required=True)
    parser.parse_args()
    print("F01_OCULUS: moteur non forge. Groupe 1. Ad Victoriam.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

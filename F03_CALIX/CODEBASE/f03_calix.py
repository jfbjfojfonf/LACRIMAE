#!/usr/bin/env python3
"""F03 CALIX — moteur non forge (Groupe 3)."""
from __future__ import annotations

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="F03 CALIX — crop + mux")
    parser.add_argument("--in", dest="in_dir", required=True)
    parser.add_argument("--out", dest="out_dir", required=True)
    parser.parse_args()
    print("F03_CALIX: moteur non forge. Groupe 3. Ad Victoriam.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Orchestrateur LACRIMAE dev-11. Seul autorise a transiter IN<-OUT."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PYTHON = sys.executable

ENGINES = {
    "F01_OCULUS": ROOT / "F01_OCULUS" / "CODEBASE" / "f01_oculus.py",
    "F02_SANGUINOR": ROOT / "F02_SANGUINOR" / "CODEBASE" / "f02_sanguinor.py",
    "F03_CALIX": ROOT / "F03_CALIX" / "CODEBASE" / "f03_calix.py",
}

TRANSIT = {
    ("F01_OCULUS", "F02_SANGUINOR"): (
        ("F01_OCULUS/OUT/landmarks", "F02_SANGUINOR/IN/landmarks"),
        ("F01_OCULUS/IN/clips", "F02_SANGUINOR/IN/clips"),
    ),
    ("F02_SANGUINOR", "F03_CALIX"): (
        ("F02_SANGUINOR/OUT/camera_path", "F03_CALIX/IN/camera_path"),
        ("F02_SANGUINOR/IN/clips", "F03_CALIX/IN/clips"),
    ),
}

GATE_FLAGS = {
    "landmarks": ("F01_OCULUS", "check-out"),
    "camera": ("F02_SANGUINOR", "check-out"),
    "calix": ("F03_CALIX", "check-out"),
}


def custos(frigate: str, mode: str) -> int:
    cmd = [
        PYTHON,
        str(ROOT / "LAC_CUSTOS.py"),
        "--frigate",
        frigate,
        "--mode",
        mode,
        "--root",
        str(ROOT),
    ]
    print("+", " ".join(cmd), file=sys.stderr)
    return subprocess.call(cmd)


def copy_tree_files(src: Path, dst: Path, skip_stems: set[str] | None = None) -> int:
    dst.mkdir(parents=True, exist_ok=True)
    n = 0
    if not src.is_dir():
        return 0
    skip = skip_stems or set()
    for item in src.iterdir():
        if item.name == ".gitkeep":
            continue
        if item.is_file():
            if item.stem in skip:
                print(f"transit HOLD skip {item.name}", file=sys.stderr)
                continue
            shutil.copy2(item, dst / item.name)
            n += 1
    return n


def transit(src: str, dst: str) -> int:
    key = (src, dst)
    if key not in TRANSIT:
        print(f"transit interdit: {src} -> {dst}", file=sys.stderr)
        return 1
    from LAC_CUSTOS import run_custos

    verdict = run_custos(ROOT, src, "check-out")
    verdict.dump(sys.stderr)
    if verdict.refused:
        print("transit refuse: CUSTOS check-out source", file=sys.stderr)
        return 1
    skip = set(verdict.held_stems) if src == "F01_OCULUS" else set()
    total = 0
    for rel_src, rel_dst in TRANSIT[key]:
        n = copy_tree_files(ROOT / rel_src, ROOT / rel_dst, skip_stems=skip)
        print(f"transit {rel_src} -> {rel_dst} ({n} fichiers)", file=sys.stderr)
        total += n
    if total == 0:
        print("transit vide", file=sys.stderr)
        return 1
    return custos(dst, "check-in")


def run_engine(frigate: str) -> int:
    engine = ENGINES[frigate]
    in_dir = ROOT / frigate / "IN"
    out_dir = ROOT / frigate / "OUT"
    cmd = [PYTHON, str(engine), "--in", str(in_dir), "--out", str(out_dir)]
    if frigate == "F02_SANGUINOR":
        cmd.extend(["--config", str(ROOT / "CONFIG" / "camera_defaults.json")])
    print("+", " ".join(cmd), file=sys.stderr)
    return subprocess.call(cmd)


def cmd_run() -> int:
    if custos("F01_OCULUS", "check-in") != 0:
        print("Porte I REFUS", file=sys.stderr)
        return 1
    code = run_engine("F01_OCULUS")
    if code != 0:
        print("F01 moteur arrete (non forge ou erreur). Porte II non franchie.", file=sys.stderr)
        return code
    if custos("F01_OCULUS", "check-out") != 0:
        print("Porte II REFUS", file=sys.stderr)
        return 1
    if transit("F01_OCULUS", "F02_SANGUINOR") != 0:
        return 1
    code = run_engine("F02_SANGUINOR")
    if code != 0:
        print("F02 moteur arrete. Porte III non franchie.", file=sys.stderr)
        return code
    if custos("F02_SANGUINOR", "check-out") != 0:
        print("Porte III REFUS", file=sys.stderr)
        return 1
    if transit("F02_SANGUINOR", "F03_CALIX") != 0:
        return 1
    code = run_engine("F03_CALIX")
    if code != 0:
        print("F03 moteur arrete. Porte IV non franchie.", file=sys.stderr)
        return code
    return custos("F03_CALIX", "check-out")


def cmd_gate(which: str) -> int:
    frigate, mode = GATE_FLAGS[which]
    return custos(frigate, mode)


def main() -> int:
    parser = argparse.ArgumentParser(description="LAC_RUN — portes I-IV")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("run")
    g = sub.add_parser("gate")
    g.add_argument("--landmarks", action="store_true")
    g.add_argument("--camera", action="store_true")
    g.add_argument("--calix", action="store_true")
    t = sub.add_parser("transit")
    t.add_argument("--from", dest="src", required=True)
    t.add_argument("--to", dest="dst", required=True)
    c = sub.add_parser("custos")
    c.add_argument("--frigate", required=True)
    c.add_argument("--mode", required=True, choices=("check-in", "check-out"))
    args = parser.parse_args()
    if args.cmd == "run":
        return cmd_run()
    if args.cmd == "gate":
        flags = [k for k in ("landmarks", "camera", "calix") if getattr(args, k)]
        if len(flags) != 1:
            print("gate: un seul flag --landmarks|--camera|--calix", file=sys.stderr)
            return 2
        return cmd_gate(flags[0])
    if args.cmd == "transit":
        from LAC_CUSTOS import resolve_frigate

        return transit(resolve_frigate(args.src), resolve_frigate(args.dst))
    if args.cmd == "custos":
        from LAC_CUSTOS import resolve_frigate

        return custos(resolve_frigate(args.frigate), args.mode)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

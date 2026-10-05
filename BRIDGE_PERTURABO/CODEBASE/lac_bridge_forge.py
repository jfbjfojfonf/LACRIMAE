#!/usr/bin/env python3
"""BRIDGE PUR — fetch pack PERTURABO + conversion manifeste dev10.pur.v1.

Rien d'autre : pas de mode forge logo, pas de meme, pas de cutlist F02.
Le telechargement video reste a F00_PUR.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BRIDGE_BASE = ROOT / "BRIDGE_PERTURABO"
BRIDGE_IN = BRIDGE_BASE / "IN"
BRIDGE_OUT = BRIDGE_BASE / "OUT"

PERTURABO_REPO = "kioka8877-ux/PERTURABO"
PERTURABO_EXPORT_PATH = "MONDES_FORGES/CLIPPING/EXPORT"
PERTURABO_BRANCH = "main"


def log_ok(msg):
    print(f"  [ok] {msg}")


def log_err(msg):
    print(f"  [fail] {msg}")


def section(title):
    print(f"\n{'-' * 60}\n  {title}\n{'-' * 60}")


def github_api(url: str) -> dict:
    headers = {"User-Agent": "LACRIMAE-BRIDGE", "Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.loads(resp.read().decode("utf-8"))


def download_file(url: str, dest: Path) -> None:
    headers = {"User-Agent": "LACRIMAE-BRIDGE"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=180) as resp:
        dest.write_bytes(resp.read())


def fetch_pack_from_perturabo(repo=PERTURABO_REPO, export_path=PERTURABO_EXPORT_PATH,
                              branch=PERTURABO_BRANCH, pack_filter=None) -> Path:
    section("FETCH — pack depuis PERTURABO/EXPORT")
    listing = github_api(
        f"https://api.github.com/repos/{repo}/contents/{export_path}?ref={branch}")
    files = [f for f in listing if f.get("type") == "file"]
    packs = [f for f in files if f["name"].startswith("production_pack_pur_") and f["name"].endswith(".json")]
    if not packs:
        log_err(f"Aucun production_pack_pur_*.json dans {export_path} (repo {repo})")
        sys.exit(1)
    if pack_filter:
        matched = [f for f in packs if pack_filter.lower() in f["name"].lower()]
        if not matched:
            log_err(f"--pack-filter '{pack_filter}' : aucun pack. Dispo : {[f['name'] for f in packs]}")
            sys.exit(1)
        packs = matched
    chosen = sorted(packs, key=lambda f: f["name"])[-1]
    log_ok(f"Pack trouve : {chosen['name']}")
    BRIDGE_IN.mkdir(parents=True, exist_ok=True)
    pack_dest = BRIDGE_IN / chosen["name"]
    download_file(chosen["download_url"], pack_dest)
    log_ok(f"Pack telecharge -> {pack_dest}")
    return pack_dest


def validate_pur_pack(pack: dict) -> tuple[bool, list[str]]:
    errors = []
    if not isinstance(pack, dict):
        return False, ["pack illisible"]
    if pack.get("mode") != "pur":
        errors.append(f"mode={pack.get('mode')!r}, attendu 'pur'")
    source = pack.get("source") or {}
    mi = pack.get("montage_instructions") or {}
    segment = mi.get("segment") or source
    if not (segment.get("source_url") or source.get("vod_url")):
        errors.append("vod_url absente")
    if not mi:
        errors.append("montage_instructions absente")
    start = segment.get("start_sec", source.get("start_sec"))
    end = segment.get("end_sec", source.get("end_sec"))
    if start is None or end is None or float(end) <= float(start):
        errors.append("segment invalide (end <= start)")
    return len(errors) == 0, errors


def convert_pur_pack_to_manifest(pack: dict, canvas: str = "9:16", style: str | None = None) -> dict:
    script = ROOT / "tools" / "convert_pur_pack.mjs"
    if not script.is_file():
        log_err(f"Script de conversion absent : {script}")
        sys.exit(1)
    BRIDGE_OUT.mkdir(parents=True, exist_ok=True)
    tmp_pack = BRIDGE_OUT / "pur_pack_in.json"
    tmp_pack.write_text(json.dumps(pack, ensure_ascii=False), encoding="utf-8")
    out = BRIDGE_OUT / "pur_manifest.json"
    cmd = ["node", str(script), "--pack", str(tmp_pack), "--out", str(out), "--canvas", canvas]
    if style:
        cmd += ["--style", style]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log_err(f"Conversion echouee :\n{result.stderr or result.stdout}")
        sys.exit(result.returncode or 1)
    print(result.stdout.strip())
    return json.loads(out.read_text(encoding="utf-8"))


def transit_pur_manifest(manifest_path: Path) -> None:
    targets = (
        ROOT / "F03_PREVIEW" / "CODEBASE" / "public",
        ROOT / "F03_PICTOR" / "CODEBASE" / "public",
    )
    for public in targets:
        if public.parent.exists():
            public.mkdir(parents=True, exist_ok=True)
            shutil.copy2(manifest_path, public / "pur_manifest.json")
            log_ok(f"Transit -> {public / 'pur_manifest.json'}")


def run_pur_mode(args):
    section("LAC_BRIDGE — MODE PUR")
    pack_path = Path(args.pack) if args.pack else fetch_pack_from_perturabo(pack_filter=args.pack_filter)
    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    ok, errors = validate_pur_pack(pack)
    if not ok:
        for e in errors:
            log_err(f"G0 PACK : {e}")
        print("\n  == MODE PUR : ECHOUE — pack invalide ==")
        sys.exit(1)
    mi = pack["montage_instructions"]
    segment = mi.get("segment") or pack.get("source") or {}
    log_ok(f"Pack PUR valide : {pack.get('pack_id', '?')} | "
           f"angle {pack.get('identite', {}).get('angle_id', '?')} | "
           f"segment {segment.get('start_sec')}s -> {segment.get('end_sec')}s")
    if args.dry_run:
        print(f"\n[DRY-RUN] {pack_path} -> BRIDGE_PERTURABO/OUT/pur_manifest.json (canvas {args.canvas})")
        return
    BRIDGE_OUT.mkdir(parents=True, exist_ok=True)
    if args.pack:
        shutil.copy2(pack_path, BRIDGE_IN / pack_path.name)
    manifest = convert_pur_pack_to_manifest(pack, canvas=args.canvas, style=args.style)
    manifest_path = BRIDGE_OUT / "pur_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    log_ok(f"pur_manifest.json : {manifest_path}")
    transit_pur_manifest(manifest_path)
    print()
    print("=" * 52)
    print(" BRIDGE PUR — MISSION ACCOMPLIE")
    print(f"  Pack      : {pack.get('pack_id', '?')}")
    print(f"  Manifeste : {manifest_path}")
    print("  Prochain  : F00_PUR telecharge le segment VOD")
    print("=" * 52)


def main():
    parser = argparse.ArgumentParser(description="BRIDGE PUR — Pont PERTURABO -> LACRIMAE")
    parser.add_argument("--pack", default=None, help="Chemin local du production_pack_pur_*.json")
    parser.add_argument("--pack-filter", default=None, help="Filtre du pack a recuperer (ex: pur_A01)")
    parser.add_argument("--pur", action="store_true", help="MODE PUR (seul mode de ce bridge)")
    parser.add_argument("--canvas", default="9:16", choices=["9:16", "16:9", "1:1"])
    parser.add_argument("--style", default=None, choices=["blur", "split_scene", "reframing"],
                        help="Style LOOK force par l'operateur")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not args.pur:
        args.pur = True
    run_pur_mode(args)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Agrégateur PUR multi-vidéos — refus de publier si un rendu manque.

Doctrine « 1 codex = N vidéos = 1 run = 1 zip » (2026-09-10) :
  - reçoit le manifeste d'entrée (multi-entrées) + les artifacts des N runners
  - VÉRIFIE que chaque entrée a son MP4 lisible (aucun zip incomplet, jamais)
  - produit le dossier bundle : N MP4 renommés + manifestes + rapport

Usage :
  python3 tools/pur_aggregate.py \
    --manifest pur_manifest.json \
    --results RUNNER_TEMP/results \
    --out F03_PICTOR/OUT \
    [--report F03_PICTOR/OUT/pur_aggregate_report.json]

Code de sortie 0 = bundle complet publié ; 1 = incomplet, RIEN n'est publié.

Fix 2026-09-11 (run 34575463702) : les identifiants d'entrée déjà préfixés
('pur_A01' via source_id) sont normalisés AVANT la recherche du MP4 — sinon
l'agrégateur cherchait pur_pur_a01_finale.mp4 (double préfixe) et refusait
un bundle pourtant complet. Le rendu, lui, était déjà bon.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_angle(raw) -> str:
    """Normalise l'identifiant d'entrée : 'pur_A01' et 'A01' désignent le même angle.

    Les manifestes dev10.pur.v1 portent un source_id déjà préfixé ('pur_A01')
    tandis que les runners produisent pur_<angle>_finale.mp4. Sans
    normalisation, la recherche devient pur_pur_a01_finale.mp4 → introuvable.
    """
    angle = str(raw if raw is not None else "?").strip()
    if len(angle) > 4 and angle.lower().startswith("pur_"):
        angle = angle[4:]
    return angle


def probe(path: Path) -> dict:
    try:
        data = json.loads(subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries",
             "stream=codec_name,codec_type,width,height:format=duration",
             "-of", "json", str(path)], text=True))
        video = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
        audio = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), None)
        return {
            "codec": video.get("codec_name") if video else None,
            "width": int(video.get("width") or 0) if video else 0,
            "height": int(video.get("height") or 0) if video else 0,
            "duration_seconds": round(float(data.get("format", {}).get("duration") or 0), 3),
            "audio_codec": audio.get("codec_name") if audio else None,
        }
    except (subprocess.CalledProcessError, json.JSONDecodeError, OSError) as exc:
        return {"error": str(exc)[-200:]}


def find_result(results_dir: Path, angle_id: str) -> Path | None:
    """Retrouve le MP4 du runner pour un angle (pur_<angle>_finale.mp4 ou variante)."""
    if not results_dir.exists():
        return None
    candidates = []
    for p in results_dir.rglob("*.mp4"):
        stem = p.stem.lower()
        if stem == f"pur_{angle_id.lower()}_finale" or stem == f"pur_{angle_id.lower()}" \
           or stem.endswith(f"_{angle_id.lower()}_finale"):
            candidates.append(p)
    # Préférence : le *_finale.mp4 exact, puis le plus gros fichier (rendu complet)
    candidates.sort(key=lambda p: (not p.stem.lower().endswith("_finale"), -p.stat().st_size))
    return candidates[0] if candidates else None


def main() -> int:
    parser = argparse.ArgumentParser(description="PUR aggregate : bundle multi-vidéos")
    parser.add_argument("--manifest", type=Path, required=True, help="pur_manifest.json multi-entrées")
    parser.add_argument("--results", type=Path, required=True, help="dossier des artifacts des runners")
    parser.add_argument("--out", type=Path, required=True, help="dossier du bundle final")
    parser.add_argument("--report", type=Path, default=None, help="rapport d'agrégation JSON")
    args = parser.parse_args()

    print(f"\n═══ PUR AGGREGATE — {now()} ═══")
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    entries = manifest.get("entries") or []
    if not entries:
        print("  [✗] manifeste sans entrées — rien à agréger")
        return 1

    results: list[dict] = []
    missing: list[str] = []
    args.out.mkdir(parents=True, exist_ok=True)

    for entry in entries:
        angle = normalize_angle(entry.get("angle_id") or entry.get("source_id") or entry.get("rank") or "?")
        found = find_result(args.results, angle)
        if found is None or found.stat().st_size < 1024:
            missing.append(angle)
            results.append({"angle_id": angle, "status": "MISSING", "expected_clip": entry.get("clip_file")})
            print(f"  [✗] {angle} : rendu absent ou vide")
            continue
        meta = probe(found)
        # Porte P-AUD (2026-09-11, décision Warsmith) : la voix du clip est
        # obligatoire (codex : « voix claire » hook) — un rendu sans piste
        # audio est un rendu muet, refusé comme un rendu manquant.
        if not meta.get("audio_codec"):
            missing.append(angle)
            results.append({"angle_id": angle, "status": "NO_AUDIO", "probe": meta, "expected_clip": entry.get("clip_file")})
            print(f"  [✗] {angle} : piste audio ABSENTE — rendu muet refusé (porte P-AUD)")
            continue
        dest = args.out / f"pur_{angle}_finale.mp4"
        dest.write_bytes(found.read_bytes())
        sha = None
        try:
            import hashlib
            sha = hashlib.sha256(dest.read_bytes()).hexdigest()
        except OSError:
            pass
        results.append({
            "angle_id": angle,
            "status": "OK",
            "file": dest.name,
            "bytes": dest.stat().st_size,
            "sha256": sha,
            "probe": meta,
            "expected_duration_seconds": entry.get("duration_seconds"),
        })
        print(f"  [✓] {angle} : {dest.name} ({dest.stat().st_size / 1e6:.1f} Mo, {meta.get('duration_seconds')}s)")

    complete = len(missing) == 0
    report = {
        "schema_version": "dev10.pur-aggregate.v1",
        "generated_at": now(),
        "schema_manifest": manifest.get("schema_version"),
        "expected_count": len(entries),
        "rendered_count": sum(1 for r in results if r["status"] == "OK"),
        "missing": missing,
        "complete": complete,
        "doctrine": "1 codex = N vidéos = 1 run = 1 zip — publication refusée si incomplet",
        "results": results,
    }
    report_path = args.report or (args.out / "pur_aggregate_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if not complete:
        print(f"\n═══ AGRÉGATION INCOMPLÈTE : {len(missing)} rendu(s) manquant(s) {missing} ═══")
        print("  → AUCUN bundle final ne sera publié (règle dev9 conservée).")
        return 1

    # Manifestes de traçabilité dans le bundle
    (args.out / "pur_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\n═══ BUNDLE COMPLET : {len(results)}/{len(entries)} vidéos → {args.out} ═══")
    return 0


if __name__ == "__main__":
    sys.exit(main())

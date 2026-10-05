#!/usr/bin/env python3
"""F00_PUR — Ingest segments VOD depuis les packs PUR de PERTURABO.

Le pack ne contient PAS la video : vod_url + start_sec + end_sec.
Telecharge UNIQUEMENT le segment via yt-dlp --download-sections.
Gates G0-G3. Aucune couche Caviar.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

MAX_SEGMENT_SECONDS = 150.0
DURATION_TOLERANCE_SEC = 0.5
REDRIFT_MAX_EXCESS_SEC = 3.0
ALLOWED_CODECS = {"h264", "vp9", "hevc", "av1"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def seconds_to_hms(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def load_pack(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def gate_g0_pack(pack: dict) -> tuple[bool, list[str]]:
    errors = []
    if not isinstance(pack, dict):
        return False, ["pack illisible"]
    if pack.get("mode") != "pur":
        errors.append(f"mode={pack.get('mode')!r}, attendu 'pur'")
    source = pack.get("source") or {}
    mi = pack.get("montage_instructions") or {}
    segment = mi.get("segment") or source
    vod_url = segment.get("source_url") or source.get("vod_url")
    if not vod_url:
        errors.append("vod_url absente (source.vod_url / montage_instructions.segment.source_url)")
    if source.get("start_sec") is None and segment.get("start_sec") is None:
        errors.append("start_sec absent")
    if source.get("end_sec") is None and segment.get("end_sec") is None:
        errors.append("end_sec absent")
    start = float(source.get("start_sec") if source.get("start_sec") is not None else segment.get("start_sec") or 0)
    end = float(source.get("end_sec") if source.get("end_sec") is not None else segment.get("end_sec") or 0)
    if end <= start:
        errors.append(f"segment invalide : end ({end}) <= start ({start})")
    if end - start > MAX_SEGMENT_SECONDS:
        errors.append(f"segment trop long ({end - start:.1f}s > {MAX_SEGMENT_SECONDS}s)")
    if not mi:
        errors.append("montage_instructions absente")
    return len(errors) == 0, errors


def build_ytdlp_command(vod_url: str, start: float, end: float, out_path: Path) -> list[str]:
    return [
        "yt-dlp",
        "--download-sections", f"*{seconds_to_hms(start)}-{seconds_to_hms(end)}",
        "--force-keyframes-at-cuts",
        "-f", "bv*[height<=1080]+ba/b",
        "--concurrent-fragments", "5",
        "--no-playlist",
        "-o", str(out_path),
        vod_url,
    ]


def probe_clip(path: Path) -> dict:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries",
        "stream=codec_name,codec_type,width,height:format=duration",
        "-of", "json", str(path),
    ]
    data = json.loads(subprocess.check_output(cmd, text=True))
    video = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    duration = float(data.get("format", {}).get("duration") or 0)
    return {
        "codec": video.get("codec_name") if video else None,
        "width": int(video.get("width") or 0) if video else 0,
        "height": int(video.get("height") or 0) if video else 0,
        "duration_seconds": round(duration, 3),
    }


def find_downloaded_file(out_dir: Path, stem: str) -> Path | None:
    candidates = (
        [p for p in out_dir.iterdir() if p.is_file() and p.stem == stem]
        if out_dir.exists()
        else []
    )
    for ext_priority in (".mp4", ".mkv", ".webm"):
        for c in candidates:
            if c.suffix.lower() == ext_priority:
                return c
    return candidates[0] if candidates else None


def main() -> int:
    parser = argparse.ArgumentParser(description="F00_PUR : ingest segment VOD depuis un pack PUR")
    parser.add_argument("--pack", type=Path, required=True, help="production_pack_pur_*.json")
    parser.add_argument("--out", type=Path, required=True, help="Dossier de sortie (clips + manifeste)")
    parser.add_argument("--clip-name", default=None, help="Nom du clip (defaut: pur_<angle_id>.mp4)")
    parser.add_argument("--append", action="store_true", help="Ajoute l'entree a pur_sources.json")
    parser.add_argument("--dry-run", action="store_true", help="Valide G0 sans telecharger")
    args = parser.parse_args()

    print(f"\n=== F00_PUR — {now()} ===")
    pack = load_pack(args.pack)

    ok, errors = gate_g0_pack(pack)
    if not ok:
        for e in errors:
            print(f"  [fail] G0 PACK : {e}")
        print("\n=== CONTROLE G0 : ECHOUE ===")
        return 1
    print("  [ok] G0 PACK : pack PUR valide")

    def _pur_speeds(node):
        found = []
        if isinstance(node, dict):
            ad = node.get("anti_detection")
            if isinstance(ad, dict) and ad.get("speed") is not None:
                try:
                    found.append(float(ad["speed"]))
                except (TypeError, ValueError):
                    pass
            for v in node.values():
                found.extend(_pur_speeds(v))
        elif isinstance(node, list):
            for v in node:
                found.extend(_pur_speeds(v))
        return found

    speeds = [s for s in _pur_speeds(pack) if s and s > 1.0]
    if speeds and max(speeds) > 1.03:
        print(f"  [!] G0 SPEED : speed max={max(speeds)} > 1.03 — acceleration perceptible.")

    mi = pack["montage_instructions"]
    segment = mi.get("segment") or pack.get("source") or {}
    vod_url = segment.get("source_url") or pack["source"].get("vod_url")
    start = float(segment.get("start_sec") if segment.get("start_sec") is not None else pack["source"]["start_sec"])
    end = float(segment.get("end_sec") if segment.get("end_sec") is not None else pack["source"]["end_sec"])
    expected_duration = end - start
    angle_id = (pack.get("identite") or {}).get("angle_id") or pack.get("pack_id") or "clip"
    clip_name = args.clip_name or f"pur_{angle_id}.mp4"

    cmd = build_ytdlp_command(vod_url, start, end, Path(clip_name))
    print(f"  Segment : {seconds_to_hms(start)} -> {seconds_to_hms(end)} ({expected_duration:.1f}s)")
    print(f"  VOD     : {vod_url}")

    if args.dry_run:
        print("  [dry-run] " + " ".join(cmd))
        print("\n=== DRY-RUN G0 : VALIDE ===")
        return 0

    if shutil.which("yt-dlp") is None:
        print("  [fail] G1 VOD : yt-dlp introuvable (pip install yt-dlp)")
        return 1
    args.out.mkdir(parents=True, exist_ok=True)
    out_pattern = args.out / clip_name.replace(".mp4", "")
    stale = [p for p in args.out.iterdir() if p.is_file() and p.stem == out_pattern.stem]
    for item in stale:
        item.unlink()
    if stale:
        print(f"  [..] G1 VOD : purge de {len(stale)} fichier(s) perime(s) {out_pattern.stem}*")
    cmd = build_ytdlp_command(vod_url, start, end, out_pattern)
    print("  [..] G1 VOD : telechargement du segment...")
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=300)
    except subprocess.CalledProcessError as exc:
        print(f"  [fail] G1 VOD : echec yt-dlp\n{exc.stderr[-800:] if exc.stderr else exc}")
        return 1
    downloaded = find_downloaded_file(args.out, out_pattern.stem)
    if downloaded is None:
        print("  [fail] G1 VOD : aucun fichier produit par yt-dlp")
        return 1
    print(f"  [ok] G1 VOD : {downloaded.name} ({downloaded.stat().st_size / 1e6:.1f} Mo)")

    clip_path = args.out / clip_name
    if downloaded.suffix.lower() != ".mp4":
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", str(downloaded),
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
             "-c:a", "aac", "-b:a", "192k", str(clip_path)],
            check=True)
        downloaded.unlink()
    else:
        shutil.move(str(downloaded), str(clip_path))

    meta = probe_clip(clip_path)
    excess = meta["duration_seconds"] - expected_duration
    if excess > DURATION_TOLERANCE_SEC and excess <= REDRIFT_MAX_EXCESS_SEC:
        print(f"  [..] G2 DUREE : +{excess:.2f}s (derive fragments) -> re-decoupe locale...")
        fixed = clip_path.with_name(clip_path.stem + "_g2fix.mp4")
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", str(clip_path),
             "-t", f"{expected_duration:.3f}",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
             "-c:a", "aac", str(fixed)],
            check=True, capture_output=True, text=True, timeout=180)
        meta2 = probe_clip(fixed)
        if abs(meta2["duration_seconds"] - expected_duration) <= DURATION_TOLERANCE_SEC and meta2["codec"] in ALLOWED_CODECS:
            fixed.replace(clip_path)
            meta = meta2
            print(f"  [ok] G2 DUREE : re-decoupe OK -> {meta['duration_seconds']}s")
    if abs(meta["duration_seconds"] - expected_duration) > DURATION_TOLERANCE_SEC:
        print(f"  [fail] G2 DUREE : {meta['duration_seconds']}s != {expected_duration}s +/-{DURATION_TOLERANCE_SEC}")
        return 1
    print(f"  [ok] G2 DUREE : {meta['duration_seconds']}s (attendu {expected_duration}s)")

    if meta["codec"] not in ALLOWED_CODECS:
        print(f"  [fail] G3 CODEC : {meta['codec']} non lisible")
        return 1
    print(f"  [ok] G3 CODEC : {meta['codec']} {meta['width']}x{meta['height']}")

    entry = {
        "pack_id": pack.get("pack_id"),
        "angle_id": angle_id,
        "vod_url": vod_url,
        "start_sec": start,
        "end_sec": end,
        "expected_duration_sec": expected_duration,
        "clip_file": f"clips/{clip_name}",
        "probe": meta,
        "gates": {"G0": "PASSED", "G1": "PASSED", "G2": "PASSED", "G3": "PASSED"},
    }
    sources_path = args.out / "pur_sources.json"
    if args.append and sources_path.exists():
        try:
            existing = json.loads(sources_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            existing = None
        if existing and isinstance(existing.get("segments"), list):
            existing["segments"] = [s for s in existing["segments"] if s.get("angle_id") != angle_id]
            existing["segments"].append(entry)
            existing["generated_at"] = now()
            existing["segment_count"] = len(existing["segments"])
            sources = existing
        else:
            sources = {
                "schema_version": "dev10-v2.pur-sources.v2",
                "generated_at": now(),
                "segments": [existing, entry] if existing else [entry],
                "segment_count": 1 if not existing else 2,
            }
    else:
        sources = {
            "schema_version": "dev10-v2.pur-sources.v1",
            "generated_at": now(),
            **entry,
        }
    sources_path.write_text(json.dumps(sources, indent=2), encoding="utf-8")
    print(f"\n=== F00_PUR : MISSION ACCOMPLIE — {clip_path} ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())

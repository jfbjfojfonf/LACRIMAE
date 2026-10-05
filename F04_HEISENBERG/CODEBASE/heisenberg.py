#!/usr/bin/env python3
"""F04_HEISENBERG — frégate TEMPS. MP4 LOOK + manifeste → MP4 reel.

Execute jump cuts, punch-in-cut, B-roll + flash d'entree, SFX sous la voix.
Jamais de zoom/swell/scale anime. Jamais une sortie JSON sans MP4.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ALLOWED_STYLES = {"blur", "split_scene", "reframing"}
JUMP_CUT_TYPES = {"breath_cut", "idea_cut"}
JUMP_SKIP_SEC = 0.08
FLASH_FRAMES = 5
DUCK_SFX_SEC = 0.25
DUCK_SMASH_SEC = 0.12
DUCK_VOICE = 0.35
BANNED_FILTERS = ("zoompan", "swell", "breathing_zoom")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def angle_of(entry: dict) -> str:
    raw = str(entry.get("angle_id") or entry.get("source_id") or "clip")
    return raw[4:] if raw.lower().startswith("pur_") and len(raw) > 4 else raw


def probe(path: Path) -> dict:
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


def merge_intervals(windows: list[tuple[float, float]]) -> list[tuple[float, float]]:
    ordered = sorted((float(a), float(b)) for a, b in windows if b > a)
    if not ordered:
        return []
    out = [ordered[0]]
    for start, end in ordered[1:]:
        last_s, last_e = out[-1]
        if start <= last_e:
            out[-1] = (last_s, max(last_e, end))
        else:
            out.append((start, end))
    return out


def plan_skips(entry: dict) -> list[tuple[float, float]]:
    duration = float(entry.get("duration_seconds") or 0)
    skips = []
    for cut in entry.get("cuts") or []:
        kind = str(cut.get("type") or "")
        if kind not in JUMP_CUT_TYPES:
            continue
        t = float(cut.get("moment_sec") or 0)
        skips.append((max(0.0, t), min(duration, t + JUMP_SKIP_SEC)))
    return merge_intervals(skips)


def plan_punches(entry: dict) -> list[dict]:
    punches = []
    for punch in entry.get("punch_ins") or []:
        start = float(punch.get("in_sec") or 0)
        end = float(punch.get("out_sec") or start)
        if end <= start:
            end = start + (1.0 / 30.0)
        punches.append({
            "in_sec": start,
            "out_sec": end,
            "scale": max(1.0, float(punch.get("scale") or 1.08)),
        })
    return punches


def subtract_skips(start: float, end: float, skips: list[tuple[float, float]]) -> list[tuple[float, float]]:
    pieces = [(start, end)]
    for skip_s, skip_e in skips:
        next_pieces = []
        for a, b in pieces:
            if skip_e <= a or skip_s >= b:
                next_pieces.append((a, b))
                continue
            if a < skip_s:
                next_pieces.append((a, skip_s))
            if skip_e < b:
                next_pieces.append((skip_e, b))
        pieces = next_pieces
    return [(a, b) for a, b in pieces if b - a > 0.001]


def plan_segments(entry: dict) -> list[dict]:
    duration = float(entry.get("duration_seconds") or 0)
    skips = plan_skips(entry)
    punches = plan_punches(entry)
    cuts = [0.0, duration]
    for punch in punches:
        cuts.extend([punch["in_sec"], punch["out_sec"]])
    for skip_s, skip_e in skips:
        cuts.extend([skip_s, skip_e])
    bounds = sorted({max(0.0, min(duration, c)) for c in cuts})
    segments = []
    for i in range(len(bounds) - 1):
        a, b = bounds[i], bounds[i + 1]
        kept = subtract_skips(a, b, skips)
        for ks, ke in kept:
            punch = next((p for p in punches if ks + 1e-6 >= p["in_sec"] and ke - 1e-6 <= p["out_sec"]), None)
            segments.append({
                "in_sec": round(ks, 4),
                "out_sec": round(ke, 4),
                "mode": "punch_in_cut" if punch else "normal",
                "scale": punch["scale"] if punch else 1.0,
            })
    return segments


def source_to_output(source_sec: float, segments: list[dict]) -> float:
    t = 0.0
    for seg in segments:
        if source_sec < seg["in_sec"]:
            return t
        if source_sec <= seg["out_sec"]:
            return t + (source_sec - seg["in_sec"])
        t += seg["out_sec"] - seg["in_sec"]
    return t


def assert_no_zoom(filtergraph: str) -> None:
    lowered = filtergraph.lower()
    for token in BANNED_FILTERS:
        if token in lowered:
            raise RuntimeError(f"P-ZOOM ZERO : filtre interdit « {token} »")


def find_sfx(sfx_dirs: list[Path], kind: str) -> Path | None:
    name = "impact" if kind == "boom" else kind
    for folder in sfx_dirs:
        candidate = folder / f"{name}.mp3"
        if candidate.is_file():
            return candidate
        wav = folder / f"{name}.wav"
        if wav.is_file():
            return wav
    return None


def run_ffmpeg(cmd: list[str]) -> None:
    assert_no_zoom(" ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr[-2000:] or result.stdout[-2000:])


def duck_windows(sfx: list[dict], broll: list[dict], smash_times: list[float] | None = None) -> list[tuple[float, float]]:
    windows: list[tuple[float, float]] = []
    for item in sfx or []:
        start = float(item.get("out_sec") or 0)
        windows.append((start, start + DUCK_SFX_SEC))
    for item in broll or []:
        if item.get("duck", True):
            windows.append((float(item.get("out_in_sec") or 0), float(item.get("out_out_sec") or 0)))
    for moment in smash_times or []:
        start = float(moment)
        windows.append((start, start + DUCK_SMASH_SEC))
    return merge_intervals([(a, b) for a, b in windows if b > a])


def volume_enable(windows: list[tuple[float, float]]) -> str:
    parts = [f"between(t,{a:.4f},{b:.4f})" for a, b in windows]
    return "+".join(parts)


def build_filter(segments: list[dict], width: int, height: int, has_audio: bool,
                 broll: list[dict], sfx: list[dict], fps: int,
                 smash_times: list[float] | None = None) -> tuple[str, int]:
    parts: list[str] = []
    video_labels: list[str] = []
    audio_labels: list[str] = []
    for i, seg in enumerate(segments):
        vlab = f"v{i}"
        chain = f"trim=start={seg['in_sec']}:end={seg['out_sec']},setpts=PTS-STARTPTS"
        if seg["mode"] == "punch_in_cut" and seg["scale"] > 1.0:
            scale = seg["scale"]
            crop_w = max(2, int(width / scale) // 2 * 2)
            crop_h = max(2, int(height / scale) // 2 * 2)
            chain += f",crop={crop_w}:{crop_h}:(iw-{crop_w})/2:(ih-{crop_h})/2,scale={width}:{height}"
        else:
            chain += f",scale={width}:{height}"
        parts.append(f"[0:v]{chain},setsar=1[{vlab}]")
        video_labels.append(f"[{vlab}]")
        if has_audio:
            alab = f"a{i}"
            parts.append(
                f"[0:a]atrim=start={seg['in_sec']}:end={seg['out_sec']},asetpts=PTS-STARTPTS[{alab}]"
            )
            audio_labels.append(f"[{alab}]")
    n = len(segments)
    parts.append("".join(video_labels) + f"concat=n={n}:v=1:a=0[vcat]")
    current_v = "vcat"
    extra_inputs = 0
    for b_i, item in enumerate(broll):
        extra_inputs += 1
        idx = extra_inputs
        in_s = float(item["out_in_sec"])
        out_s = float(item["out_out_sec"])
        dur = max(0.04, out_s - in_s)
        parts.append(
            f"[{idx}:v]scale={width}:{height},setsar=1,trim=duration={dur},setpts=PTS-STARTPTS[br{b_i}]"
        )
        parts.append(
            f"[{current_v}][br{b_i}]overlay=x=0:y=0:enable='between(t,{in_s},{out_s})'[vo{b_i}]"
        )
        current_v = f"vo{b_i}"
        if item.get("flash_in", True):
            flash_end = in_s + (FLASH_FRAMES / max(1, fps))
            parts.append(
                f"[{current_v}]drawbox=x=0:y=0:w=iw:h=ih:color=white@0.85:t=fill:"
                f"enable='between(t,{in_s},{flash_end})'[vf{b_i}]"
            )
            current_v = f"vf{b_i}"
    parts.append(f"[{current_v}]format=yuv420p[outv]")
    if has_audio:
        parts.append("".join(audio_labels) + f"concat=n={n}:v=0:a=1[acat]")
        ducks = duck_windows(sfx, broll, smash_times)
        enable = volume_enable(ducks)
        if enable:
            parts.append(
                f"[acat]volume={DUCK_VOICE}:enable='{enable}'[aduck]"
            )
            current_a = "aduck"
        else:
            current_a = "acat"
        for s_i, item in enumerate(sfx):
            extra_inputs += 1
            idx = extra_inputs
            delay_ms = max(0, int(round(float(item["out_sec"]) * 1000)))
            vol = float(item.get("volume") or 0.55)
            parts.append(f"[{idx}:a]adelay={delay_ms}|{delay_ms},volume={vol}[sx{s_i}]")
            parts.append(
                f"[{current_a}][sx{s_i}]amix=inputs=2:duration=first:dropout_transition=0[am{s_i}]"
            )
            current_a = f"am{s_i}"
        parts.append(
            f"[{current_a}]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[outa]"
        )
    return ";".join(parts), extra_inputs


def resolve_look_mp4(path: Path, angle: str) -> Path:
    if path.is_file():
        return path
    if path.is_dir():
        for name in (f"pur_{angle}_look.mp4", f"pur_{angle}.mp4"):
            candidate = path / name
            if candidate.is_file():
                return candidate
    raise FileNotFoundError(f"MP4 LOOK introuvable pour {angle} : {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="F04_HEISENBERG — execution TEMPS PUR")
    parser.add_argument("--input", type=Path, required=True, help="MP4 PICTOR (fichier ou dossier)")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--entry", type=int, default=0)
    parser.add_argument("--sfx-dir", type=Path, default=None)
    parser.add_argument("--broll-dir", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(f"\n=== F04_HEISENBERG — {now()} ===")
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        print("  [fail] ffmpeg/ffprobe introuvable")
        return 1
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "dev10.pur.v1":
        print(f"  [fail] schema_version={manifest.get('schema_version')}")
        return 1
    style = str(manifest.get("style") or "")
    if style not in ALLOWED_STYLES:
        print(f"  [fail] P-ZOOM/G0-S : style {style!r} hors blur/split_scene/reframing")
        return 2
    entries = manifest.get("entries") or []
    if not entries:
        print("  [fail] manifeste sans entrees")
        return 1
    index = max(0, min(args.entry, len(entries) - 1))
    entry = entries[index]
    angle = angle_of(entry)
    look = resolve_look_mp4(args.input, angle)
    meta = probe(look)
    if not meta.get("width") or not meta.get("height"):
        print(f"  [fail] P3 : LOOK illisible {look}")
        return 1
    fps = int(manifest.get("fps") or 30)
    duration = float(entry.get("duration_seconds") or meta["duration_seconds"])
    entry = {**entry, "duration_seconds": duration}
    segments = plan_segments(entry)
    if not segments:
        print("  [fail] P3 : timeline vide")
        return 1

    broll_dir = args.broll_dir or args.input.parent
    broll_mapped = []
    for item in entry.get("broll") or []:
        src = Path(str(item.get("file") or ""))
        if not src.is_file():
            src = broll_dir / src.name if src.name else None
        if not src or not src.is_file():
            print(f"  [!] B-roll manquant ({item.get('file')}) — ignore")
            continue
        broll_mapped.append({
            **item,
            "path": src,
            "out_in_sec": source_to_output(float(item.get("in_sec") or 0), segments),
            "out_out_sec": source_to_output(float(item.get("out_sec") or 0), segments),
            "flash_in": item.get("flash_in", True),
        })

    sfx_dirs = [
        args.sfx_dir,
        Path(__file__).resolve().parent / "sfx",
        Path(__file__).resolve().parents[2] / "F03_PICTOR" / "CODEBASE" / "public" / "sfx",
    ]
    sfx_dirs = [p for p in sfx_dirs if p]
    sfx_mapped = []
    if meta.get("audio_codec"):
        for item in entry.get("sfx_list") or []:
            kind = str(item.get("type") or "impact")
            path = find_sfx(sfx_dirs, kind)
            if path is None:
                continue
            sfx_mapped.append({
                **item,
                "path": path,
                "out_sec": source_to_output(float(item.get("moment_sec") or 0), segments),
            })
    smash_times = [
        source_to_output(float(c.get("moment_sec") or 0), segments)
        for c in (entry.get("cuts") or [])
        if str(c.get("type") or "") == "smash_cut"
    ]

    graph, extra = build_filter(
        segments, meta["width"], meta["height"], bool(meta.get("audio_codec")),
        broll_mapped, sfx_mapped, fps, smash_times,
    )
    assert_no_zoom(graph)

    args.out.mkdir(parents=True, exist_ok=True)
    dest = args.out / f"pur_{angle}.mp4"
    report = {
        "schema_version": "dev10-v2.heisenberg.v1",
        "created_at": now(),
        "angle_id": angle,
        "input": str(look),
        "output": str(dest),
        "segments": segments,
        "jump_cuts": plan_skips(entry),
        "punch_ins": [s for s in segments if s["mode"] == "punch_in_cut"],
        "broll_count": len(broll_mapped),
        "sfx_count": len(sfx_mapped),
        "filtergraph": graph,
        "dry_run": bool(args.dry_run),
    }
    (args.out / f"heisenberg_{angle}_plan.json").write_text(
        json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8")

    if args.dry_run:
        print(f"  [dry-run] {len(segments)} segments, punch-in={len(report['punch_ins'])}, "
              f"broll={len(broll_mapped)}, sfx={len(sfx_mapped)}")
        print("  [dry-run] aucun MP4 ecrit")
        return 0

    cmd = ["ffmpeg", "-y", "-i", str(look)]
    for item in broll_mapped:
        cmd += ["-i", str(item["path"])]
    for item in sfx_mapped:
        cmd += ["-i", str(item["path"])]
    maps = ["-map", "[outv]"]
    if meta.get("audio_codec") or sfx_mapped:
        maps += ["-map", "[outa]"]
    cmd += ["-filter_complex", graph, *maps, "-c:v", "libx264", "-preset", "veryfast",
            "-crf", "18", "-pix_fmt", "yuv420p"]
    if meta.get("audio_codec") or sfx_mapped:
        cmd += ["-c:a", "aac", "-b:a", "192k"]
    cmd += ["-movflags", "+faststart", str(dest)]
    print(f"  [..] P3 TEMPS {angle} → {dest}")
    try:
        run_ffmpeg(cmd)
    except RuntimeError as exc:
        print(f"  [fail] P3 ffmpeg : {exc}")
        return 1
    if not dest.is_file() or dest.stat().st_size < 1024:
        print("  [fail] P3 : MP4 absent ou vide — pas de livraison")
        return 1
    after = probe(dest)
    report["probe"] = after
    report["qa_pass"] = bool(after.get("width") and after.get("codec"))
    (args.out / f"heisenberg_{angle}_report.json").write_text(
        json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8")
    if not report["qa_pass"]:
        print("  [fail] P3 : MP4 illisible")
        return 1
    print(f"  [ok] P3 TEMPS {angle} ({after['duration_seconds']}s, {after['width']}x{after['height']})")
    print(f"\n=== HEISENBERG : MISSION ACCOMPLIE — {dest} ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())

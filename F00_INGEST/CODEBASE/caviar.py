#!/usr/bin/env python3
"""CAVIAR — couche narrative du bras armé (spec TRACKING/CAVIAR_SPEC_PERTURABO.md).

Deux responsabilités, aucune interprétation créative :

1. gate_pcav_budgets()  — PORTE BLOQUANTE P-CAV : valide les champs narratifs
   OPTIONNELS du pack (narrative / broll / audio_design) et fait ÉCHOUER le job
   si un budget anti-saturation est dépassé. Champs absents = bypass (packs v1).

2. analyze_clip()       — LE DIRECTEUR (advisory) : analyse le clip téléchargé
   et produit des PROPOSITIONS (silences → Jump Cuts, pics RMS → candidats
   is_climax, mots → punchline). Rien n'est appliqué sans validation du
   manifeste/opérateur. Whisper CPU optionnel (jamais bloquant).
"""
from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "dev10.caviar.v1"

# ── Budgets anti-saturation (spec §5) — des PORTES, pas des warnings ──
MAX_BROLL = 3
MAX_BROLL_FRAMES = 45          # 1,5 s à 30 fps
MAX_FLASHES = 3
MIN_FLASH_GAP_SEC = 1.5
MAX_PUNCHINS = 4
MIN_PUNCHIN_GAP_SEC = 2.0
UNIQUE_ELEMENT_WINDOW_SEC = 0.05   # 2 événements visuels forts à <50 ms = superposition
VALID_HOOK_TYPES = {"climax_first", "reframe", "question"}
VALID_ENERGY = {"rise", "peak", "fall"}
DEFAULT_FPS = 30.0


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def has_caviar_fields(pack: dict) -> bool:
    """True si le pack porte au moins un champ narratif Caviar (v2)."""
    mi = pack.get("montage_instructions") or {}
    return any(k in mi for k in ("narrative", "broll", "audio_design"))


def _mi(pack: dict) -> dict:
    return pack.get("montage_instructions") or {}


def _events_sec(pack: dict, fps: float) -> tuple[list[dict], list[str]]:
    """Événements visuels forts (zooms + broll) normalisés en secondes."""
    events: list[dict] = []
    errors: list[str] = []
    mi = _mi(pack)
    for i, z in enumerate(mi.get("zooms") or []):
        f = z.get("moment_frame")
        if f is None:
            errors.append(f"zooms[{i}] : moment_frame absent")
            continue
        events.append({"kind": "zoom", "i": i, "sec": float(f) / fps,
                       "flash": z.get("white_flash") in (True, "true")})
    for i, b in enumerate(mi.get("broll") or []):
        s = b.get("start_sec", b.get("start_frame") / fps if b.get("start_frame") is not None else None)
        if s is None:
            errors.append(f"broll[{i}] : start_sec (ou start_frame) absent")
            continue
        events.append({"kind": "broll", "i": i, "sec": float(s),
                       "flash": b.get("entry_flash") in (True, "true")})
    return events, errors


def gate_pcav_budgets(pack: dict, expected_duration: float | None = None,
                      fps: float | None = None) -> tuple[bool, list[str]]:
    """Porte P-CAV : (ok, errors). Champ invalide PRÉSENT = rouge ; absent = bypass."""
    errors: list[str] = []
    mi = _mi(pack)
    if fps is None:
        fps = float(mi.get("fps") or pack.get("fps") or DEFAULT_FPS)

    narrative = mi.get("narrative") or {}
    broll = mi.get("broll") or []
    audio = mi.get("audio_design") or {}

    # ── Schéma : valeurs invalides refusées ──
    if "hook_type" in narrative and narrative["hook_type"] not in VALID_HOOK_TYPES:
        errors.append(f"narrative.hook_type invalide : {narrative['hook_type']!r} (attendu parmi {sorted(VALID_HOOK_TYPES)})")
    if "energy_curve" in narrative:
        curve = narrative["energy_curve"]
        if not (isinstance(curve, list) and curve and all(c in VALID_ENERGY for c in curve)):
            errors.append(f"narrative.energy_curve invalide : {curve!r} (attendu une liste parmi {sorted(VALID_ENERGY)})")
    if "is_climax" in narrative:
        cl = narrative["is_climax"]
        if not (isinstance(cl, list) and all(isinstance(x, (int, float)) and x >= 0 for x in cl)):
            errors.append("narrative.is_climax doit être une liste de secondes ≥ 0")
        elif expected_duration is not None and any(x > expected_duration for x in cl):
            errors.append(f"narrative.is_climax hors segment : {[x for x in cl if x > expected_duration]} > {expected_duration}s")
    if "resolution_at" in narrative:
        r = narrative["resolution_at"]
        if not (isinstance(r, (int, float)) and 0 <= r):
            errors.append("narrative.resolution_at doit être un nombre de secondes ≥ 0")

    # ── B-roll : quantité, durée, SFX obligatoire ──
    if len(broll) > MAX_BROLL:
        errors.append(f"broll : {len(broll)} éléments > budget {MAX_BROLL} par clip")
    resolution_at = narrative.get("resolution_at")
    for i, b in enumerate(broll):
        frames = b.get("duration_frames")
        if frames is None:
            errors.append(f"broll[{i}] : duration_frames absent")
        elif not (isinstance(frames, int) and 0 < frames <= MAX_BROLL_FRAMES):
            errors.append(f"broll[{i}] : duration_frames={frames} > budget {MAX_BROLL_FRAMES} frames (1,5 s)")
        if not b.get("sfx"):
            errors.append(f"broll[{i}] : sfx obligatoire (un visuel sans son = impression de bug)")
        if resolution_at is not None and isinstance(b.get("start_sec"), (int, float)) \
                and float(b["start_sec"]) >= float(resolution_at):
            errors.append(f"broll[{i}] démarre ({b['start_sec']}s) pendant la résolution (≥ {resolution_at}s) — payoff propre obligatoire")

    # ── Événements + flashs ──
    events, ev_errors = _events_sec(pack, fps)
    errors.extend(ev_errors)
    flashes = sorted(e["sec"] for e in events if e["flash"])
    if len(flashes) > MAX_FLASHES:
        errors.append(f"flashs blancs : {len(flashes)} > budget {MAX_FLASHES} par clip")
    for a, b2 in zip(flashes, flashes[1:]):
        if b2 - a < MIN_FLASH_GAP_SEC:
            errors.append(f"flashs trop rapprochés : {a:.2f}s et {b2:.2f}s (min {MIN_FLASH_GAP_SEC}s)")

    # ── Punch-ins (zooms) : quantité + espacement ──
    zooms = [e for e in events if e["kind"] == "zoom"]
    if len(zooms) > MAX_PUNCHINS:
        errors.append(f"zooms : {len(zooms)} > budget {MAX_PUNCHINS} par clip")
    zs = sorted(z["sec"] for z in zooms)
    for a, b2 in zip(zs, zs[1:]):
        if b2 - a < MIN_PUNCHIN_GAP_SEC:
            errors.append(f"zooms trop rapprochés : {a:.2f}s et {b2:.2f}s (min {MIN_PUNCHIN_GAP_SEC}s)")

    # ── Règle de l'élément unique : pas de superposition d'événements forts ──
    times = sorted((e["sec"], f"{e['kind']}[{e['i']}]") for e in events)
    for (t1, n1), (t2, n2) in zip(times, times[1:]):
        if abs(t2 - t1) < UNIQUE_ELEMENT_WINDOW_SEC:
            errors.append(f"superposition d'événements : {n1} et {n2} à {t1:.2f}s (règle de l'élément unique)")

    # ── Flashs de zooms couplés à un SFX sur la même frame ──
    sfx_frames = [float(s.get("moment_frame", -1)) for s in (mi.get("sfx_list") or [])]
    for e in events:
        if e["kind"] == "zoom" and e["flash"]:
            e_frame = e["sec"] * fps
            if not any(abs(sf - e_frame) <= fps * 0.05 for sf in sfx_frames):
                errors.append(f"zooms[{e['i']}] : white_flash sans SFX sur la même frame — impact sourd interdit")

    # ── audio_design : valeurs ──
    duck = audio.get("duck_at_climax") or {}
    if duck and not (isinstance(duck.get("db"), (int, float)) and duck["db"] <= 0):
        errors.append("audio_design.duck_at_climax.db doit être ≤ 0 (ducking)")
    if "silence_before_punchline" in audio and not isinstance(audio["silence_before_punchline"], bool):
        errors.append("audio_design.silence_before_punchline doit être un booléen")

    return (len(errors) == 0), errors


# ═══════════════════════════════════════════════════════════════════
# LE DIRECTEUR — analyse advisory (propositions, jamais appliquées)
# ═══════════════════════════════════════════════════════════════════

SILENCE_NOISE_DB = "-35dB"
SILENCE_MIN_D = 0.25
RMS_WINDOW_MS = 50


def _detect_silences(clip: Path) -> list[dict]:
    """ffmpeg silencedetect → [{start, end, duration_sec}]."""
    proc = subprocess.run(
        ["ffmpeg", "-i", str(clip), "-af",
         f"silencedetect=noise={SILENCE_NOISE_DB}:d={SILENCE_MIN_D}", "-f", "null", "-"],
        capture_output=True, text=True, timeout=300)
    text = proc.stderr
    silences: list[dict] = []
    open_start: float | None = None
    for line in text.splitlines():
        m = re.search(r"silence_start:\s*([0-9.]+)", line)
        if m:
            open_start = float(m.group(1))
            continue
        m = re.search(r"silence_end:\s*([0-9.]+)(?:\s*\|\s*silence_duration:\s*([0-9.]+))?", line)
        if m and open_start is not None:
            end = float(m.group(1))
            dur = float(m.group(2)) if m.group(2) else end - open_start
            if dur >= SILENCE_MIN_D:
                silences.append({"start": round(open_start, 3), "end": round(end, 3),
                                 "duration_sec": round(dur, 3)})
            open_start = None
    if open_start is not None:  # silence final non refermé
        dur = 0.5  # borne conservatrice ; le trim s'arrêtera à la fin du clip
        silences.append({"start": round(open_start, 3), "end": round(open_start + dur, 3),
                         "duration_sec": dur})
    return silences


def _rms_series(clip: Path) -> list[tuple[float, float]]:
    """RMS (dB) par fenêtres de 50 ms → [(temps, rms_db)]."""
    proc = subprocess.run(
        ["ffmpeg", "-i", str(clip), "-af",
         f"asetnsamples=n={int(44100 * RMS_WINDOW_MS / 1000)}:p=0,"
         "astats=metadata=1:reset=1,"
         "ametadata=print:key=lavfi.astats.Overall.RMS_level:file=-",
         "-f", "null", "-"],
        capture_output=True, text=True, timeout=300)
    series: list[tuple[float, float]] = []
    t: float | None = None
    for line in (proc.stdout or "").splitlines() + (proc.stderr or "").splitlines():
        m = re.search(r"pts_time:([0-9.]+)", line)
        if m:
            t = float(m.group(1))
            continue
        m = re.search(r"lavfi\.astats\.Overall\.RMS_level=(-?[0-9.]+|-inf)", line)
        if m and t is not None:
            v = m.group(1)
            series.append((t, -90.0 if v == "-inf" else float(v)))
            t = None
    return series


def _peak_clusters(series: list[tuple[float, float]], max_clusters: int = 3) -> list[dict]:
    """Clusters de fenêtres bruyantes (RMS > moyenne + 2σ) → candidats is_climax."""
    vals = [v for _, v in series if v > -60]
    if len(vals) < 4:
        return []
    mean = sum(vals) / len(vals)
    var = sum((v - mean) ** 2 for v in vals) / len(vals)
    thr = mean + 2 * (var ** 0.5)
    clusters: list[dict] = []
    cur: list[tuple[float, float]] = []
    for t, v in series:
        if v > thr and v > -60:
            cur.append((t, v))
        elif cur:
            peak_t, peak_v = max(cur, key=lambda x: x[1])
            clusters.append({"start": round(cur[0][0], 2), "end": round(cur[-1][0], 2),
                             "peak_sec": round(peak_t, 2), "rms_db": round(peak_v, 1)})
            cur = []
    if cur:
        peak_t, peak_v = max(cur, key=lambda x: x[1])
        clusters.append({"start": round(cur[0][0], 2), "end": round(cur[-1][0], 2),
                         "peak_sec": round(peak_t, 2), "rms_db": round(peak_v, 1)})
    clusters.sort(key=lambda c: c["rms_db"], reverse=True)
    return clusters[:max_clusters]


def _whisper_words(clip: Path) -> dict:
    """Timestamps de mots (faster-whisper CPU, optionnel — jamais bloquant)."""
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except Exception as exc:
        return {"available": False, "reason": f"faster-whisper indisponible : {exc}"}
    try:
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _info = model.transcribe(str(clip), word_timestamps=True, language=None)
        words: list[dict] = []
        for seg in segments:
            for w in (seg.words or []):
                words.append({"start": round(float(w.start), 3),
                              "end": round(float(w.end), 3),
                              "word": (w.word or "").strip()})
        punchline = None
        best_gap = 0.0
        for a, b in zip(words, words[1:]):
            gap = b["start"] - a["end"]
            if gap > best_gap:
                best_gap = gap
                punchline = a["end"]  # dernier mot avant la plus longue pause = chute probable
        strong = [w["end"] for w in words if w["word"].endswith(("!", "?"))]
        return {"available": True, "model": "base/cpu-int8", "word_count": len(words),
                "punchline_proposal_sec": round(punchline, 2) if punchline else None,
                "strong_punctuation_ends": [round(x, 2) for x in strong[:5]]}
    except Exception as exc:
        return {"available": False, "reason": f"transcription échouée : {exc}"}


def analyze_clip(clip_path: Path, expected_duration: float,
                 with_whisper: bool = True) -> dict:
    """Analyse complète d'un clip téléchargé → PROPOSITIONS (advisory)."""
    clip_path = Path(clip_path)
    silences = _detect_silences(clip_path)
    series = _rms_series(clip_path)
    clusters = _peak_clusters(series)
    speech = sum(s["duration_sec"] for s in silences)
    total = float(expected_duration)
    result = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now(),
        "source_file": clip_path.name,
        "duration_sec": total,
        "silences": silences,
        "silence_count": len(silences),
        "speech_ratio": round(1.0 - min(1.0, speech / total), 3) if total else None,
        "trim_proposals": [
            {"cut_at_sec": s["end"], "removes_sec": s["duration_sec"],
             "kind": "jump_cut", "status": "PROPOSAL"}
            for s in silences
        ],
        "rms_peak_clusters": clusters,
        "climax_proposals": [c["peak_sec"] for c in clusters],
        "notes": [
            "PROPOSITIONS uniquement — application sur validation manifeste/opérateur",
            "le bras armé propose, le cerveau dispose (spec §4)",
        ],
    }
    if with_whisper:
        result["whisper"] = _whisper_words(clip_path)
    return result


if __name__ == "__main__":
    import argparse as _ap
    p = _ap.ArgumentParser(description="Analyse Caviar d'un clip (advisory)")
    p.add_argument("clip", type=Path)
    p.add_argument("--duration", type=float, default=30.0)
    p.add_argument("--no-whisper", action="store_true")
    a = p.parse_args()
    print(json.dumps(analyze_clip(a.clip, a.duration, with_whisper=not a.no_whisper), indent=2))

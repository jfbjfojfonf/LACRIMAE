#!/usr/bin/env python3
"""HEISENBERG — sous-frégate Caviar du bras armé (embarquée dans F03_PICTOR).

Mission unique : servir la frégate. Elle reçoit les vidéos FINIES produites par
F03_PICTOR (validées par le gate qui suit F03), les analyse, et émet un
caviar_manifest.json PAR vidéo — le JSON que PERTURABO embarque dans le pack
et que le bras armé transformera en clip caviar au rendu.

Architecture (tout vit ICI, isolé — rien d'autre n'est modifié) :
  HEISENBERG/
  ├── heisenberg.py        ← ce moteur (aucune décision créative)
  ├── caviar_budget.json   ← Budget d'Attention (source de vérité unique)
  ├── BROLL/
  │   ├── registry.json    ← registre NUMÉROTÉ (PERTURABO ne voit jamais les fichiers)
  │   ├── FILES/           ← les .mp4/.png réels (jamais commités)
  │   └── candidates/      ← propositions d'ajout (une fiche = un numéro candidat)
  ├── IN/                  ← vidéos reçues de F03_PICTOR (input)
  ├── OUT/                 ← caviar_manifest_<angle>.json émis (output)
  └── LEDGER/              ← manifest_ledger.json + gate_history.json (ARCHIVUM-friendly)

Doctrine (spec CAVIAR §4) : PERTURABO = le OÙ/QUOI · LACRIMAE = le COMMENT ·
Warsmith tranche. Heisenberg ANALYSE et PROPOSE ; elle n'écrit pas l'accroche,
elle ne choisit pas le segment, elle ne décide pas du style.

Usage :
  python3 heisenberg.py --manifest OUT/pur_A01_finale.mp4                 # une vidéo
  python3 heisenberg.py --batch IN/                                      # toutes les IN/
  python3 heisenberg.py --manifest ... --emit-pack-chunk                 # chunk PERTURABO
  python3 heisenberg.py --broll "met le numéro 1" --at 8.5               # résolution d'un numéro
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HEISENBERG_ROOT = Path(__file__).resolve().parent
SCHEMA_VERSION = "dev10.caviar.v1"

JUMPCUT_GAP_SEC = 8.0
JUMPCUT_WINDOW_MAX_SEC = 2.0
JUMPCUT_WINDOW_DEFAULT_SEC = 1.5
JUMPCUT_SCALE = 1.20
HOOK_END_SEC = 3.0
OUTRO_SEC = 1.0
SILENCE_CUT_DEAD = 0.70
SILENCE_CUT_LAG = 1.0
SILENCE_KEEP_BREATH = 0.45
FLASH_FRAMES = 5
FLASH_FPS = 30.0

# Le Budget d'Attention est ingéré depuis caviar_budget.json — UNE source de
# vérité partagée avec PERTURABO (pas de constante dupliquée dans le code).
_budget_cache: dict | None = None


def load_budget() -> dict:
    global _budget_cache
    if _budget_cache is None:
        path = HEISENBERG_ROOT / "caviar_budget.json"
        _budget_cache = json.loads(path.read_text(encoding="utf-8"))
    return _budget_cache


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log(msg: str) -> None:
    print(msg, flush=True)


# ═══════════════════════════════════════════════════════════════════
# ANALYSE — réutilisation du Directeur Caviar (F00_INGEST, zéro doublon)
# ═══════════════════════════════════════════════════════════════════

_CODEBASE_F00 = Path(__file__).resolve().parents[2] / "F00_INGEST" / "CODEBASE"


def _director():
    """Importe le module caviar (Directeur) — analyse advisory éprouvée."""
    if str(_CODEBASE_F00) not in sys.path:
        sys.path.insert(0, str(_CODEBASE_F00))
    import caviar  # noqa: E402

    return caviar


def probe(path: Path) -> dict:
    """ffprobe minimal — codec, dimensions, durée, piste audio."""
    data = json.loads(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_name,codec_type,width,height:format=duration",
         "-of", "json", str(path)], text=True))
    streams = data.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    return {
        "codec": video.get("codec_name") if video else None,
        "width": int(video.get("width") or 0) if video else 0,
        "height": int(video.get("height") or 0) if video else 0,
        "duration_sec": round(float(data.get("format", {}).get("duration") or 0), 3),
        "has_audio": audio is not None,
    }


# ═══════════════════════════════════════════════════════════════════
# BUDGET D'ATTENTION — la frégate dépense AVANT d'écrire
# ═══════════════════════════════════════════════════════════════════

def compute_budget(narrative: dict, silences_count: int, duration_sec: float) -> dict:
    """Calcule la dépense du manifeste et le verdict de saturation.

    Règles de survie (note du Warsmith) :
      - dépense totale ≤ 55 u sur 100 → le reste = respiration
      - > 8 silences à trimmer → REFUS d'émettre (« segment mauvais »)
    """
    b = load_budget()["events"]
    counts = {
        "broll": len(narrative.get("broll") or []),
        "smash": len(narrative.get("is_climax") or []),
        "punchin": len(narrative.get("zooms") or []),
        "jumpcut": silences_count,
    }
    spend = (counts["broll"] * b["broll"]["cost_units"]
             + counts["smash"] * b["smash"]["cost_units"]
             + counts["punchin"] * b["punchin"]["cost_units"]
             + counts["jumpcut"] * b["jumpcut"]["cost_units"])
    verdict = {
        "total_units": load_budget()["total_budget_units"],
        "spend_units": spend,
        "breathing_units": load_budget()["total_budget_units"] - spend,
        "source_ratio_target": load_budget()["breathing"]["min_source_ratio"],
        "caps": {
            "broll": {"count": counts["broll"], "max": b["broll"]["max_per_clip"],
                      "ok": counts["broll"] <= b["broll"]["max_per_clip"]},
            "smash": {"count": counts["smash"], "max": b["smash"]["max_per_clip"],
                      "ok": counts["smash"] <= b["smash"]["max_per_clip"]},
            "punchin": {"count": counts["punchin"], "max": b["punchin"]["max_per_clip"],
                        "ok": counts["punchin"] <= b["punchin"]["max_per_clip"]},
            "jumpcut": {"count": counts["jumpcut"], "max": b["jumpcut"]["max_per_clip"],
                        "ok": counts["jumpcut"] <= b["jumpcut"]["max_per_clip"]},
        },
        "spend_ok": spend <= load_budget()["max_spend_units"],
    }
    return verdict


# ═══════════════════════════════════════════════════════════════════
# B-ROLL NUMÉROTÉ — PERTURABO donne un numéro, le bras armé connaît le fichier
# ═══════════════════════════════════════════════════════════════════

def load_registry() -> dict:
    return json.loads((HEISENBERG_ROOT / "BROLL" / "registry.json").read_text(encoding="utf-8"))


def resolve_broll_number(number: int) -> dict:
    """'met le numéro 1' → la fiche complète (fichier, flash, SFX).

    C'est la parade demandée par le Warsmith : PERTURABO n'a JAMAIS accès aux
    fichiers B-roll. Il écrit l'émotion à illustrer + le numéro ; Heisenberg
    seule fait le lien numéro → fichier (et pose flash d'entrée + SFX couplé).
    """
    reg = load_registry()
    clip = (reg.get("clips") or {}).get(str(number))
    if clip is None:
        available = ", ".join(sorted(reg.get("clips", {}).keys(), key=str)) or "aucun"
        raise KeyError(f"B-roll numéro {number} inconnu (disponibles : {available})")
    return {
        "broll_number": int(number),
        "asset_ref": f"broll#{number}",   # référence neutre — jamais le chemin brut
        "label": clip.get("label"),
        "emotions": clip.get("emotions") or [],
        "entry_flash": bool(clip.get("entry_flash", True)),
        "sfx": clip.get("sfx") or "impact",
        "duration_frames_max": clip.get("duration_frames_max", 45),
    }


def suggest_broll_by_emotion(emotion: str) -> list[int]:
    """PERTURABO décrit l'émotion → numéros candidats (il tranche ensuite)."""
    emo = (emotion or "").strip().lower()
    out: list[int] = []
    for num, clip in (load_registry().get("clips") or {}).items():
        emotions = [e.lower() for e in (clip.get("emotions") or [])]
        if emo and any(emo in e or e in emo for e in emotions):
            out.append(int(num))
    return out


def parse_broll_order(order: str) -> list[int]:
    """'met le numéro 1' / 'numeros 1 et 3' → [1] / [1, 3]."""
    return [int(n) for n in re.findall(r"\d+", order or "")]


def load_pack(path: Path | None) -> dict:
    if path is None:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def numbered_brolls_from_pack(pack: dict) -> list[dict]:
    """B-rolls Heisenberg = numéros du registre uniquement. BLUR-0x ignoré."""
    partition = pack.get("caviar_partition") or {}
    mi = pack.get("montage_instructions") or {}
    body = mi.get("body") or {}
    raw = list(partition.get("panels") or []) + list(body.get("panels") or [])
    registry = load_registry().get("clips") or {}
    files_dir = HEISENBERG_ROOT / "BROLL" / "FILES"
    out: list[dict] = []
    seen: set[tuple] = set()
    for panel in raw:
        num = None
        if panel.get("broll_number") is not None:
            try:
                num = int(panel["broll_number"])
            except (TypeError, ValueError):
                num = None
        if num is None:
            bid = str(panel.get("broll_id") or panel.get("panel_id") or "")
            m = re.search(r"^broll[#_]?(\d+)$", bid.strip(), re.I)
            if not m:
                continue
            num = int(m.group(1))
        if str(num) not in registry:
            continue
        start = float(panel.get("start_sec") or panel.get("at_sec") or 0)
        key = (num, round(start, 2))
        if key in seen:
            continue
        seen.add(key)
        clip = registry[str(num)]
        asset = files_dir / Path(clip.get("file") or f"broll_{num:02d}.mp4").name
        out.append({
            "broll_number": num,
            "asset_ref": f"broll#{num}",
            "start_sec": start,
            "duration_frames": int(panel.get("duration_frames") or clip.get("duration_frames_max") or 36),
            "entry_flash": True,
            "flash_color": "white",
            "sfx": clip.get("sfx") or "impact",
            "file_ready": asset.is_file(),
        })
    return out


def pack_punchins_ignored(pack: dict) -> list[dict]:
    """Zoom / punch-in bannis (2026-10-06) — listés puis ignorés au rendu."""
    partition = pack.get("caviar_partition") or {}
    return list(partition.get("punch_ins") or [])


def classify_silences(silences: list[dict], duration: float,
                      smash_secs: list[float] | None = None,
                      broll_windows: list[tuple[float, float]] | None = None) -> list[dict]:
    """KEEP / CUT / HOLD — short ≠ mute total."""
    smash_secs = smash_secs or []
    broll_windows = broll_windows or []
    classified: list[dict] = []
    for s in silences:
        start = float(s.get("start") or 0)
        end = float(s.get("end") or start)
        dur = float(s.get("duration_sec") or (end - start))
        row = {"start": round(start, 3), "end": round(end, 3), "duration_sec": round(dur, 3)}
        under_broll = any(start < w1 and end > w0 for w0, w1 in broll_windows)
        under_smash = any(abs(((start + end) / 2) - sm) < 1.0 for sm in smash_secs)
        in_hook = end <= HOOK_END_SEC
        in_outro = start >= max(0.0, duration - OUTRO_SEC)
        if in_hook or in_outro:
            row.update(verdict="KEEP", reason="hook_or_outro")
        elif under_broll or under_smash:
            row.update(verdict="HOLD", reason="under_smash_or_broll")
        elif dur >= SILENCE_CUT_LAG:
            row.update(verdict="CUT", reason="lag_gt_1s")
        elif dur > SILENCE_CUT_DEAD:
            row.update(verdict="CUT", reason="dead_air_gt_0.70s")
        elif dur <= SILENCE_KEEP_BREATH:
            row.update(verdict="KEEP", reason="breath_or_beat")
        else:
            row.update(verdict="HOLD", reason="dramatic_pause_candidate")
        classified.append(row)
    return classified


def jumpcut_quota(duration: float) -> int:
    return max(0, int(duration // JUMPCUT_GAP_SEC))


def select_jumpcuts(duration: float, classified: list[dict],
                    broll_windows: list[tuple[float, float]] | None = None) -> list[dict]:
    """Fenêtres IN/OUT : cut sec, déjà +20 %, gap 8 s, hors hook/outro/CUT/B-roll."""
    broll_windows = broll_windows or []
    cut_windows = [(c["start"], c["end"]) for c in classified if c.get("verdict") == "CUT"]
    usable_start = HOOK_END_SEC
    usable_end = max(usable_start, duration - OUTRO_SEC)
    quota = jumpcut_quota(duration)
    window = JUMPCUT_WINDOW_DEFAULT_SEC
    chosen: list[dict] = []
    t = usable_start
    while t + window <= usable_end and len(chosen) < quota:
        in_sec, out_sec = t, t + window
        blocked = False
        for a, b in cut_windows + broll_windows:
            if in_sec < b and out_sec > a:
                blocked = True
                t = max(t, b) + 0.05
                break
        if blocked:
            continue
        if chosen and (in_sec - chosen[-1]["in_sec"]) < JUMPCUT_GAP_SEC:
            t = chosen[-1]["in_sec"] + JUMPCUT_GAP_SEC
            continue
        chosen.append({
            "in_sec": round(in_sec, 3),
            "out_sec": round(out_sec, 3),
            "scale": JUMPCUT_SCALE,
            "kind": "jumpcut_hold",
        })
        t = in_sec + JUMPCUT_GAP_SEC
    return chosen


def _even(n: int) -> int:
    return n if n % 2 == 0 else n - 1


def _keep_intervals(duration: float, classified: list[dict]) -> list[tuple[float, float]]:
    cuts = sorted((c["start"], c["end"]) for c in classified if c.get("verdict") == "CUT")
    kept: list[tuple[float, float]] = []
    cursor = 0.0
    for a, b in cuts:
        if a > cursor:
            kept.append((cursor, a))
        cursor = max(cursor, b)
    if cursor < duration:
        kept.append((cursor, duration))
    return [(round(a, 3), round(b, 3)) for a, b in kept if b - a > 0.02]


def _segment_plan(keep: list[tuple[float, float]], jumpcuts: list[dict]) -> list[dict]:
    """Découpe les intervalles gardés en sous-segments crop/normal."""
    cuts = [(j["in_sec"], j["out_sec"]) for j in jumpcuts]
    segs: list[dict] = []
    for a, b in keep:
        points = {a, b}
        for c0, c1 in cuts:
            if c0 > a and c0 < b:
                points.add(c0)
            if c1 > a and c1 < b:
                points.add(c1)
        ordered = sorted(points)
        for x, y in zip(ordered, ordered[1:]):
            cropped = any(x >= c0 and y <= c1 for c0, c1 in cuts)
            segs.append({"start": x, "end": y, "crop": cropped})
    return segs


def render_caviar_mp4(video: Path, manifest: dict, out_mp4: Path) -> Path:
    """2e MP4 : CUT silences + jumpcuts +20 % instant. Flash blanc seulement si B-roll numéroté prêt."""
    meta = probe(video)
    w, h = _even(meta["width"] or 1080), _even(meta["height"] or 1920)
    classified = (manifest.get("silences") or {}).get("classified") or []
    jumpcuts = manifest.get("jumpcuts") or []
    keep = _keep_intervals(meta["duration_sec"] or 0, classified)
    segs = _segment_plan(keep, jumpcuts)
    if not segs:
        raise RuntimeError("aucun segment gardé — refus rendu")
    out_mp4 = Path(out_mp4)
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    cw, ch = _even(int(w / JUMPCUT_SCALE)), _even(int(h / JUMPCUT_SCALE))
    filters = []
    concats = []
    for i, seg in enumerate(segs):
        dur = seg["end"] - seg["start"]
        chain = (
            f"[0:v]trim=start={seg['start']}:duration={dur},setpts=PTS-STARTPTS"
        )
        if seg["crop"]:
            chain += f",crop={cw}:{ch}:(iw-{cw})/2:(ih-{ch})/2,scale={w}:{h}"
        chain += f"[v{i}]"
        filters.append(chain)
        filters.append(
            f"[0:a]atrim=start={seg['start']}:duration={dur},asetpts=PTS-STARTPTS[a{i}]"
        )
        concats.append(f"[v{i}][a{i}]")
    n = len(segs)
    filters.append(f"{''.join(concats)}concat=n={n}:v=1:a=1[outv][outa]")
    cmd = [
        "ffmpeg", "-y", "-i", str(video),
        "-filter_complex", ";".join(filters),
        "-map", "[outv]", "-map", "[outa]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(out_mp4),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if proc.returncode != 0 or not out_mp4.is_file() or out_mp4.stat().st_size == 0:
        raise RuntimeError(f"ffmpeg rendu échoué : {(proc.stderr or '')[-800:]}")
    return out_mp4


# ═══════════════════════════════════════════════════════════════════
# ÉMISSION DU MANIFESTE CAVIAR — PROPOSITIONS, jamais appliquées d'office
# ═══════════════════════════════════════════════════════════════════

def _proposals_from_analysis(analysis: dict, duration: float,
                             with_whisper: bool) -> dict:
    """Traduit l'analyse du Directeur en propositions Caviar (champs pack v2)."""
    budget = load_budget()
    silences = analysis.get("silences") or []

    # Jump cuts : silences trims (proposés, jamais appliqués sans validation)
    jumpcuts = [
        {"cut_at_sec": s["end"], "removes_sec": s["duration_sec"], "kind": "jump_cut"}
        for s in silences
    ]

    # Smash audio : candidats climax du Directeur (ducking -12 dB / 0.8 s par défaut)
    smash = [
        {"at_sec": c, "duck_db": -12, "duration_sec": 0.8, "kind": "smash_cut"}
        for c in (analysis.get("climax_proposals") or [])
    ]

    out = {
        "jump_cut_proposals": jumpcuts,
        "smash_audio_proposals": smash,
        "broll_proposals": [],   # rempli par l'opérateur (numéros) — jamais auto
        "flash_proposals": [],
    }

    # Flash blanc : seulement si un B-roll futur sera placé — la doctrine dit
    # ENTRÉE de B-roll uniquement ; sans B-roll demandé, zéro flash proposé.
    # (anti-saturation : flash sans changement d'état = stroboscope interdit)

    if with_whisper and (analysis.get("whisper") or {}).get("available"):
        pl = analysis["whisper"].get("punchline_proposal_sec")
        if pl is not None and 0 < pl < duration:
            out["punchline"] = {
                "at_sec": pl,
                "silence_before_punchline": True,
                "note": "0,3-0,5 s de silence total avant la chute (spec §5)",
            }
    return out


def build_caviar_manifest(video: Path, source_meta: dict | None = None,
                          with_whisper: bool = True, pack: dict | None = None) -> dict:
    """Analyse une vidéo FINIE → caviar_manifest complet (verdict + propositions)."""
    caviar = _director()
    meta = probe(video)
    pack = pack or {}
    duration = meta["duration_sec"] or float(source_meta or {}).get("duration_sec", 0) or 30.0

    # Verdict d'entrée — la vidéo doit être saine avant toute analyse
    entry_ok, entry_errors = [], []
    if meta["codec"] not in ("h264", "vp9", "hevc", "av1"):
        entry_errors.append(f"codec {meta['codec']} non lisible")
    if not meta["has_audio"]:
        entry_errors.append("pas de piste audio (porte P-AUD du bras armé)")
    if meta["width"] <= 0:
        entry_errors.append("dimensions illisibles")
    entry_ok = not entry_errors

    analysis = caviar.analyze_clip(video, duration, with_whisper=with_whisper) if entry_ok else {}
    silences_count = analysis.get("silence_count", 0)
    max_silences = load_budget()["silences"]["max_before_refusal"]

    # Refus documenté : trop de silences → « segment mauvais, prends un autre »
    if silences_count > max_silences:
        refused = (f"segment mauvais : {silences_count} silences > {max_silences} — "
                   f"{load_budget()['silences']['refusal_message']}")
        return {
            "schema_version": SCHEMA_VERSION,
            "generated_at": now(),
            "source_file": video.name,
            "probe": meta,
            "verdict": "REFUSED",
            "refusal_reason": refused,
            "budget": compute_budget({}, silences_count, duration),
            "proposals": {},
            "note": "Aucun manifeste toxique n'est émis — diagnostic renvoyé à l'opérateur.",
        }

    narrative_hint = (source_meta or {}).get("narrative") or {}
    numbered = numbered_brolls_from_pack(pack) if pack else []
    punchins_ignored = pack_punchins_ignored(pack) if pack else []
    smash_secs = [float(s.get("at_sec")) for s in (pack.get("caviar_partition") or {}).get("smash_audio") or [] if s.get("at_sec") is not None]
    broll_windows = [(b["start_sec"], b["start_sec"] + b["duration_frames"] / FLASH_FPS) for b in numbered]
    classified = classify_silences(analysis.get("silences") or [], duration, smash_secs, broll_windows) if entry_ok else []
    cut_count = sum(1 for c in classified if c.get("verdict") == "CUT")
    jumpcuts = select_jumpcuts(duration, classified, broll_windows) if entry_ok else []
    flashes = [{"at_sec": b["start_sec"], "color": "white", "frames": FLASH_FRAMES, "coupled_sfx": b["sfx"], "broll": b["asset_ref"]} for b in numbered if b.get("file_ready")]
    budget_narrative = dict(narrative_hint)
    budget_narrative["broll"] = numbered
    budget_narrative["is_climax"] = smash_secs
    budget_narrative["zooms"] = []
    budget = compute_budget(budget_narrative, cut_count + len(jumpcuts), duration)
    proposals = _proposals_from_analysis(analysis, duration, with_whisper) if entry_ok else {}
    proposals["jumpcuts"] = jumpcuts
    proposals["silence_cuts"] = [c for c in classified if c.get("verdict") == "CUT"]
    proposals["broll_proposals"] = numbered
    proposals["flash_proposals"] = flashes

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now(),
        "generator": "HEISENBERG (sous-frégate Caviar — F03_PICTOR)",
        "source_file": video.name,
        "probe": meta,
        "verdict": "OK" if entry_ok else "BLOCKED",
        "entry_gate": {"ok": entry_ok, "errors": entry_errors},
        "analysis": {
            "silence_count": silences_count,
            "speech_ratio": analysis.get("speech_ratio"),
            "climax_candidates": analysis.get("climax_proposals") or [],
            "whisper": analysis.get("whisper"),
        },
        "silences": {"classified": classified, "cut_count": cut_count},
        "jumpcuts": jumpcuts,
        "pack_ignored": {"punch_ins": punchins_ignored, "reason": "zoom_banned_2026-10-06"},
        "broll": numbered,
        "flashes": flashes,
        "budget": budget,
        "proposals": proposals,
        "doctrine": {
            "perturabo": "le OÙ/QUOI — il tranche les propositions, écrit l'accroche, choisit les numéros B-roll",
            "lacrimae": "le COMMENT — courbes, synchro, flashs, budgets, portes",
            "warsmith": "valide au gate ; toute décision créative finale lui revient",
        },
        "notes": [
            "PROPOSITIONS uniquement — rien n'est appliqué sans validation pack/manifeste + opérateur",
            "Jumpcut = cut sec +20% figé (IN/OUT), gap 8 s, jamais d'animation de zoom",
            "flash blanc à l'ENTRÉE de chaque B-roll numéroté, jamais à la sortie, jamais sur jumpcut",
            "SFX uniquement à l'entrée des B-rolls (règle Warsmith anti-saturation)",
            "pas de B-roll numéroté = 0 flash, 0 SFX — panels BLUR-0x ignorés",
            "punch_ins / zooms du pack ignorés (bannis 2026-10-06)",
        ],
    }
    return manifest


# ═══════════════════════════════════════════════════════════════════
# LEDGER — la mémoire de la frégate (confinée, ARCHIVUM-friendly)
# ═══════════════════════════════════════════════════════════════════

def ledger_write(entry: dict, kind: str = "manifest") -> None:
    """Écrit dans LEDGER/ — la frégate ne mélange jamais ses journaux."""
    ledger = HEISENBERG_ROOT / "LEDGER"
    ledger.mkdir(parents=True, exist_ok=True)
    file = ledger / ("manifest_ledger.json" if kind == "manifest" else "gate_history.json")
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        data = {"schema_version": "dev10.heisenberg-ledger.v1", "entries": []}
    data["entries"] = (data.get("entries") or [])[-499:] + [entry]
    data["updated_at"] = now()
    file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def emit(video: Path, out_dir: Path | None = None, with_whisper: bool = True,
         source_meta: dict | None = None, pack: dict | None = None,
         render: bool = False) -> dict:
    """Reçoit une vidéo finie → écrit OUT/caviar_manifest_<stem>.json + ledger (+ MP4 si --render)."""
    out_dir = out_dir or (HEISENBERG_ROOT / "OUT")
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = build_caviar_manifest(video, source_meta=source_meta, with_whisper=with_whisper, pack=pack)
    out_path = out_dir / f"caviar_manifest_{video.stem}.json"
    out_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    _log(f"  [✓] HEISENBERG : manifeste émis → {out_path}")
    ledger_write({
        "at": now(),
        "kind": "emit",
        "video": video.name,
        "verdict": manifest.get("verdict"),
        "spend_units": (manifest.get("budget") or {}).get("spend_units"),
        "out_file": out_path.name,
        "jumpcuts": len(manifest.get("jumpcuts") or []),
        "silence_cuts": (manifest.get("silences") or {}).get("cut_count"),
    }, kind="manifest")
    if manifest.get("verdict") == "REFUSED":
        hold = out_dir / "hold"
        hold.mkdir(parents=True, exist_ok=True)
        (hold / out_path.name).write_text(out_path.read_text(encoding="utf-8"), encoding="utf-8")
        _log(f"  [✗] REFUS : {manifest.get('refusal_reason')}")
    elif render and manifest.get("verdict") == "OK":
        mp4 = out_dir / f"{video.stem}_caviar.mp4"
        render_caviar_mp4(video, manifest, mp4)
        manifest["rendered_mp4"] = mp4.name
        out_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        _log(f"  [✓] HEISENBERG : MP4 caviar → {mp4}")
    return manifest


# ═══════════════════════════════════════════════════════════════════
# CHUNK PACK — la part de PERTURABO (montage_instructions additionnelles)
# ═══════════════════════════════════════════════════════════════════

def emit_pack_chunk(manifest_path: Path) -> dict:
    """Extrait la portion à embarquer dans le pack PUR (champs v2 OPTIONNELS).

    Rétrocompatibilité garantie : champs absents = comportement pack v1.
    PERTURABO relit, tranche (garde/modifie/rejette), et stampé son pack.
    """
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    proposals = m.get("proposals") or {}
    chunk = {
        "schema_version": SCHEMA_VERSION,
        "origin": "HEISENBERG",
        "note": "à intégrer dans montage_instructions du pack par PERTURABO — optionnel, v1-compatible",
        "narrative": {
            "energy_curve_hint": m.get("analysis", {}).get("climax_candidates"),
            "is_climax_proposals": m.get("analysis", {}).get("climax_candidates"),
        },
        "jump_cut_proposals": proposals.get("jump_cut_proposals") or [],
        "smash_audio_proposals": proposals.get("smash_audio_proposals") or [],
        "punchline": proposals.get("punchline"),
        "broll_available_numbers": sorted(
            int(n) for n in (load_registry().get("clips") or {}).keys()),
    }
    return chunk


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════

def main() -> int:
    p = argparse.ArgumentParser(description="HEISENBERG — sous-frégate Caviar (F03_PICTOR)")
    p.add_argument("--manifest", type=Path, default=None,
                   help="vidéo FINIE (MP4) à analyser — OUT de F03_PICTOR")
    p.add_argument("--batch", type=Path, default=None,
                   help="dossier IN/ : analyse toutes les vidéos finies")
    p.add_argument("--out", type=Path, default=None, help="dossier OUT (défaut HEISENBERG/OUT)")
    p.add_argument("--no-whisper", action="store_true", help="désactive l'analyse CPU optionnelle")
    p.add_argument("--emit-pack-chunk", type=Path, default=None, metavar="MANIFEST_JSON",
                   help="extrait le chunk à embarquer dans le pack PERTURABO")
    p.add_argument("--broll", type=str, default=None, metavar="'met le numéro 1'",
                   help="résout un ordre B-roll numéroté (démo du contrat bras armé)")
    p.add_argument("--broll-emotion", type=str, default=None, metavar="moqueur",
                   help="propose des numéros B-roll par émotion (PERTURABO tranche)")
    p.add_argument("--pack", type=Path, default=None, help="production_pack JSON (lecture caviar_partition)")
    p.add_argument("--render", action="store_true", help="écrit le 2e MP4 caviar (jumpcuts + CUT silences)")
    args = p.parse_args()

    _log(f"\n═══ HEISENBERG — sous-frégate Caviar — {now()} ═══")
    _log("  'I am the one who knocks.' — analyse, budgets, propositions ; jamais de décision créative.")

    if args.broll:
        nums = parse_broll_order(args.broll)
        for n in nums:
            _log(f"  B-roll {n} → {json.dumps(resolve_broll_number(n), ensure_ascii=False)}")
        return 0
    if args.broll_emotion:
        _log(f"  Émotion « {args.broll_emotion} » → numéros candidats : {suggest_broll_by_emotion(args.broll_emotion)}")
        return 0
    if args.emit_pack_chunk:
        chunk = emit_pack_chunk(args.emit_pack_chunk)
        out = args.emit_pack_chunk.with_name(args.emit_pack_chunk.stem + "_pack_chunk.json")
        out.write_text(json.dumps(chunk, indent=2, ensure_ascii=False), encoding="utf-8")
        _log(f"  [✓] chunk PERTURABO émis → {out}")
        return 0

    videos: list[Path] = []
    if args.manifest:
        videos = [args.manifest]
    elif args.batch:
        videos = sorted(p for p in args.batch.iterdir()
                        if p.suffix.lower() in (".mp4", ".mov", ".mkv", ".webm"))
    else:
        p.print_help()
        return 1

    pack = load_pack(args.pack) if args.pack else {}
    ok = True
    for v in videos:
        _log(f"\n── {v.name}")
        try:
            m = emit(v, out_dir=args.out, with_whisper=not args.no_whisper,
                     pack=pack, render=args.render)
            if args.render:
                ok = ok and m.get("verdict") == "OK" and bool(m.get("rendered_mp4"))
            else:
                ok = ok and m.get("verdict") in ("OK", "REFUSED")
        except Exception as exc:
            _log(f"  [✗] échec : {exc}")
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Tests de la couche Caviar : porte P-CAV (budgets bloquants) + Directeur."""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "CODEBASE"))
import caviar  # noqa: E402

FAILS = []


def check(cond, label):
    print(("  [✓] " if cond else "  [✗] ") + label)
    if not cond:
        FAILS.append(label)


def base_pack(**mi_extra):
    mi = {"mode": "pur", "segment": {"source_url": "x", "start_sec": 0, "end_sec": 30}}
    mi.update(mi_extra)
    return {"pack_id": "test", "montage_instructions": mi}


def zoom(frame, flash=False):
    return {"moment_frame": frame, "scale_from": 1.0, "scale_to": 1.15,
            "frames": 3, **({"white_flash": True} if flash else {})}


def broll(start, frames=36, sfx="impact"):
    return {"asset_file": "broll/x.png", "start_sec": start,
            "duration_frames": frames, "sfx": sfx, "entry_flash": True}


print("═ P-CAV : bypass pack v1 (aucun champ narratif) ═")
ok, errs = caviar.gate_pcav_budgets(base_pack())
check(ok and not errs, "pack v1 passe sans erreur")
check(not caviar.has_caviar_fields(base_pack()), "has_caviar_fields=False pour pack v1")

print("═ P-CAV : pack narratif valide ═")
ok, errs = caviar.gate_pcav_budgets(base_pack(
    narrative={"hook_type": "reframe", "is_climax": [14.2], "resolution_at": 24.0,
               "energy_curve": ["rise", "peak", "fall"]},
    zooms=[zoom(430, flash=True)],
    sfx_list=[{"type": "impact", "moment_frame": 430}],
    broll=[broll(8.5)],
    audio_design={"duck_at_climax": {"db": -12, "duration_sec": 0.8},
                  "silence_before_punchline": True},
))
check(ok, f"pack narratif valide accepté (errs={errs})")

print("═ P-CAV : budgets bloquants ═")
ok, _ = caviar.gate_pcav_budgets(base_pack(broll=[broll(5), broll(10), broll(15), broll(20)]))
check(not ok, "4 brolls → rouge (budget 3)")
ok, _ = caviar.gate_pcav_budgets(base_pack(broll=[broll(5, frames=46)]))
check(not ok, "broll 46 frames → rouge (budget 45)")
ok, _ = caviar.gate_pcav_budgets(base_pack(broll=[{"asset_file": "x", "start_sec": 5, "duration_frames": 30}]))
check(not ok, "broll sans sfx → rouge")
ok, _ = caviar.gate_pcav_budgets(base_pack(narrative={"resolution_at": 20.0}, broll=[broll(25)]))
check(not ok, "broll pendant la résolution → rouge")
ok, _ = caviar.gate_pcav_budgets(base_pack(zooms=[zoom(30, flash=True), zoom(90, flash=True), zoom(150, flash=True), zoom(210, flash=True)]))
check(not ok, "4 flashs → rouge (budget 3)")
ok, _ = caviar.gate_pcav_budgets(base_pack(zooms=[zoom(30, flash=True), zoom(60, flash=True)]))
check(not ok, "flashs à 1s d'écart → rouge (min 1.5s)")
ok, _ = caviar.gate_pcav_budgets(base_pack(zooms=[zoom(30), zoom(60)]))
check(not ok, "zooms à 1s d'écart → rouge (min 2s)")
ok, _ = caviar.gate_pcav_budgets(base_pack(zooms=[zoom(30), zoom(150), zoom(300), zoom(450), zoom(600)]))
check(not ok, "5 zooms → rouge (budget 4)")
ok, _ = caviar.gate_pcav_budgets(base_pack(zooms=[zoom(300)], broll=[broll(10.0)]))
check(not ok, "zoom + broll à la même seconde → rouge (élément unique)")
ok, _ = caviar.gate_pcav_budgets(base_pack(zooms=[zoom(300, flash=True)], sfx_list=[]))
check(not ok, "white_flash sans SFX même frame → rouge")
ok, _ = caviar.gate_pcav_budgets(base_pack(zooms=[zoom(300, flash=True)], sfx_list=[{"type": "impact", "moment_frame": 301}]))
check(ok, "white_flash avec SFX à ±1 frame → passe (tolérance 50 ms)")
ok, _ = caviar.gate_pcav_budgets(base_pack(zooms=[zoom(300, flash=True)], sfx_list=[{"type": "impact", "moment_frame": 302}]))
check(not ok, "white_flash avec SFX à ±2 frames → rouge (frame exacte exigée)")

print("═ P-CAV : schéma (valeurs invalides refusées) ═")
ok, _ = caviar.gate_pcav_budgets(base_pack(narrative={"hook_type": "nimporte"}))
check(not ok, "hook_type invalide → rouge")
ok, _ = caviar.gate_pcav_budgets(base_pack(narrative={"energy_curve": ["boom"]}))
check(not ok, "energy_curve invalide → rouge")
ok, _ = caviar.gate_pcav_budgets(base_pack(narrative={"is_climax": [45.0]}), expected_duration=30.0)
check(not ok, "is_climax hors segment → rouge")
ok, _ = caviar.gate_pcav_budgets(base_pack(audio_design={"duck_at_climax": {"db": 3}}))
check(not ok, "ducking dB > 0 → rouge")

print("═ Directeur : clusters RMS (synthétique) ═")
series = [(i * 0.05, -20.0 if 10 < i < 14 else -35.0) for i in range(200)]
clusters = caviar._peak_clusters(series, max_clusters=3)
check(len(clusters) == 1 and 0.5 <= clusters[0]["peak_sec"] <= 0.75,
      f"1 cluster détecté au bon endroit ({clusters})")
check(caviar._peak_clusters([]) == [], "série vide → aucun cluster")

print("═ Directeur : silences (intégration ffmpeg, si disponible) ═")
try:
    tmp = Path("/tmp/caviar_test_tone.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
                    "sine=frequency=440:duration=2", "-f", "lavfi", "-i",
                    "anullsrc=r=44100:cl=mono:d=0.6", "-f", "lavfi", "-i",
                    "sine=frequency=440:duration=2",
                    "-filter_complex", "[0][1][2]concat=n=3:v=0:a=1", str(tmp)],
                   check=True, capture_output=True, timeout=60)
    sil = caviar._detect_silences(tmp)
    check(len(sil) >= 1 and 0.4 <= sil[0]["duration_sec"] <= 0.8,
          f"silence central détecté ({sil})")
    tmp.unlink(missing_ok=True)
except FileNotFoundError:
    print("  [·] ffmpeg absent — test intégration sauté")

print()
if FAILS:
    print(f"═══ ÉCHEC : {len(FAILS)} test(s) ═══")
    sys.exit(1)
print("═══ TOUS LES TESTS CAVIAR PASSENT ═══")

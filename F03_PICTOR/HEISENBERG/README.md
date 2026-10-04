## Groupe 3 v2 — punch-ins réels + trims géants + budget_state absent (2026-10-04)

Les packs réels `asf_c1→c5` (branche PERTURABO `v2-live-vox-c`, style blur)
valident le moteur sur des données terrain battues :

- **Punch-ins (v2)** : `{ at_sec, scale:1.2, duration_sec:0.6, cause:amplitude_peak }`
  — l'adaptateur lit `scale` (=1.2, plafonné à 1.15 au moteur) et transporte
  `duration_sec` + `cause` dans le bloc v1 ; le moteur DERIVE la courbe
  attack/hold/release depuis la durée (1/6, 2/6, reste) quand aucune frame
  explicite n'est fournie → 0.6 s @ 30 fps = 3f/6f/9f (défauts).
- **Trims géants (v2)** : `silence_trims = { start_sec, end_sec, duration_sec }`
  fenêtre `[start, end)` → `cut_at_sec = end` (reprise DU CONTENU, pas début du
  silence). c1 : trim d'intro `[0, 9.994]` → la timeline recommence à 9.994 s
  (segment sourceStart = 300 @ 30 fps), le pack n'a de son que depuis ce point.
  Fix moteur : une tuile de longueur nulle (cutStart == srcSec, ex. trim collé à 0
  ou deux trims adjacents) ne SAUTE PAS l'update `srcSec = cut_at_sec`, sinon le
  silence suivant est réintégré dans la tuile suivante — aggravé sur les trims
  adjacents (c3 : [16.999→18.32] + [18.32→22.345] fusionnent → 8 tuiles, pas 9).
  Fix adaptateur : `removes_sec` arrondi au millième (évite flottant 0,4510000000000005).
- **budget_state ABSENT** des 5 packs asf — le recalcul côté gate + moteur :
  c1=52, c2=54, c3=46, c4=50, c5=55 (tous ≤ 55u, caps ok, spacing punch ≥ 2 s).
  Silence trim < 0.25s ignorés (règle moteur), frames c1 : 75 (smash),
  150 (BLUR-01 aftertrim), 219/321 (punch-ins survécu), 587 (BLUR-02).

Fixture : les 5 packs réels `pack_asf_c1..5.json` déposés dans
`F03_PICTOR/CODEBASE/tests/` (copie lecture-seule depuis /tmp/pert2).
Tests : `caviar_v2.test.mjs` — 16/16 (mapping punch+trims, timeline c1
trims géants, 5 packs budget+timeline, c3 tuiles fusionnées).
Gate CLI : `caviar_gate.py --manifest manifest_asf_c1.json --pack-v2 pack_asf_c1.json
--manifest-caviar manifest_asf_c1.json` → avertissement budget_state absent +
portes v2 OK, checksum16 interne == binding (`e567d4ad00e06ab1`).

**Portée actuelle** : les packs asf (mode pur, bloc caviar v2) CI :
✅ voir gate ✅ (punch-ins réels cap 4, espacés ≥ 2 s).
**Hors scope pour l'instant (décision à confirmer)** : les 3 meme_* packs
(mode logo/text+punch via schéma meme_v2, `overlay_image` json, 2 silences
dans chacune) — schéma DIFFERENT, signification de `scale_to`, résolution du
manifeste F00D. Ne pas les confondre avec les packs asf (schéma caviar v2).

## Ce que Heisenberg NE fait PAS

# F03_PICTOR

Rendu LOOK. Remotion. Miroir exact de F03_PREVIEW (`_purPackComposition.jsx`).
Sort un MP4 compose : style + overlay + anti-detection (miroir / speed / crop).
Timeline encore plate — le TEMPS est Heisenberg.

## Contrats

| | Chemin |
|--|--------|
| IN | manifeste valide + clips F00_PUR |
| OUT | `OUT/pur_<angle>_look.mp4` |
| Code | `CODEBASE/` (Remotion) |

```bash
cd F03_PICTOR/CODEBASE
npm ci || npm install
node render_pictor.mjs \
  --manifest ../../BRIDGE_PERTURABO/OUT/pur_manifest.json \
  --clips ../../F00_PUR/OUT \
  --out ../../F03_PICTOR/OUT
```

`--entry N` pour un asset. `--dry-run` verifie G0-S / P-ZOOM ZERO sans Remotion.

## Interdits

- Zoom, swell, scale anime, breathing_zoom
- Jump cuts, SFX, B-roll, flash (c'est F04)
- Ranking

`reframing` = recadrage **fixe** (echelle / offset), pas une animation.

Porte P2 LOOK + P-ZOOM ZERO. Voir `TRACKING/PUR_GATES.md`.

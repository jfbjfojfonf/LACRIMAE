# F03_PREVIEW

Validation visuelle (porte P1). Vite + player. Trois styles uniquement :
`blur`, `split_scene`, `reframing`. Overlay 1–3 lignes, statique debut → fin.

## Contrats

| | Chemin |
|--|--------|
| IN | `pur_manifest.json` + clips F00_PUR |
| OUT | manifeste valide par l'operateur |
| Code | `CODEBASE/` (Vite + Remotion player) |

## Interdits

- Zoom, swell, breathing_zoom
- Ranking
- Modification du pack PERTURABO

Le moteur LOOK de la preview est le meme que F03_PICTOR (parite par
construction). Rendu CI interdit sans P1.

Voir `TRACKING/GUIDE_BRAS_ARME_PUR.md` etape 3.

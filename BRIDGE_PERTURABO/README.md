# BRIDGE_PERTURABO

Pont entre le monde forge et LACRIMAE. Recupere le pack PUR, valide G0,
convertit en manifeste `dev10.pur.v1`. Ne telecharge pas la video.

## Contrats

| | Chemin |
|--|--------|
| IN | `IN/production_pack_pur_*.json` (ou fetch distant PERTURABO EXPORT) |
| OUT | `OUT/pur_manifest.json` |
| Code | `CODEBASE/lac_bridge_forge.py` |

## Role

- Fetch du pack depuis `PERTURABO/MONDES_FORGES/CLIPPING/EXPORT/`
- Gate G0 PACK + G0-S STYLE (`blur` / `split_scene` / `reframing`)
- Conversion → `pur_manifest.json` transite vers F03_PREVIEW et F03_PICTOR
- Le pack n'est jamais reecrit

Style infere = refus. Ranking refuse.

Voir `TRACKING/PUR_GATES.md` et `TRACKING/GUIDE_BRAS_ARME_PUR.md`.

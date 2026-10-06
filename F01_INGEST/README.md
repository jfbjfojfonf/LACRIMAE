# F01_INGEST

Recupere les videos, valide 1920x1080, emet le manifeste pour F02_RENDER.

## Contrats

| | Chemin |
|--|--------|
| IN | `IN/` (sources, jamais commite) |
| OUT | `OUT/manifest.json` + copies inbox |
| Code | `CODEBASE/ingest.py` |

Champs manifeste : `id`, `video_path`. Pile : Modal + Actions (P3).
Pas de LUT, pas d'encodage.

# F02_RENDER

Applique un `.cube` (FFmpeg `lut3d`) sur chaque item du manifeste F01.
Le nom de fregate reste `F02_RENDER`.

## Contrats

| | Chemin |
|--|--------|
| IN | manifeste F01 + `SHARED/IN/*.cube` |
| OUT | `OUT/<id>.mp4` |
| Code | `CODEBASE/lut.py` (P2), `CODEBASE/modal_app.py` (P3) |

Un item = un job. CPU, pas GPU. Pas de Nexrender.

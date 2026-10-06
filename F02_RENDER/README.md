# F02_RENDER

Applique un `.cube` (FFmpeg `lut3d`) sur chaque item du manifeste F01.
Le nom de fregate reste `F02_RENDER`.

## Contrats

| | Chemin |
|--|--------|
| IN | manifeste F01 + `SHARED/IN/*.cube` |
| OUT | `OUT/<id>.mp4` |
| Code | `CODEBASE/lut.py` |
| Tests | `tests/test_lut.py` |

```
python3 F02_RENDER/CODEBASE/lut.py \
  --manifest F01_INGEST/OUT/manifest.json \
  --lut SHARED/IN/look.cube \
  --outbox F02_RENDER/OUT \
  --dry-run
```

G0 : `.cube` obligatoire. Un item = un job. CPU, pas GPU.
P3 : `CODEBASE/modal_app.py` (pas encore).

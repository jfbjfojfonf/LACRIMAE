# F01_INGEST

Recupere les videos, valide 1920x1080 ou 1080x1920, emet le manifeste pour F02_RENDER.

## Contrats

| | Chemin |
|--|--------|
| IN | `IN/` (sources, jamais commite) |
| OUT | `OUT/manifest.json` + copies inbox |
| Code | `CODEBASE/ingest.py` |
| Tests | `tests/test_ingest.py` |

```
python3 F01_INGEST/CODEBASE/ingest.py --source F01_INGEST/IN --inbox F01_INGEST/OUT --queue F01_INGEST/OUT
```

Champs manifeste : `id`, `video_path`. Schema : `SHARED/contract/f01_f02.schema.json`.
Pas de LUT, pas d'encodage.

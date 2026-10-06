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

## Modal (P3)

App : `lacrimae-dev6f-lut`. Volume : `lacrimae-dev6f`.

| Volume | Chemin |
|--|--|
| LUT | `/data/lut/Cinematic.cube` |
| Inbox mp4 | `/data/inbox/` |
| Outbox | `/data/outbox/` |

```
modal deploy F02_RENDER/CODEBASE/modal_app.py
modal run F02_RENDER/CODEBASE/modal_app.py --dry-run
```

Apres LUT : F05 `--batch` puis F06 `--batch` (scripts verbatim `dev10-v2`).
Livrable volume : `/data/f06/*.mp4`.

Secrets GitHub : `MODAL_TOKEN_ID`, `MODAL_TOKEN_SECRET`.
Workflow : `.github/workflows/dev6f_lut_render.yml` (`workflow_dispatch`).

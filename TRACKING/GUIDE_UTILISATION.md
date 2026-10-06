# Guide d'utilisation — LACRIMAE dev6-F

LUT batch. Deux fregates. Pile Modal + Actions (P3).

## Vocabulaire

- **asset** : 1 mp4 source = 1 job F02
- **LUT** : un fichier `.cube` dans `SHARED/IN/`
- **LOOK** : F02_RENDER via `ffmpeg -vf lut3d`
- **livrable** : F05 puis F06 (P4)

## Local (P2, sans Modal)

```
python3 F01_INGEST/CODEBASE/ingest.py \
  --source /chemin/sources \
  --inbox F01_INGEST/OUT \
  --queue F01_INGEST/OUT

python3 F02_RENDER/CODEBASE/lut.py \
  --manifest F01_INGEST/OUT/manifest.json \
  --lut SHARED/IN/look.cube \
  --outbox F02_RENDER/OUT \
  --dry-run
```

Tests :

```
python3 -m unittest F01_INGEST.tests.test_ingest F02_RENDER.tests.test_lut -v
```

## CI / Modal (P3, pas encore)

Workflow prevu : `.github/workflows/dev6f_lut_render.yml`
Secret : `MODAL_TOKEN`. Humain fournit le `.cube`.

## Fichiers jamais commites

`.cube`, mp4, `IN/` `OUT/` runtime, tokens.

## En cas de probleme

| Symptome | Cause | Action |
|---|---|---|
| SKIP resolution | pas 1920x1080 | conformer la source |
| lut3d fail | `.cube` absent / casse | G0 |
| Modal 401 | pas de `MODAL_TOKEN` | P3 humain |

# HANDOFF — `dev6-E`

## Où on en est

Phases 0 → 1c **faites et pushées**.
Prochain palier : **humain** (`ROADMAP_HUMAIN.md`). Pas de code tant que le VPS n'a pas un log d'erreur.

## Repo

| Chemin | Role |
|---|---|
| `ROADMAP_HUMAIN.md` | Feuille de route VPS pour l'humain |
| `pipeline.py` | F01 puis F02 |
| `NEXRENDER/vps/*.ps1` | bootstrap, start-nexrender, run-pipeline |
| `NEXRENDER/paths.json` | Chemins VPS |
| `NEXRENDER/jobs/job.reference.json` | Job (AE 2023+ outputModule) |
| `NEXRENDER/scripts/apply_cc2.jsx` | Preset a la volee |
| `F01_INGEST/ingest.py` | Scan / valide / inbox / manifeste |
| `F02_RENDER/render.py` | POST `/api/v1/jobs` + poll |
| `tests/` | 10 tests sans VPS |

## Decisions figées

Calque `SRC`, comp `MAIN`, mp4 H.264, un job / video, plugin manquant = fail.
API : `http://127.0.0.1:3000/api/v1/jobs`, header `nexrender-secret` (env `NEXRENDER_SECRET`).
Pas de Polyester / OpenCV / F09. Pas de `*.ffx` `*.aep` `*.mp4` dans Git.

## Tests

```
python3 -m unittest tests.test_ingest tests.test_render tests.test_pipeline -v
```

## Si un agent reprend

1. Lire `CONTINUATION.md` puis ce fichier puis `ROADMAP_HUMAIN.md`.
2. Ne coder que sur un bug Phase 4 (log nexrender/aerender fourni) ou Phase 5 demandee.
3. Ne pas modifier `dev6`, `dev6-D`, `f09-output`, `main`.
4. Ne jamais committer token / preset / aep / mp4.

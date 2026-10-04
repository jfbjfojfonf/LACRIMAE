# HANDOFF — `dev6-E`

## Où on en est

Phase 0 (structure/docs) et Phase 1a (artefacts Nexrender) sont **faites et pushées**.
Phase 1b (code F01/F02) est **le prochain palier**.

## Ce qui est dans le repo

| Chemin | Rôle |
|---|---|
| `NEXRENDER/paths.json` | Chemins VPS + conventions figées |
| `NEXRENDER/jobs/job.reference.json` | Job Nexrender de référence |
| `NEXRENDER/scripts/apply_cc2.jsx` | Applique `cc2.ffx` sur le calque `SRC` |
| `NEXRENDER/contract/` | Schema + exemple manifeste F01→F02 |
| `F01_INGEST/README.md` | Spec ingest (pas encore de code) |
| `F02_RENDER/README.md` | Spec render (pas encore de code) |

## Décisions figées — ne pas rouvrir

- Calque : `SRC`
- Comp : `MAIN`
- Sortie : mp4 H.264
- Un job par vidéo
- Plugin manquant = fail
- Pas de Polyester / OpenCV / F09 sur cette branche
- `*.ffx` `*.aep` `*.mp4` jamais committés

## Prochain palier (Phase 1b)

1. Code `F01_INGEST` : lire un dossier source, valider 1920x1080, copier vers inbox, écrire `manifest.json`.
2. Code `F02_RENDER` : lire manifeste, cloner `job.reference.json` par item, POST au nexrender-server, suivre, copier outbox.
3. Tests unitaires locaux (sans VPS, filesystem mock).
4. Commit + push + maj `CONTINUATION.md` avant de passer à autre chose.

## Ce que l'humain doit faire (pas l'agent)

Phases 2-3-4 : installer Node/Nexrender/AE/plugins sur le VPS Kamatera, créer le `.aep` en RDP.

## Interdits

- Ne pas committer de token, `.env`, preset, projet AE, vidéo.
- Ne pas modifier `dev6`, `dev6-D`, `f09-output`, `main`.

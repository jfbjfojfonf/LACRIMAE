# CONTINUATION — branche `dev6-E`

## Objet de la branche

Flux **« vidéos existantes → Nexrender → preset `cc2.ffx` → vidéo finie »**.

- **Pas de Polyester**, pas de pipeline OpenCV, pas de preview F09 : tout ça reste sur `f09-output` / `dev6-D`.
- **Deux frégates seulement** : `F01_INGEST`, `F02_RENDER`.
- **After Effects ne tourne jamais sur le PC local** : tout se passe sur le VPS Kamatera.

## Règles de branche

1. Ne jamais modifier `dev6` (stable), `dev6-D`, `f09-output` ni `main`.
2. Jamais committé : `.env*`, tokens, `*.ffx`, `*.aep`, `*.mp4`, `node_modules/`.
3. Préservation absolue de tout changement utilisateur existant ; pas de reset/clean/squash.
4. Push uniquement quand demandé.

## Flux cible

```
[vidéos déjà créées]
        │
        ▼
 F01_INGEST  ─ récupère, valide, dépose en file d'attente
        │
        ▼
 F02_RENDER  ─ job Nexrender → VPS → aerender + cc2.ffx
        │
        ▼
[vidéos finies, colorées]
```

## TODO

### ✅ Phase 0 — Structure
### ✅ Phase 1a — Artefacts Nexrender
### ✅ Phase 1b — Code F01 / F02 + tests
### ✅ Phase 1c — API Nexrender réelle + scripts VPS + feuille de route (2026-10-04)
- [x] POST/GET `/api/v1/jobs` + header `nexrender-secret`
- [x] Job AE 2023+ (`outputModule`, `outputExt`, `useOriginal`)
- [x] `pipeline.py` (F01 puis F02)
- [x] Scripts PowerShell `NEXRENDER/vps/`
- [x] `ROADMAP_HUMAIN.md`

### ⬜ Phase 2 — VPS (**toi**, `ROADMAP_HUMAIN.md` etapes 1-6)
### ⬜ Phase 3 — Template `.aep` (**toi**, etape 7)
### ⬜ Phase 4 — Premier rendu (**toi** + agent depannage, etapes 8-9)
### ⬜ Phase 5 — Automatisation (optionnelle)

## Décisions figées

| Question | Décision |
|---|---|
| Calque | `SRC` |
| Comp | `MAIN` |
| Sortie | mp4 H.264 |
| Jobs | un par video |
| Plugin manquant | fail |
| API | `/api/v1/jobs` + `nexrender-secret` |
| Source F01 | `C:\nexrender\sources` |

## Handoff agent

Code pret. Attendre que l'humain fasse `ROADMAP_HUMAIN.md`.
Ensuite Phase 4 : depanner le premier rendu reel.
Ne pas coder tant qu'il n'y a pas un log d'erreur VPS.

## Tests

```
python3 -m unittest tests.test_ingest tests.test_render tests.test_pipeline -v
```

## État Git

- Branche : `dev6-E`
- Dernier palier : Phase 1c API + scripts VPS + roadmap humain

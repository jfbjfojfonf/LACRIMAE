# HANDOFF — `dev6-E`

## Où on en est

Phases 0, 1a et 1b sont **faites et pushées**.
Prochain palier **humain** : Phase 2 (install VPS). Rien à coder tant que le VPS n'est pas prêt.

## Ce qui est dans le repo

| Chemin | Rôle |
|---|---|
| `NEXRENDER/paths.json` | Chemins VPS + conventions figées |
| `NEXRENDER/jobs/job.reference.json` | Job Nexrender de référence |
| `NEXRENDER/scripts/apply_cc2.jsx` | Applique `cc2.ffx` sur le calque `SRC` |
| `NEXRENDER/contract/` | Schema + exemple manifeste F01→F02 |
| `F01_INGEST/ingest.py` | Scan / valide / copie inbox / manifeste |
| `F02_RENDER/render.py` | Manifeste → jobs → POST server → poll |
| `tests/test_ingest.py` | Tests F01 (probe mocké, pas besoin de ffprobe) |
| `tests/test_render.py` | Tests F02 (HTTP mocké, dry-run) |

## Décisions figées — ne pas rouvrir

- Calque : `SRC`
- Comp : `MAIN`
- Sortie : mp4 H.264
- Un job par vidéo
- Plugin manquant = fail
- Pas de Polyester / OpenCV / F09 sur cette branche
- `*.ffx` `*.aep` `*.mp4` jamais committés

## Comment relancer les tests

```
python3 -m unittest tests.test_ingest tests.test_render -v
```

Doit afficher 8/8 OK.

## Usage prévu sur le VPS (Phase 4)

```
python F01_INGEST/ingest.py
python F02_RENDER/render.py --dry-run
python F02_RENDER/render.py
```

F01 exige `ffprobe` dans le PATH. F02 exige `nexrender-server` sur `http://127.0.0.1:3000`.

## Ce que l'humain doit faire (pas l'agent)

1. Phase 2 : Node LTS, Nexrender server+worker, AE officiel, plugins MBL + Sapphire.
2. Copier `NEXRENDER/scripts/apply_cc2.jsx` → `C:\nexrender\scripts\apply_cc2.jsx`.
3. Copier `cc2.ffx` → `C:\nexrender\presets\cc2.ffx` (fichier privé, hors repo).
4. Phase 3 : créer `template.aep` (comp `MAIN`, calque `SRC`, Output Module H.264).
5. Phase 4 : une vidéo test dans `C:\nexrender\sources`, lancer F01 puis F02.

## Si un agent reprend le code

- Lire `CONTINUATION.md` puis ce fichier.
- Ne coder que si Phase 4 a un bug reproductible, ou si Phase 5 (workflow GH) est demandée.
- Ne pas modifier `dev6`, `dev6-D`, `f09-output`, `main`.

## Interdits

- Ne pas committer de token, `.env`, preset, projet AE, vidéo.

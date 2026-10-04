# CONTINUATION — branche `dev6-E`

## Objet de la branche

Flux **« vidéos existantes → Nexrender → preset `cc2.ffx` → vidéo finie »**.

- **Pas de Polyester**, pas de pipeline OpenCV, pas de preview F09 : tout ça reste sur `f09-output` / `dev6-D`.
- **Deux frégates seulement** (convention de nommage LACRIMAE `F0X_NOM`) :
  - `F01_INGEST` — celle qui **récupère les vidéos**
  - `F02_RENDER` — celle qui **les travaille** via Nexrender, et basta
- **After Effects ne tourne jamais sur le PC local** (trop faible) : tout se passe sur le VPS Kamatera.

## Règles de branche

1. Ne jamais modifier `dev6` (stable), `dev6-D`, `f09-output` ni `main`.
2. Jamais committé : `.env*`, tokens, `*.ffx`, `*.aep`, `*.mp4`, `node_modules/`.
3. Préservation absolue de tout changement utilisateur existant ; pas de reset/clean/squash.
4. Push uniquement quand demandé.

## Flux cible

```
[vidéos déjà créées, autre branche/stockage]
        │
        ▼
 F01_INGEST  ─ récupère, valide, dépose en file d'attente
        │
        ▼
 F02_RENDER  ─ construit le job Nexrender → VPS → aerender + cc2.ffx
        │
        ▼
[vidéos finies, colorées avec le preset AE]
```

## TODO — plan d'implémentation

### ✅ Phase 0 — Structure (Fait)
- [x] Branche `dev6-E` créée depuis `main`
- [x] Structure : `NEXRENDER/`, `F01_INGEST/`, `F02_RENDER/`
- [x] Documentation de branche
- [x] `.gitignore` de sécurité

### ✅ Phase 1a — Artefacts Nexrender (Fait, 2026-10-04)
- [x] JSON de job de référence (`NEXRENDER/jobs/job.reference.json`)
- [x] Script JSX appliquant `cc2.ffx` (`NEXRENDER/scripts/apply_cc2.jsx`)
- [x] Contrat F01 → F02 (`NEXRENDER/contract/`)
- [x] Chemins VPS figés (`NEXRENDER/paths.json`)

### ✅ Phase 1b — Code des frégates (Fait, 2026-10-04)
- [x] `F01_INGEST/ingest.py` : scan source, validation 1920x1080, copie inbox, manifeste
- [x] `F02_RENDER/render.py` : manifeste → jobs, POST nexrender-server, suivi, outbox
- [x] Tests unitaires sans VPS (`tests/test_ingest.py`, `tests/test_render.py`) — 8/8 OK

### ⬜ Phase 2 — VPS (**toi**, voir `NEXRENDER/docs/01_VPS_SETUP.md`)
- [ ] Node.js LTS installé sur le VPS
- [ ] Nexrender installé (`@nexrender/cli`, server + worker)
- [ ] After Effects officiel installé + mode Render Only
- [ ] Plugins du preset (Magic Bullet Looks, Sapphire) installés
- [ ] Règle on/off du VPS maîtrisée (crédit essai 100 $ / 30 jours)
- [ ] Copier `apply_cc2.jsx` vers `C:\nexrender\scripts\`
- [ ] Copier `cc2.ffx` vers `C:\nexrender\presets\` (jamais dans le repo)

### ⬜ Phase 3 — Template `.aep` sur le VPS (**toi**, voir `02_TEMPLATE_AEP.md`)
- [ ] Composition 1920×1080 créée via RDP, nommée `MAIN`
- [ ] Calque vidéo placeholder nommé `SRC`
- [ ] Output module configuré (obligatoire AE 2023+)
- [ ] `.aep` enregistré dans `C:\nexrender\templates\template.aep` (jamais committé)

### ⬜ Phase 4 — Premier rendu de test (**toi** + moi : dépannage)
- [ ] 1 vidéo test déposée dans `C:\nexrender\sources`
- [ ] `python F01_INGEST/ingest.py` puis `python F02_RENDER/render.py`
- [ ] Rendu réussi (pas de pop-up, pas de watermark, look cc2 correct)

### ⬜ Phase 5 — Automatisation (optionnelle)
- [ ] Self-hosted runner GitHub installé sur le VPS (**toi**)
- [ ] Workflow `.github/workflows/` (**moi**)

## Décisions figées

| Question | Décision |
|---|---|
| Nom du calque placeholder | `SRC` |
| Nom de la composition | `MAIN` |
| Format de sortie | mp4 H.264 |
| Politique jobs | un job par vidéo |
| Plugin manquant | échec du job |
| Chemin preset | `C:\nexrender\presets\cc2.ffx` |
| Source F01 par défaut | `C:\nexrender\sources` |

## Handoff agent

Prochaine action **côté code** : rien de bloquant. Attendre Phase 2-3 (humain, VPS).
Ensuite Phase 4 : lancer un job réel, dépanner via `NEXRENDER/docs/05_DEPANNAGE.md`.

Voir `HANDOFF.md`.

## Commandes locales (sans VPS)

```
python3 -m unittest tests.test_ingest tests.test_render -v
python3 F02_RENDER/render.py --dry-run --manifest /chemin/manifest.json --jobs-dir /tmp/jobs --outbox /tmp/outbox
```

## État Git

- Branche courante : `dev6-E`
- Dernier palier : Phase 1b code F01/F02 + tests

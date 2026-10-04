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
3. **Pas de code avant validation humaine de la phase concernée** (voir TODO).
4. Préservation absolue de tout changement utilisateur existant ; pas de reset/clean/squash.
5. Push uniquement quand demandé — via `push_via_api.py` (le credential Freebuff n'a pas accès au repo).

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
- [x] Documentation de branche (8 docs, cf. `NEXRENDER/README.md`)
- [x] `.gitignore` de sécurité

### ⬜ Phase 1 — Artefacts Nexrender dans le repo (**moi**, code à valider)
- [ ] JSON de job de référence (`NEXRENDER/jobs/`)
- [ ] Script JSX appliquant `cc2.ffx` à la volée (`NEXRENDER/scripts/`)
- [ ] Contrat d'interface F01_INGEST → F02_RENDER
- **Validation utilisateur requise avant d'écrire le code.**

### ⬜ Phase 2 — VPS (**toi**, voir `NEXRENDER/docs/01_VPS_SETUP.md`)
- [ ] Node.js LTS installé sur le VPS
- [ ] Nexrender installé (`@nexrender/cli`, server + worker)
- [ ] After Effects officiel installé + mode Render Only
- [ ] Plugins du preset (Magic Bullet Looks, Sapphire) installés
- [ ] Règle on/off du VPS maîtrisée (crédit essai 100 $ / 30 jours)

### ⬜ Phase 3 — Template `.aep` sur le VPS (**toi**, voir `02_TEMPLATE_AEP.md`)
- [ ] Composition 1920×1080 créée via RDP
- [ ] Calque vidéo placeholder nommé (convention à confirmer)
- [ ] Output module configuré (obligatoire AE 2023+)
- [ ] `.aep` enregistré dans `NEXRENDER/templates/` **sur le VPS** (jamais committé)

### ⬜ Phase 4 — Premier rendu de test (**toi** + moi : dépannage)
- [ ] 1 vidéo test déposée sur le VPS
- [ ] Job lancé, rendu réussi (pas de pop-up, pas de watermark, look cc2 correct)

### ⬜ Phase 5 — Automatisation (optionnelle)
- [ ] Self-hosted runner GitHub installé sur le VPS (**toi**)
- [ ] Workflow `.github/workflows/` (**moi**)

## Points en attente de décision

| Question | Statut |
|---|---|
| Nom du calque vidéo placeholder dans le `.aep` | à confirmer (`SRC` proposé) |
| Format de sortie (mp4 H.264 ? fps/résolution source ?) | à confirmer |
| Source des vidéos pour F01_INGEST (autre branche ? stockage Modal ?) | à définir |

## État Git

- Branche courante : `dev6-E` (créée depuis `main`)
- Stash en attente : `stash@{0}` = modification `.pyc` de `f09-output` à restaurer
  avec `git stash pop` quand on retourne sur `f09-output`

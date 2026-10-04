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
- [x] Documentation de branche (8 docs, cf. `NEXRENDER/README.md`)
- [x] `.gitignore` de sécurité

### ✅ Phase 1a — Artefacts Nexrender (Fait, 2026-10-04)
- [x] JSON de job de référence (`NEXRENDER/jobs/job.reference.json`)
- [x] Script JSX appliquant `cc2.ffx` (`NEXRENDER/scripts/apply_cc2.jsx`)
- [x] Contrat F01 → F02 (`NEXRENDER/contract/`)
- [x] Chemins VPS figés (`NEXRENDER/paths.json`)

### ⬜ Phase 1b — Code des frégates (**en cours**)
- [ ] `F01_INGEST` : scan source, validation, copie inbox, manifeste
- [ ] `F02_RENDER` : manifeste → jobs Nexrender, soumission, suivi, outbox
- [ ] Tests unitaires sans VPS

### ⬜ Phase 2 — VPS (**toi**, voir `NEXRENDER/docs/01_VPS_SETUP.md`)
- [ ] Node.js LTS installé sur le VPS
- [ ] Nexrender installé (`@nexrender/cli`, server + worker)
- [ ] After Effects officiel installé + mode Render Only
- [ ] Plugins du preset (Magic Bullet Looks, Sapphire) installés
- [ ] Règle on/off du VPS maîtrisée (crédit essai 100 $ / 30 jours)

### ⬜ Phase 3 — Template `.aep` sur le VPS (**toi**, voir `02_TEMPLATE_AEP.md`)
- [ ] Composition 1920×1080 créée via RDP, nommée `MAIN`
- [ ] Calque vidéo placeholder nommé `SRC`
- [ ] Output module configuré (obligatoire AE 2023+)
- [ ] `.aep` enregistré dans `C:\nexrender\templates\template.aep` (jamais committé)

### ⬜ Phase 4 — Premier rendu de test (**toi** + moi : dépannage)
- [ ] 1 vidéo test déposée sur le VPS
- [ ] Job lancé, rendu réussi (pas de pop-up, pas de watermark, look cc2 correct)

### ⬜ Phase 5 — Automatisation (optionnelle)
- [ ] Self-hosted runner GitHub installé sur le VPS (**toi**)
- [ ] Workflow `.github/workflows/` (**moi**)

## Décisions figées (Phase 1a)

| Question | Décision |
|---|---|
| Nom du calque placeholder | `SRC` |
| Nom de la composition | `MAIN` |
| Format de sortie | mp4 H.264 |
| Politique jobs | un job par vidéo |
| Plugin manquant | échec du job |
| Chemin preset | `C:\nexrender\presets\cc2.ffx` |
| Source F01 par défaut | `C:\nexrender\sources` (overridable) |

## Handoff agent

Prochaine action : **Phase 1b** — écrire le code Python de `F01_INGEST` et `F02_RENDER`.
Voir `HANDOFF.md`. Ne pas toucher Phase 2+ (VPS, c'est l'humain).

## État Git

- Branche courante : `dev6-E`
- Dernier palier : Phase 1a artefacts Nexrender

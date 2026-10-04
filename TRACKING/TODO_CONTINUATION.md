# TODO — continuation `dev-11`

Dernière mise à jour : 2026-10-04
État : **tree + Groupe 0 CUSTOS scellés**. Moteurs F01/F02/F03 = pas encore forgés.

---

## Scellé (ne pas rouvrir sans note TRACKING)

- [x] Branche `dev-11` = projet de flotte, pas une F07 dans LACRIMAE
- [x] 3 frégates : F01_OCULUS, F02_SANGUINOR, F03_CALIX
- [x] Hommage Blood Angels (Œil / Ange qui suit / Calice)
- [x] IN/OUT isolés, transit orchestrateur, CUSTOS
- [x] Actions = dispatch ; Modal = compute
- [x] Cibles `face | nose | eyes`
- [x] Audio stream copy
- [x] Pile : MediaPipe + One Euro + PyAV/FFmpeg + Modal
- [x] Tree docs : README, DESIGN, GATES, campaign log, README frégates, exemples JSON
- [x] Tree runtime : IN/OUT `.gitkeep`, CONFIG, SHARED, stubs moteurs
- [x] Groupe 0 : `LAC_CUSTOS.py`, `LAC_RUN.py`, tests contrat, workflows GHA contrats

---

## Groupe 0 — Gardien (fait)

- [x] `LAC_CUSTOS.py` : check-in / check-out F01 F02 F03 selon `DEV11_GATES.md`
- [x] `LAC_RUN.py` : portes I–IV, transit copies IN←OUT, stop si moteur non forge
- [x] Tests contrat : JSON fixtures valides / invalides (sans MP4 lourds)
- [x] Workflow GHA : pytest contrats (`dev11_contracts.yml`)

---

## Groupe 1 — F01 OCULUS

- [ ] `f01_oculus.py` : MediaPipe Face Landmarker, Tasks API
- [ ] Ecrire `dev11.landmarks.v1` par stem
- [ ] `job_request.target` → IDs landmarks (face centre / nose / eyes mid)
- [ ] Hold de détection : `detected=false` si sous seuil
- [ ] Rapport `oculus_report.json` (taux détection, gaps)
- [ ] Image Modal CPU + modèles dans volume
- [ ] Fixture : 1 clip court synthétique en `tests/fixtures/` (généré CI, pas commité)

---

## Groupe 2 — F02 SANGUINOR (cœur produit)

- [ ] One Euro sur cx, cy (params dans `CONFIG/camera_defaults.json`)
- [ ] Deadzone : intérieur = camera immobile
- [ ] Hold-last si `detected=false`
- [ ] Zoom lent borné (`zoom_max_delta_per_s`)
- [ ] Yeux au tiers haut si target=`eyes` ou composition talking-head
- [ ] Clamp crop toujours dans le frame source
- [ ] Ecrire `dev11.camera_path.v1`
- [ ] Tests unitaires jitter / deadzone **sans** vidéo (frames synthétiques) — fichier placeholder `tests/test_sanguinor_filter.py`

---

## Groupe 3 — F03 CALIX

- [ ] FFmpeg crop depuis camera_path (filtre crop+scale 1080×1920)
- [ ] `-c:a copy` si audio ; flag manifeste si absent
- [ ] yuv420p + faststart + H.264
- [ ] `calix_manifest.json` + hashes
- [ ] Agrégation stricte : un stem manquant = REFUS
- [ ] Modal GPU optionnel `h264_nvenc`

---

## Groupe 4 — Orchestration

- [x] `.github/workflows/dev11_oculus.yml` : squelette portes / secrets / timeouts
- [ ] `modal/app.py` : app `lacrimae-dev11-oculus`, stages F01 / F02 / F03 (skeleton only)
- [ ] Videos via Release GitHub ou URI objet — jamais artifact > quota
- [ ] Secrets repo : `MODAL_TOKEN_ID`, `MODAL_TOKEN_SECRET` (documentés, non écrits)

---

## Groupe 5 — Branchement flottes sœurs

- [ ] Note d'intégration `dev10` PUR : où pousser les clips vers F01/IN
- [ ] Note d'intégration `dev9` ranking / `dev8` reveal
- [ ] Interdit : importer le code PICTOR ici

---

## Hors scope (ne pas faire dans cette continuation)

- Preview Remotion, titres, SFX, ranking
- Camouflage / Luther
- YOLO commercial
- Tracking dans GitHub Actions
- OpenReel / éditeur navigateur
- Multi-visages v1 (max_num_faces=1, HOLD si plusieurs)

---

## Prochaine action recommandée

Forger **Groupe 1** (`f01_oculus.py` MediaPipe) maintenant que CUSTOS existe. Ne pas sauter à F02 tant que F01 n'écrit pas un JSON que P-OC-10…16 acceptent.

# TODO — continuation `dev-11`

Dernière mise à jour : 2026-10-04
État : **F02 forgé**. F01/F03 moteurs présents. Modal stages forgés. Reste : tokens + premier clip.

Carte : `TRACKING/WHERE_WE_ARE.md`

---

## Scellé (ne pas rouvrir sans note TRACKING)

- [x] Branche `dev-11` = projet de flotte, pas une F07 dans LACRIMAE
- [x] 3 frégates : F01_OCULUS, F02_SANGUINOR, F03_CALIX
- [x] Hommage Blood Angels (Œil / Ange qui suit / Calice)
- [x] IN/OUT isolés, transit orchestrateur, CUSTOS
- [x] Actions = dispatch ; Modal = compute
- [x] Cibles `face | nose | eyes`
- [x] Audio stream copy
- [x] Pile : MediaPipe + One Euro + FFmpeg + Modal
- [x] Tree docs + IN/OUT `.gitkeep` + CONFIG
- [x] Groupe 0 CUSTOS / LAC_RUN / tests contrat / GHA contrats
- [x] Groupe 2 F02 : 1€ + deadzone + hold-last + zoom + clamp
- [x] Note sœurs `TRACKING/INTEGRATION_SISTERS.md`

---

## Groupe 0 — Gardien (fait)

- [x] `LAC_CUSTOS.py`
- [x] `LAC_RUN.py` (skip HOLD au transit)
- [x] Tests contrat sans MP4 lourds
- [x] `dev11_contracts.yml`

---

## Groupe 1 — F01 OCULUS

- [x] `f01_oculus.py` : Tasks API si modèle, sinon HOLD `detected=false`
- [x] Ecrire `dev11.landmarks.v1` par stem
- [x] `job_request.target` → oval_mean / nose 4 / eyes 468+473
- [x] Rapport `oculus_report.json`
- [x] Image Modal CPU + volume `face_landmarker.task`
- [ ] Fixture clip synthétique généré CI (pas commité)

---

## Groupe 2 — F02 SANGUINOR (cœur produit) — fait

- [x] One Euro cx, cy
- [x] Deadzone immobile
- [x] Hold-last si `detected=false`
- [x] Zoom borné `zoom_max_delta_per_s`
- [x] Yeux `eyes_y_anchor`
- [x] Clamp crop 9:16 in-bounds
- [x] `dev11.camera_path.v1`
- [x] `tests/test_sanguinor_filter.py`

---

## Groupe 3 — F03 CALIX

- [x] Crop+scale depuis camera_path (FFmpeg encode H.264 yuv420p +faststart)
- [x] `-c:a copy` ou `audio: none`
- [x] `calix_manifest.json` + sha256
- [x] Agrégation stricte CUSTOS P-CX-6
- [ ] Modal GPU `h264_nvenc`
- [ ] Test encode bout-en-bout (clip synthétique CI, pas git)

---

## Groupe 4 — Orchestration

- [x] `dev11_oculus.yml` timeouts / secrets / `modal run`
- [x] `modal/app.py` stages réels (bootstrap / oculus / sanguinor / calix / full)
- [x] Videos via `object_uri` HTTPS (MP4 ou ZIP)
- [ ] Secrets `MODAL_TOKEN_ID` / `MODAL_TOKEN_SECRET` dans le repo GitHub

---

## Groupe 5 — Branchement flottes sœurs

- [x] Note `dev10` / `dev9` / `dev8` dans `INTEGRATION_SISTERS.md`
- [x] Interdit PICTOR ici
- [ ] Premier transit réel depuis une campagne sœur

---

## Hors scope

- Preview Remotion, titres, SFX, ranking
- Camouflage / Luther
- YOLO commercial
- Tracking dans GitHub Actions
- OpenReel
- Multi-visages v1

---

## Prochaine action

1. Poser secrets `MODAL_TOKEN_ID` / `MODAL_TOKEN_SECRET` (repo GitHub + CLI Modal).
2. Dispatch `bootstrap` puis `full` avec `object_uri` d'un clip 9:16 hors git.
3. Tests contrat A (pytest) + campagne B une fois le clip fourni.

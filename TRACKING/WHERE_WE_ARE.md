# WHERE WE ARE — `dev-11`

Date : 2026-10-04
Branche : `dev-11` → `origin/dev-11` (https://github.com/jfbjfojfonf/LACRIMAE/tree/dev-11)

---

## Une phrase

Flotte camera virtuelle 9:16. Tree + CUSTOS scellés. F02 (cœur) **forgé**. F01 écrit des landmarks (MediaPipe si modèle, sinon HOLD). F03 croppe si FFmpeg. Modal **forgé** (`modal/app.py` stages bootstrap/oculus/sanguinor/calix/full). GHA `dev11_oculus.yml` dispatch `modal run`. Campagne réelle : token Modal + clip 9:16.

---

## Par pièce

| Pièce | Fichier | État | Rôle |
|-------|---------|------|------|
| Loi | `TRACKING/DEV11_DESIGN.md` | scellé | 3 frégates, pas F07 |
| Portes | `TRACKING/DEV11_GATES.md` | scellé | P-OC / P-SG / P-CX / P-ISO / P-CI |
| Gardien | `LAC_CUSTOS.py` | forgé | check-in/out, HOLD vs REFUS |
| Orchestrateur | `LAC_RUN.py` | forgé | transit copies, skip HOLD |
| Config camera | `CONFIG/camera_defaults.json` | scellé | deadzone, 1€, zoom |
| F01 contrat | `F01_OCULUS/README.md` | scellé | landmarks JSON |
| F01 moteur | `F01_OCULUS/CODEBASE/f01_oculus.py` | forgé | MediaPipe ou HOLD |
| F02 contrat | `F02_SANGUINOR/README.md` | scellé | camera_path JSON |
| F02 1€ | `F02_SANGUINOR/CODEBASE/one_euro.py` | forgé | Casiez |
| F02 camera | `F02_SANGUINOR/CODEBASE/camera.py` | forgé | deadzone hold-last zoom clamp |
| F02 moteur | `F02_SANGUINOR/CODEBASE/f02_sanguinor.py` | forgé | JSON→JSON, zéro MP4 |
| F03 contrat | `F03_CALIX/README.md` | scellé | tracked MP4 |
| F03 moteur | `F03_CALIX/CODEBASE/f03_calix.py` | forgé | crop+scale+audio copy |
| IO | `SHARED/CODEBASE/ffmpeg_io.py` | forgé | probe/decode/encode |
| Tests contrat | `tests/test_*_contract.py` | forgé | 0 decode campagne |
| Tests filtre | `tests/test_sanguinor_filter.py` | forgé | deadzone/hold/crop |
| GHA contrats | `.github/workflows/dev11_contracts.yml` | scellé | pytest push/PR |
| GHA Modal | `.github/workflows/dev11_oculus.yml` | forgé | dispatch `modal run`, pas ffmpeg |
| Modal app | `modal/app.py` | forgé | Groupe 4 stages réels |
| Sœurs | `TRACKING/INTEGRATION_SISTERS.md` | noté | où pousser les clips |

---

## Ce qui manque pour une vraie campagne

1. Secrets GitHub `MODAL_TOKEN_ID` + `MODAL_TOKEN_SECRET` (et token pour `modal run` local)
2. Clip 9:16 H.264 via `object_uri` (hors git) — bootstrap telecharge `face_landmarker.task`
3. `job_request.json` : GHA `--target face|nose|eyes` ou copie de l'exemple en local
4. Sans token Modal : GHA job `modal` REFUS P-CI-2. Sans clip : Porte I P-OC-2.

---

## Relances

| Tu changes | Tu relances |
|------------|-------------|
| cible face/nose/eyes ou le clip | F01 |
| deadzone / 1€ / zoom | F02 seulement |
| codec / 1080×1920 | F03 seulement |

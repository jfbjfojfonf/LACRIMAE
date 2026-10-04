# WHERE WE ARE — `dev-11`

Date : 2026-10-04
Branche : `dev-11` → `origin/dev-11` (https://github.com/jfbjfojfonf/LACRIMAE/tree/dev-11)

---

## Une phrase

Flotte camera virtuelle 9:16. Tree + CUSTOS scellés. F02 (cœur) **forgé**. F01 écrit des landmarks (MediaPipe si modèle, sinon HOLD). F03 croppe si FFmpeg. Modal = skeleton. Moteurs **ne tournent pas** de campagne réelle tant que clips + `face_landmarker.task` ne sont pas là.

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
| GHA Modal | `.github/workflows/dev11_oculus.yml` | skeleton | dispatch, pas ffmpeg |
| Modal app | `modal/app.py` | skeleton | Groupe 4 |
| Sœurs | `TRACKING/INTEGRATION_SISTERS.md` | noté | où pousser les clips |

---

## Ce qui manque pour une vraie campagne

1. Clips 9:16 H.264 dans `F01_OCULUS/IN/clips/` (hors git)
2. `job_request.json` copié depuis l'exemple
3. Modèle `face_landmarker.task` (MediaPipe Tasks) sur Modal / volume
4. `modal/app.py` stages réels + secrets `MODAL_TOKEN_*`
5. Sans (3) : F01 écrit `detected=false` partout → HOLD P-OC-14 → F02 non transité

---

## Relances

| Tu changes | Tu relances |
|------------|-------------|
| cible face/nose/eyes ou le clip | F01 |
| deadzone / 1€ / zoom | F02 seulement |
| codec / 1080×1920 | F03 seulement |

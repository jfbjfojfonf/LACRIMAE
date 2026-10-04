# Campaign log — `dev-11`

> Journal de branche. Une entrée par décision ou forge. Pas un changelog git.

---

## 2026-10-04 — Fondation

- Branche créée : `dev-11`.
- Décision : ce n'est **pas** une frégate F07 dans LACRIMAE. C'est une flotte dédiée camera virtuelle, consommée par les autres branches.
- Flotte : F01_OCULUS, F02_SANGUINOR, F03_CALIX (noms scellés, hommage Blood Angels).
- Tree docs posé : README racine, DESIGN, GATES, TODO, README frégates, contrats JSON exemple, CONFIG, Modal/GHA squelettes.
- Moteurs : non forgés. Interdit de coder le tracking tant que Groupe 0 CUSTOS n'est pas là.
- Compute : Actions orchestre, Modal exécute.
- Cible défaut : `face`. Alternatives `nose`, `eyes`.

Magos : cadrage validé avant forge.

---

## 2026-10-04 — Tree + Groupe 0

- README frégates F01/F02/F03, exemples JSON, IN/OUT `.gitkeep`.
- `CONFIG/camera_defaults.json` : deadzone, 1€, zoom, jitter.
- `LAC_CUSTOS.py` lit `DEV11_GATES.md` (P-OC / P-SG / P-CX / P-ISO). HOLD vs REFUS.
- `LAC_RUN.py` : seul transit IN←OUT. Moteurs stubs exit 2.
- Tests contrat `tests/` sans decode MP4. GHA `dev11_contracts.yml` + `dev11_oculus.yml` (Modal skeleton).
- Interdit toujours : MediaPipe / One Euro / FFmpeg campaign tant que Groupe 1 n'est pas demandé.

Magos : Groupe 0 scellé. Groupe 1 ensuite.

---

## 2026-10-04 — Moteurs + chronique

- Poussé `dev-11` : https://github.com/jfbjfojfonf/LACRIMAE/tree/dev-11
- F02 forgé : `one_euro.py`, `camera.py`, `f02_sanguinor.py`. Tests deadzone / hold-last / clamp sans video.
- F01 : MediaPipe Tasks si modèle, sinon HOLD (P-OC-14 bloque transit).
- F03 : crop Python + ffmpeg libx264 +faststart + audio copy.
- `SHARED/CODEBASE/ffmpeg_io.py` : probe/decode/encode. Isolation OK.
- Docs : `WHERE_WE_ARE.md`, `INTEGRATION_SISTERS.md`, TODO mis à jour.
- Modal toujours skeleton. Pas de campagne réelle sans clips + modèle.

Magos : F02 est le cœur. Ne pas retune F01 pour un jitter camera.

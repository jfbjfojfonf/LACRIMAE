# LACRIMAE — branche `dev-11`

> *The Eye sees. The Sanguinor follows. The Chalice seals.*

**Flotte OCULUS** — camera virtuelle lisse pour Shorts 9:16. Ce n'est pas une frégate insérée dans une autre branche. C'est un **projet de branche** : les autres modes LACRIMAE (`dev`, `dev4`, `dev8`, `dev9`, `dev10`) lui envoient des clips déjà cadrés ; il leur rend des clips **trackés**, visage / nez / yeux, sans tremblement.

Le reframe 9:16 existe déjà ailleurs. `dev-11` n'ingère pas une vidéo longue, ne choisit pas les cuts, ne compose pas de titre, ne camoufle pas. Il ne fait **qu'une chose** : coller une caméra stable au visage.

---

## Pipeline

```
clips 9:16 (autre branche / Magos)
        │
        ▼
[F01 OCULUS]     MediaPipe Face Landmarker
        │        OUT/landmarks/<stem>.json
        ▼
[F02 SANGUINOR]  One Euro + deadzone + inertie + zoom
        │        OUT/camera_path/<stem>.json
        ▼
[F03 CALIX]      FFmpeg crop 9:16 + audio original
        │        OUT/tracked/<stem>.mp4
        ▼
retour à la flotte appelante (Preview / Signum / Camouflage / Luther)
```

GitHub Actions **orchestre**. Modal **exécute** (GPU / CPU). Aucun tracking vidéo ne tourne sur un runner GitHub.

---

## Frégates

| Frégate | Nom | Hommage | Mission | Contrat OUT |
|---------|-----|---------|---------|-------------|
| **F01_OCULUS** | L'Œil | Regard de Sanguinius | Landmarks nez / yeux / ovale | `landmarks/<stem>.json` |
| **F02_SANGUINOR** | L'Ange d'or | Celui qui suit le guerrier | Camera virtuelle lisse | `camera_path/<stem>.json` |
| **F03_CALIX** | Le Calice | Red Grail | Crop 9:16 + audio | `tracked/<stem>.mp4` + `calix_manifest.json` |

Trois frégates. Pas F00 (l'ingest est chez l'appelant). Pas F04–F06 (sceau, camouflage, luther restent sur la branche de production).

Retune sans relancer MediaPipe : relancer **F02** seulement. Ré-encoder sans retune : relancer **F03** seulement.

---

## Rites du Sang

1. **LOI D'ISOLEMENT** — chaque frégate lit son `IN/`, écrit son `OUT/`. Jamais le dossier d'une sœur.
2. **RITE DE VALIDATION** — `LAC_CUSTOS.py` après chaque output. Pas de transit sans verdict.
3. **TRANSIT** — orchestrateur uniquement (`LAC_RUN.py` local ou GitHub Actions). Jamais à la main entre frégates en production.
4. **DUREE PAR LA SOURCE** — F03 ne change pas la durée du clip. Il recadre.
5. **AUDIO INTACT** — stream copy audio. Calix n'invente pas de musique.
6. **PORTES** — I Brief (cible + clips), II Landmarks, III Camera, IV Calice.

---

## Pile technique

| Couche | Outil | Depot |
|--------|-------|-------|
| Detection | MediaPipe Face Landmarker | https://github.com/google-ai-edge/mediapipe |
| Lissage | 1€ filter | https://github.com/casiez/OneEuroFilter |
| Frames | PyAV | https://github.com/PyAV-Org/PyAV |
| Encode / mux | FFmpeg | https://github.com/FFmpeg/FFmpeg |
| Compute | Modal | https://github.com/modal-labs/modal-client |
| CI | GitHub Actions | dispatch uniquement |

YOLO / Ultralytics : **hors pile v1** (licence AGPL). Fallback multi-têtes documenté, pas implémenté.

---

## Quickstart

```
1. Déposer les clips 9:16 H.264 dans F01_OCULUS/IN/clips/
2. Copier F01_OCULUS/IN/job_request.example.json → job_request.json (cible: face | nose | eyes)
3. python LAC_CUSTOS.py --frigate F01 --mode check-in
4. python LAC_RUN.py run
5. python -m pytest tests
```

Sans `face_landmarker.task` : F01 HOLD (detected=false) → pas de transit F02 (P-OC-14).
F02 se teste seul sur JSON : `python F02_SANGUINOR/CODEBASE/f02_sanguinor.py --in ... --out ...`
GHA : `dev11_contracts.yml` pytest. `dev11_oculus.yml` Modal skeleton. Videos hors git.

---

## Docs de campagne

| Document | Rôle |
|----------|------|
| `TRACKING/DEV11_DESIGN.md` | Architecture, hommage, pourquoi 3 frégates |
| `TRACKING/DEV11_GATES.md` | Portes bloquantes P-OC / P-SG / P-CX |
| `TRACKING/WHERE_WE_ARE.md` | Où on en est, pièce par pièce |
| `TRACKING/TODO_CONTINUATION.md` | Scellé vs reste à forger |
| `TRACKING/LACRIMAE_CAMPAIGN_LOG.md` | Journal de branche |
| `TRACKING/INTEGRATION_SISTERS.md` | Branchement dev10 / dev9 / dev8 |
| `F01_OCULUS/README.md` | Contrat F01 |
| `F02_SANGUINOR/README.md` | Contrat F02 |
| `F03_CALIX/README.md` | Contrat F03 |

> *LACRIMAE dev-11 — For the Angel's Tears shall become gold. Ad Victoriam.*

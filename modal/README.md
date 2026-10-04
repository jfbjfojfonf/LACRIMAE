# Modal — `lacrimae-dev11-oculus`

GitHub Actions **orchestre**. Modal **exécute**. Jamais de decode/tracking MP4 sur un runner GHA (P-CI-1).

## App

Nom : `lacrimae-dev11-oculus`

Fichier : `modal/app.py`

| Stage | Fonction Modal | Compute v1 |
|-------|----------------|------------|
| bootstrap | `run_stage("bootstrap")` | CPU, telecharge `face_landmarker.task` sur volume |
| F01 | `run_stage("oculus")` | CPU, volume modeles MediaPipe |
| F02 | `run_stage("sanguinor")` | CPU |
| F03 | `run_stage("calix")` | CPU libx264 |
| full | `LAC_RUN.py run` | CPU, portes I-IV |

Volumes :

- `lacrimae-dev11-models` → `/models/face_landmarker.task`
- `lacrimae-dev11-campaign` → `/campaign/IN/clips` + `/campaign/OUT`

## Secrets

Repo GitHub (P-CI-2, P-ISO-3) :

- `MODAL_TOKEN_ID`
- `MODAL_TOKEN_SECRET`

Jamais dans git. Jamais dans un JSON de campagne.

Creer un token : https://modal.com/settings/tokens

## CLI local (une fois token present)

```
python -m modal run modal/app.py --stage bootstrap
python -m modal run modal/app.py --stage full --object-uri "https://example.com/clip.mp4" --target face
```

`object_uri` : MP4 direct ou ZIP de MP4. Videos jamais dans git.

## Timeout

Documente dans `.github/workflows/dev11_oculus.yml` (P-CI-3). Defaut : 10 min / clip F01, 5 min F02, 15 min F03. Job GHA 45 min.

## Videos

IN clips via URI objet (HTTPS / S3-compatible public). OUT tracked : volume Modal `lacrimae-dev11-campaign` + rapports JSON. Artifact GHA = JSON seulement.

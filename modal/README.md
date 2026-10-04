# Modal — `lacrimae-dev11-oculus`

GitHub Actions **orchestre**. Modal **exécute**. Jamais de decode/tracking MP4 sur un runner GHA (P-CI-1).

## App

Nom : `lacrimae-dev11-oculus`

| Stage | Fonction Modal | Compute v1 |
|-------|----------------|------------|
| F01 | `stage_oculus` | CPU, volume modèles MediaPipe |
| F02 | `stage_sanguinor` | CPU |
| F03 | `stage_calix` | CPU libx264 ; GPU optionnel `h264_nvenc` |

## Secrets

Repo GitHub :

- `MODAL_TOKEN_ID`
- `MODAL_TOKEN_SECRET`

Jamais dans git. Jamais dans un JSON de campagne (P-ISO-3, P-CI-2).

## Timeout

Documenté dans `.github/workflows/dev11_oculus.yml` (P-CI-3). Défaut : 10 min / clip F01, 5 min F02, 15 min F03.

## Videos

IN clips via URI objet (S3/R2) ou GitHub Release. Jamais artifact GHA > quota. OUT tracked : objet distant + `calix_manifest.json` en artifact JSON.

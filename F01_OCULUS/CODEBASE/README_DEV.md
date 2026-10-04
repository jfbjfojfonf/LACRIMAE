# F01 OCULUS — README DÉVELOPPEUR

> *"L'Œil nomme. Il ne poursuit pas."*

## Mission

MediaPipe Face Landmarker sur chaque frame (ou sous-échantillon déclaré). Écrire `dev11.landmarks.v1`.

## Fichiers

| Fichier | Rôle |
|---------|------|
| `f01_oculus.py` | Moteur : MediaPipe Tasks VIDEO, sinon HOLD |
| `models/` | `face_landmarker.task` (hors git, `*.task` ignore) |
| `README_DEV.md` | Ce fichier |

## CLI prévu

```
python3 F01_OCULUS/CODEBASE/f01_oculus.py \
  --in F01_OCULUS/IN \
  --out F01_OCULUS/OUT
```

Aucun autre path. Pas de flag `--clips` pointant hors IN.

## Mapping target → landmarks

| `target` | Construction `target.x/y` |
|----------|---------------------------|
| `face` | centroïde ovale / face oval landmarks |
| `nose` | tip (équivalent point 4 Face Mesh ; IDs Tasks à figer dans le code Groupe 1) |
| `eyes` | milieu iris G / D (refine landmarks ON) |

Documenter les IDs **dans le JSON** (`landmark_ids`) pour que F02 ne hardcode pas MediaPipe.

## Interdit

- Écrire un MP4
- Lisser (1€ = F02)
- Lire `F02_*` ou `F03_*`
- Appeler FFmpeg encode

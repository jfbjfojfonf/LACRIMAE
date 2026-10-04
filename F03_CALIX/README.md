# F03_CALIX — Le Calice

> *Le sang est versé. Le Calice le scelle.*

## Mission

Une fonction : **appliquer** le path. Recadrer chaque clip en 9:16 selon `camera_path`, muxer l'audio original, écrire les MP4 trackés + manifeste.

Pas de détection. Pas de lissage. Si le path tremble, c'est F02 qu'on relance, pas F03.

## Hommage

CALIX — le Red Grail. Ce qui a été vu (OCULUS) et suivi (SANGUINOR) est **scellé** dans un fichier livrable.

## Technologie cible

| Composant | Cible |
|-----------|--------|
| FFmpeg | crop + scale 1080×1920, H.264 yuv420p, `+faststart` |
| Audio | `-c:a copy` |
| Wrapper | PyAV et/ou ffmpeg-python |
| Compute | Modal CPU ; GPU `h264_nvenc` optionnel |

Depots : https://github.com/FFmpeg/FFmpeg · https://github.com/PyAV-Org/PyAV · https://github.com/kkroening/ffmpeg-python

## Structure

```
F03_CALIX/
├── CODEBASE/
│   ├── f03_calix.py
│   └── README_DEV.md
├── IN/
│   ├── clips/
│   └── camera_path/
├── OUT/
│   ├── tracked/
│   ├── calix_manifest.json
│   └── calix_report.json
├── tests/
└── README.md
```

## IN

Transit depuis F02 :

- `IN/camera_path/<stem>.json`
- `IN/clips/<stem>.mp4` (même stem, source à cropper)

## OUT

```
OUT/tracked/<stem>.mp4
OUT/calix_manifest.json     schema dev11.calix_manifest.v1
OUT/calix_report.json
```

## Règles

- Durée = durée source ± 1 frame.
- 9:16. Défaut 1080×1920.
- Audio copy. Si pas d'audio : champ `audio: "none"` dans le manifeste, fichier quand même produit.
- **Agrégation stricte** : un stem manquant = REFUS de tout l'artifact (doctrine PUR / P-CX-6).

## Relance

Changer codec / résolution de sortie = F03 seulement.

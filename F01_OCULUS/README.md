# F01_OCULUS — L'Œil

> *Le Regard de Sanguinius. Voir, avant de suivre.*

## Mission

Une fonction : **détecter**. Produire, pour chaque clip 9:16, un fichier de landmarks temporel. Ne pas recadrer. Ne pas lisser. Ne pas encoder.

## Hommage

OCULUS — l'œil. Vision du Primarque. La flotte ne bouge pas tant que l'Œil n'a pas nommé le visage.

## Technologie cible

| Composant | Cible |
|-----------|--------|
| Python | 3.10+ |
| MediaPipe Tasks | Face Landmarker |
| Lecture frames | PyAV |
| Compute | Modal CPU (volume modèles) |

Depot : https://github.com/google-ai-edge/mediapipe

## Structure

```
F01_OCULUS/
├── CODEBASE/
│   ├── f01_oculus.py          ← moteur (à forger, Groupe 1)
│   └── README_DEV.md
├── IN/
│   ├── clips/                 ← MP4 9:16 poussés par l'appelant
│   └── job_request.json
├── OUT/
│   ├── landmarks/             ← <stem>.json
│   └── oculus_report.json
├── tests/
│   └── test_oculus_contract.py
└── README.md                  ← ce fichier
```

## IN

```
IN/
├── job_request.json
└── clips/
    ├── clip_001.mp4
    └── ...
```

`job_request.json` — voir `IN/job_request.example.json`.

Champs critiques :

- `target` : `face` | `nose` | `eyes`
- `max_num_faces` : 1 en v1
- `min_detection_confidence` : 0.5 défaut

## OUT

```
OUT/
├── landmarks/<stem>.json      schema dev11.landmarks.v1
└── oculus_report.json
```

F01 n'écrit **aucun** MP4.

## Schema `dev11.landmarks.v1`

Voir `OUT/examples/landmarks.example.json`. Chaque frame :

- `t_s`, `detected`
- `target.x`, `target.y` normalisés `[0,1]` si detected
- `bbox` optionnel (ovale visage) pour le zoom F02

## Rites

- **ISOLEMENT** : lit uniquement `F01_OCULUS/IN/`.
- **CUSTOS** : `python LAC_CUSTOS.py --frigate F01 --mode check-in` puis `check-out`.
- **HOLD** : taux détection < 0.85 → stem en HOLD, les autres passent (P-OC-14).

## Relance

Relancer F01 **seulement** si la cible (`face/nose/eyes`) change ou si le clip source change. Un retune camera = F02, pas F01.

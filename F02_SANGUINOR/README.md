# F02_SANGUINOR — L'Ange d'or

> *Il n'est pas le guerrier. Il apparaît à ses côtés et suit.*

## Mission

Une fonction : **suivre sans trembler**. Lire les landmarks. Écrire un path de caméra virtuelle 9:16 (centre + zoom) lissé. Ne pas encoder de vidéo.

C'est le **cœur produit** de `dev-11`. Sans F02, F01+F03 = crop naïf qui tue la retention.

## Hommage

SANGUINOR — l'Ange d'or des Blood Angels. Il **accompagne**. Deadzone, inertie, 1€ : la camera ne colle pas au bruit du nez frame à frame.

## Technologie cible

| Composant | Cible |
|-----------|--------|
| Python | 3.10+ |
| Filtre | One Euro (réf. https://github.com/casiez/OneEuroFilter) |
| Params | `CONFIG/camera_defaults.json` |
| Compute | Modal CPU |

## Structure

```
F02_SANGUINOR/
├── CODEBASE/
│   ├── f02_sanguinor.py
│   └── README_DEV.md
├── IN/
│   ├── clips/
│   ├── landmarks/
│   └── camera_request.json
├── OUT/
│   ├── camera_path/
│   └── sanguinor_report.json
├── tests/
└── README.md
```

## IN

Transit depuis F01 :

- `IN/landmarks/<stem>.json` (copie, pas un symlink vers F01/OUT)
- `IN/clips/<stem>.mp4` (dimensions source pour le clamp)
- `IN/camera_request.json` (overrides optionnels ; sinon CONFIG)

F02 **interdit** `open("F01_OCULUS/OUT/...")`.

## OUT

```
OUT/camera_path/<stem>.json     schema dev11.camera_path.v1
OUT/sanguinor_report.json
```

Aucun MP4.

## Comportement camera (contrat, pas l'algo détaillé)

1. **Deadzone** — si la cible reste dans le rectangle mort autour du centre actuel, `cx,cy` inchangés.
2. **One Euro** — hors deadzone, lisser jitter vs lag (mincutoff / beta dans CONFIG).
3. **Hold-last** — `detected=false` : garder le dernier centre, ne **pas** recentrer l'image.
4. **Zoom** — dérive de `bbox` (taille visage). Variation bornée par seconde.
5. **Clamp** — crop 9:16 entièrement dans le frame source. Toujours.

## Relance

Changer deadzone / 1€ / zoom = relancer **F02 seulement** (landmarks déjà là).

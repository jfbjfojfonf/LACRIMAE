# F02 SANGUINOR — README DÉVELOPPEUR

> *"L'Ange suit. Il ne saccade pas."*

## Mission

`landmarks.v1` → `camera_path.v1`. Zéro MediaPipe ici.

## CLI prévu

```
python3 F02_SANGUINOR/CODEBASE/f02_sanguinor.py \
  --in F02_SANGUINOR/IN \
  --out F02_SANGUINOR/OUT \
  --config CONFIG/camera_defaults.json
```

## Ordre d'application (figé)

1. Lire target x,y (ou hold-last)
2. Deadzone → skip update centre
3. One Euro sur cx, cy
4. Zoom depuis bbox lissée
5. Clamp crop 9:16 dans [0,width]×[0,height]
6. Écrire frame path

## Tests sans vidéo

`tests/test_sanguinor_filter.py` : séries x,y synthétiques. Deadzone immobile, hold-last, pas de NaN, crop 9:16 in-bounds.

Moteur **forgé**. Crop : k pair, `w=9k` `h=16k` (jamais un 9:16 cassé par arrondi pair).

## Interdit

- Réimporter MediaPipe
- Écrire MP4
- Lire hors `IN/` + `CONFIG/`

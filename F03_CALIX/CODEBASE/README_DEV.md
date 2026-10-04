# F03 CALIX — README DÉVELOPPEUR

> *"Le Calice n'invente pas le geste. Il le conserve."*

## CLI prévu

```
python3 F03_CALIX/CODEBASE/f03_calix.py \
  --in F03_CALIX/IN \
  --out F03_CALIX/OUT
```

## Encode v1

- Filtre : crop exact pixels du path + scale 1080×1920
- Video : libx264 (ou h264_nvenc si Modal GPU)
- Pix_fmt : yuv420p
- Movflags : +faststart
- Audio : copy

Path crop déjà clampé par F02. Si crop illégal : **REFUS**, ne pas "réparer" en recentrant (ce serait refaire Sanguinor).

## Interdit

- MediaPipe
- One Euro
- Loudnorm / métadonnées camouflage (métier F05/F06 ailleurs)
- Drop audio sans le déclarer

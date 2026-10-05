# F04_HEISENBERG

Frégate TEMPS. Prend le MP4 LOOK de PICTOR + le manifeste et **ecrit un
nouveau MP4**. Pas du JSON advisory. Pas Signum.

## Ce qu'il execute

- Jump cuts (silences `breath_cut` / `idea_cut` : skip 80 ms)
- Punch-in **par cut** : a `in`, coupe et joue uniquement `[in, out]`
  recadre plus serre (crop + scale du **segment**, pas de l'image animee) ;
  a `out`, coupe et revient au framing normal
- B-roll / memes (overlay, flash blanc a l'ENTREE uniquement)
- SFX cales sur la meme frame, sous la voix (si fichiers presents)
- Ducking / smash audio via amix volume

## Contrats

| | Chemin |
|--|--------|
| IN | MP4 PICTOR + `pur_manifest.json` |
| OUT | `OUT/pur_<angle>.mp4` (fichier video reel) |
| Code | `CODEBASE/heisenberg.py` |

```bash
python3 F04_HEISENBERG/CODEBASE/heisenberg.py \
  --input F03_PICTOR/OUT/pur_A01_look.mp4 \
  --manifest BRIDGE_PERTURABO/OUT/pur_manifest.json \
  --out F04_HEISENBERG/OUT
```

`--dry-run` ecrit le plan JSON sans ffmpeg.

## Interdits

- Zoom / swell / scale anime / zoompan
- Sortie JSON sans MP4
- Modifier le look (blur / split / overlay) — deja fige par PICTOR

Si Heisenberg ne sort pas un MP4 lisible, porte P3 = rouge, pas de livraison.

Voir `TRACKING/GUIDE_BRAS_ARME_PUR.md` etape 5.

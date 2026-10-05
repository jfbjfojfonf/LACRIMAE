# F04_HEISENBERG

Frégate TEMPS. Prend le MP4 LOOK de PICTOR + le manifeste et **ecrit un
nouveau MP4**. Pas du JSON advisory. Pas Signum.

## Ce qu'il execute

- Jump cuts (silences)
- Punch-in **par cut** : a `in`, coupe et joue uniquement `[in, out]`
  recadre plus serre (crop + scale du **segment**, pas de l'image animee) ;
  a `out`, coupe et revient au framing normal
- B-roll / memes
- Flash blanc a l'ENTREE d'un B-roll uniquement (jamais a la sortie)
- SFX cales sur la meme frame, sous la voix
- Ducking / smash audio

## Contrats

| | Chemin |
|--|--------|
| IN | MP4 PICTOR + `pur_manifest.json` |
| OUT | `OUT/pur_<angle>.mp4` (fichier video reel) |
| Code (a venir) | `CODEBASE/heisenberg.py` |

## Interdits

- Zoom / swell / scale anime
- Sortie JSON sans MP4
- Modifier le look (blur / split / overlay) — deja fige par PICTOR

Si Heisenberg ne sort pas un MP4 lisible, porte P3 = rouge, pas de livraison.

Voir `TRACKING/GUIDE_BRAS_ARME_PUR.md` etape 5.

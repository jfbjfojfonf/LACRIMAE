# F07_CAPTION

Sous-titres 3D mot-a-mot (clipping). Frégate **hors flux PUR jour 1**.
Coloring LUT (`.cube`) et LOOK F03 ne passent pas ici.

Une frégate, deux halves : TRAVAIL (Whisper / Blender / overlay) et
PREVIEW (coque JS, proof frame). IN/OUT a la racine, comme les autres.

H0–H4 poses. Preview coque Vite. Whisper GHA. Proof + rendu Modal Blender. Overlay + hook F05/F06.

## Arbre

```text
F07_CAPTION/
  TRAVAIL/CODEBASE/     Whisper GHA + Blender/Modal + overlay (H2+)
  TRAVAIL/tests/
  PREVIEW/CODEBASE/     coque type F03_PREVIEW, moteur telecharge ailleurs (H1)
  IN/                   video cible (+ font optionnelle) — jamais commitee
  OUT/                  transcript.json, style.json (s1), proof PNG, calque
```

## Contrats

| Fichier | Role | Duree de vie |
|---------|------|----------------|
| `transcript.json` | Whisper, mot + `start` + `end` | 1 par video |
| `style.json` (`s1`) | police, place, taille, couleur, mouvement, glow, contour | pack, N videos |
| `proof.json` | 1 mot + s1 -> 1–3 PNG Blender | validation operateur |

Mouvement = enum uniquement : `pop-in` / `bounce` / `slide`. Pas de formule libre.

`s1` n'est pas par video. Un style valide s'applique a N transcripts.

## Commandes

```bash
# H1 preview locale
cd F07_CAPTION/PREVIEW/CODEBASE
npm ci
npm run dev

# H2 Whisper (C0 -> C1)
python3 F07_CAPTION/TRAVAIL/CODEBASE/whisper_transcribe.py \
  --input F07_CAPTION/IN \
  --out F07_CAPTION/OUT \
  --model base

# H3 proof 1 mot (Modal GPU)
modal run F07_CAPTION/TRAVAIL/CODEBASE/modal_app.py --mode proof --word HOE

# H4 calque + overlay + F05/F06 (Modal GPU)
modal run F07_CAPTION/TRAVAIL/CODEBASE/modal_app.py --mode render
```

CI : `.github/workflows/dev11_caption.yml` (`job=whisper|proof|render`).
Tests : `python3 -m pytest -q F07_CAPTION/TRAVAIL/tests`.

## Chaine

```text
IN/video
    -> Whisper GHA            -> OUT/transcript.json          (C1)
    -> PREVIEW proxy JS       -> OUT/style.json (s1)          (C2)
    -> proof 1 mot Modal      -> OUT/proof PNG                (C3)
    -> Blender calque alpha   -> overlay ffmpeg               (C4)
    -> F05 / F06 inchanges
```

## Portes

Voir `TRACKING/CAPTION_GATES.md`. Operateur : `TRACKING/GUIDE_CAPTION.md`.

## Interdits

- Live Blender pendant les sliders preview
- Coller F07 dans F03_PREVIEW / F03_PICTOR
- LUT `.cube` comme recette 3D
- Zoom / swell dans F03 ou F04 (P-ZOOM ZERO intact)
- Assets lourds dans git (IN/OUT media = artifacts / Releases)
- Token, secrets Modal, Volume Modal comme source de verite

# Guide Operateur — F07_CAPTION

> Sous-titres 3D mot-a-mot. Pas le flux PUR.
> H1–H4 poses. Operateur = portes C0–C4.

## Principe en 3 lignes

1. Whisper sort un transcript **au mot pres** (`transcript.json`).
2. La preview JS sert a regler **un** pack `s1` (police, place, taille, couleur, mouvement, glow, contour). Ce pack se rejoue sur N videos.
3. Un bouton **proof** demande a Blender 1 mot / 1–3 frames. Sans cette frame, pas de rendu video.

## Ce que tu ne fais pas

- Tu ne lances pas Blender a chaque slider.
- Tu ne melanges pas transcript et style dans un seul JSON.
- Tu ne touches pas F03 (LOOK) ni le coloring `.cube`.
- Tu ne commites pas les mp4 / PNG de preuve.

## Checklist

- Video dans `F07_CAPTION/IN/` (C0)
- Transcript `OUT/transcript.json` (C1) — Whisper GHA `job=whisper`
- `s1` exporte `OUT/style.json` (C2) — preview `npm run dev`
- Proof PNG valide visuellement (C3) — GHA `job=proof` ou bouton preview
- Puis seulement : calque alpha + overlay (C4) — GHA `job=render` → F05 → F06

## Commandes

```bash
cd F07_CAPTION/PREVIEW/CODEBASE && npm ci && npm run dev

python3 F07_CAPTION/TRAVAIL/CODEBASE/whisper_transcribe.py \
  --input F07_CAPTION/IN --out F07_CAPTION/OUT --model base

modal run F07_CAPTION/TRAVAIL/CODEBASE/modal_app.py --mode proof --word HOE
modal run F07_CAPTION/TRAVAIL/CODEBASE/modal_app.py --mode render
```

Actions → DEV11 — F07 CAPTION → `job` = whisper | proof | render.
Secrets : `MODAL_TOKEN_ID` / `MODAL_TOKEN_SECRET` (deja poses pour dev6-F).

## Preview

Coque du meme type que `F03_PREVIEW` (Vite, drop fichier, canvas 9:16, barre laterale).
Moteur CODEBASE : telecharge ailleurs — pas copie du LOOK blur/split/reframing.
Sliders = proxy layout. Glow Eevee = proof Blender uniquement.

## Proof frame

1 mot (exemple : un punch du transcript).
1 pose (taille / place de `s1`).
1–3 PNG/EXR + alpha, plaques sur un freeze de la video.
Operateur dit oui → `s1` est un pack. Operateur dit non → retour sliders, pas C4.

## s1 et N videos

Tu valides `s1` une fois. Les clips suivants ne font que fournir un autre `transcript.json`.
Oublier le nombre : le contrat est 1 style, N transcripts.

## Reprise

```bash
git clone https://github.com/jfbjfojfonf/LACRIMAE.git
cd LACRIMAE
git fetch origin --prune
git checkout dev11-F07
```

Lire `F07_CAPTION/README.md` puis `TRACKING/CAPTION_GATES.md` avant tout code.
PUR : `TRACKING/GUIDE_BRAS_ARME_PUR.md` — autre flux.

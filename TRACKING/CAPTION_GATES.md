# LACRIMAE — F07_CAPTION GATES

Portes de la frégate sous-titres 3D. **Separees de PUR_GATES.**
Le flux PUR (G0–P-ZOOM ZERO) ne change pas. F07 est optionnel.

Branche de travail : `dev11-F07` (base `dev10-v2`).

## Doctrine

```text
IN/video
        |
        v
[C0 IN]  video lisible
        |
        v
[C1 TRANSCRIPT]  Whisper GHA → transcript.json (mot + start + end)
        |
        v
[C2 PREVIEW]  proxy JS → style.json (s1)  layout seulement
        |
        v
[C3 PROOF]  1 mot, 1–3 PNG Blender reel, operateur OK
        |
        v
[C4 RENDER]  calque alpha video entiere + overlay ffmpeg
        |
        v
[F05] → [F06]  inchanges
```

Deux JSON, jamais un seul fichier mixte :

- `transcript.json` — change a chaque video
- `style.json` (`s1`) — pack rejouable sur N videos

## Gates

| Gate | Moment | Verification | Critere |
|------|--------|--------------|---------|
| **C0 IN** | Avant tout | Video cible | Fichier lisible dans `F07_CAPTION/IN/`, dimensions > 0 |
| **C1 TRANSCRIPT** | Apres Whisper | JSON mot-a-mot | `word` + `start` + `end` par cue, `start < end` |
| **C2 PREVIEW** | Apres sliders JS | Pack style | `style.json` ecrit (`s1`) : font, place, taille, couleur, mouvement enum, glow, contour |
| **C3 PROOF** | Avant rendu video | Matiere reelle | 1–3 PNG/EXR Blender (Eevee), 1 mot, operateur valide |
| **C4 RENDER** | Apres Blender full | Calque + overlay | Sequence alpha + MP4 overlay. Pas de preview CSS dans le livrable |

## Politique d'echec

- C0 echoue → pas de Whisper. Poser la video dans `IN/`.
- C1 echoue → transcript incomplet. Relancer Whisper, ne pas inventer les timings.
- C2 echoue → s1 non ecrit. Pas de job Modal.
- C3 echoue → glow / bevel / place faux. Retour PREVIEW, pas de C4.
- C4 echoue → calque ou overlay manquant. Pas de livraison F05/F06 depuis F07.

## Interdits

- Live Blender dans les sliders (proof = bouton, pas un viewport continu)
- LUT `.cube` comme recette texte 3D
- Toucher F03_PREVIEW / F03_PICTOR / P-ZOOM ZERO
- Mouvement hors enum (`pop-in` / `bounce` / `slide`)
- Volume Modal comme source de verite (GitHub detient s1 + fonts + scripts)

## Contrats

| Contrat | Chemin | Proprietaire |
|---------|--------|--------------|
| Video cible | `F07_CAPTION/IN/` | Operateur |
| Transcript mot-a-mot | `F07_CAPTION/OUT/transcript.json` | TRAVAIL Whisper |
| Pack style `s1` | `F07_CAPTION/OUT/style.json` | PREVIEW + operateur |
| Proof frame | `F07_CAPTION/OUT/` PNG/EXR | TRAVAIL Blender proof |
| Calque + overlay | `F07_CAPTION/OUT/` | TRAVAIL C4 |

## Paliers code (hors H0)

| Palier | Contenu | Statut |
|--------|---------|--------|
| H0 | dirs + docs | FAIT |
| H1 | PREVIEW coque Vite | FAIT |
| H2 | Whisper GHA | FAIT |
| H3 | proof frame Modal | FAIT |
| H4 | Blender full + overlay + F05/F06 | FAIT |

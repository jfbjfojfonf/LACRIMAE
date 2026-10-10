# LACRIMAE — TODO DE CONTINUATION

> Point d'entree obligatoire apres toute reprise.
> Derniere mise a jour : 2026-10-10.
> Branche : `dev11-F07` (base `dev10-v2`) sur `jfbjfojfonf/LACRIMAE`.
> Statut : A–G poses. H0–H4 F07_CAPTION poses.

## Etat confirme

`dev10` (cote / `dev10-v1`) etait un palimpseste : 19 workflows, moteurs
ranking/reveal/hybrid melanges au PUR, SIGNUM inutile, Heisenberg advisory
(JSON, pas un MP4). `dev10-v2` repart de zero.

Doctrine figee :

1. PERTURABO = cerveau (OU / QUOI). LACRIMAE = bras (COMMENT).
2. Pack in, MP4 out. 1 asset = 1 job.
3. Trois styles : blur, split_scene, reframing.
4. Zoom banni partout.
5. Heisenberg est une vraie frégate : il **modifie le MP4**.
6. SIGNUM n'existe pas.

## Priorites

1. **Docs** — arbre + contrats + portes. FAIT.
2. **A F05 + F06** — camouflage H.264/loudnorm + luther YouTube, `--batch`. FAIT.
3. **B F00_PUR** — yt-dlp segment, G0–G3, `pur_aggregate.py`, converter G0-S. FAIT.
4. **C BRIDGE** — fetch PUR-only, G0, convert, transit preview/PICTOR. FAIT.
5. **D F03_PREVIEW** — LOOK Vite, 3 styles, 0 zoom, overlay. FAIT.
6. **E F03_PICTOR** — miroir Remotion de la preview. FAIT.
7. **F F04_HEISENBERG** — jump cuts, SFX, B-roll, flash, punch-in-cut → MP4. FAIT.
8. **G CI** — un seul workflow `dev10_pur_render.yml`. FAIT.
9. **H0 F07_CAPTION** — arbre TRAVAIL/PREVIEW + IN/OUT + gates caption. FAIT.
10. **H1–H4 F07_CAPTION** — preview Vite, Whisper GHA, proof Modal, overlay+F05/F06. FAIT.

## Contrats a preserver

- Pack PUR : `production_pack_pur_*.json` — propriete PERTURABO. JAMAIS
  modifie cote LACRIMAE.
- Manifeste : `dev10.pur.v1` produit par le bridge.
- Parite preview/render : meme moteur LOOK en F03_PREVIEW et F03_PICTOR.
- Heisenberg consomme le MP4 PICTOR + le manifeste, ecrit un MP4.
- Assets volumineux jamais commites (CI artifacts / Releases).

## Interdits a ne pas reintroduire

- Ranking, reveal, hybrid, music timeline.
- Zoom / swell / breathing_zoom dans PICTOR ou Heisenberg.
- Heisenberg "advisory" qui ne fait que du JSON.
- F04_SIGNUM.
- Heritage `sequences.json` / fps vole / re-routage ranking.

## Palier H — F07_CAPTION (hors PUR)

Sous-titres 3D mot-a-mot. Une frégate, deux halves (TRAVAIL / PREVIEW).
`s1` = pack style rejouable. Transcript = 1 par video.

| Palier | Contenu | Statut |
|--------|---------|--------|
| H0 | dirs + README + CAPTION_GATES + GUIDE_CAPTION | FAIT |
| H1 | PREVIEW coque Vite (drop transcript + video, sliders, Save s1, couple pop-in) | FAIT |
| H2 | Whisper GHA : IN -> `transcript.json` | FAIT |
| H3 | proof frame Modal : 1 mot, 1–3 PNG | FAIT |
| H4 | Blender full + overlay ffmpeg, hook F05/F06 | FAIT |

## Prochaine etape exacte

**F07** : C0+C1 OK (Whisper run 37544539417, 133 mots). C2 OK : `s1` dans `F07_CAPTION/TRAVAIL/CODEBASE/styles/s1.json` (`motion_speed: 1.95`, pop-in). Prochaine etape = C3 proof (1 mot, 1–3 PNG Blender), sans lancer le run tant que l'operateur n'a pas dit go. Puis C4 render. Corriger la fregate fautive, pas le pack `s1`.

**PUR** (inchange) : premier E2E CI (`dev10_pur_render.yml`) avec un pack
PERTURABO joignable. Si le run E2E casse : corriger la frégate fautive,
pas le pack.

## Reprise sandbox

```bash
git clone https://github.com/jfbjfojfonf/LACRIMAE.git
cd LACRIMAE
git fetch origin --prune
git checkout dev11-F07
```

Lire ce fichier, `TRACKING/PUR_GATES.md` (flux PUR) et
`TRACKING/CAPTION_GATES.md` (F07) avant tout code.

# LACRIMAE dev10-v2 — TODO DE CONTINUATION

> Point d'entree obligatoire apres toute reprise.
> Derniere mise a jour : 2026-10-05.
> Branche : `dev10-v2` sur `jfbjfojfonf/LACRIMAE`.
> Statut : A–D poses (F05/F06, F00_PUR, Bridge, Preview LOOK). E/F/G a venir.

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
6. **E F03_PICTOR** — miroir Remotion de la preview. PAS COMMENCE.
7. **F F04_HEISENBERG** — jump cuts, SFX, B-roll, flash, punch-in-cut → MP4. PAS COMMENCE.
8. **G CI** — un seul workflow `dev10_pur_render.yml`. PAS COMMENCE.

Chaque etape = GO Warsmith separe. Pas d'implementation sans GO.

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

## Prochaine etape exacte

A–D poses localement. Commit + push `dev10-v2` puis, dans cet ordre :

1. E F03_PICTOR (miroir preview, LOOK, 0 zoom)
2. F F04_HEISENBERG (execution temporelle → MP4 reel)
3. G workflow unique `dev10_pur_render.yml` + agregeur strict

## Reprise sandbox

```bash
git clone https://github.com/jfbjfojfonf/LACRIMAE.git
cd LACRIMAE
git fetch origin --prune
git checkout dev10-v2
```

Lire ce fichier puis `TRACKING/PUR_GATES.md` avant tout code.

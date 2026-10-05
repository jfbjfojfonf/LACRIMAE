# LACRIMAE dev10-v2 — TODO DE CONTINUATION

> Point d'entree obligatoire apres toute reprise.
> Derniere mise a jour : 2026-10-05.
> Branche : `dev10-v2` sur `jfbjfojfonf/LACRIMAE`.
> Statut : squelette documentaire. Aucun code de frégate.

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

1. **Docs** (cette livraison) — arbre + contrats + portes. FAIT.
2. **BRIDGE + F00_PUR** — fetch pack, G0–G3, segment VOD. PAS COMMENCE.
3. **F03_PREVIEW + F03_PICTOR** — moteur unique, look only, parite
   preview/render. PAS COMMENCE.
4. **F04_HEISENBERG** — jump cuts, SFX, B-roll, flash, punch-in-cut.
   Sort un MP4 reel. PAS COMMENCE.
5. **F05 + F06** — camouflage puis luther. PAS COMMENCE.
6. **CI** — un seul workflow `dev10_pur_render.yml`. PAS COMMENCE.

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

Attendre GO Warsmith pour l'implementation, dans cet ordre :

1. BRIDGE_PERTURABO (conversion pack → manifeste)
2. F00_PUR (segment VOD + gates G0–G3)
3. F03_PREVIEW (3 styles, overlay, 0 zoom)
4. F03_PICTOR (miroir preview)
5. F04_HEISENBERG (execution temporelle → MP4)
6. F05 puis F06
7. Workflow unique + agregeur strict

## Reprise sandbox

```bash
git clone https://github.com/jfbjfojfonf/LACRIMAE.git
cd LACRIMAE
git fetch origin --prune
git checkout dev10-v2
```

Lire ce fichier puis `TRACKING/PUR_GATES.md` avant tout code.

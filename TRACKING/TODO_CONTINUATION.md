# LACRIMAE dev10 — TODO DE CONTINUATION

> Point d'entrée obligatoire après toute migration de sandbox.
> Dernière mise à jour : 2026-09-10.

## État confirmé

Le dépôt est `https://github.com/kioka8877-ux/LACRIMAE`, branche `dev10`
(commit de référence `ba979c2` — 2026-09-11, fix agrégateur). dev10 est canonisé **bras armé du mode PUR**
de PERTURABO (`kioka8877-ux/PERTURABO`, `MONDES_FORGES/CLIPPING`) : le pack
PUR entre, le MP4 final sort, 100 % GitHub Actions.

Travail PUR réalisé sur la branche de travail `dev10-pur` (commits
`42a9ebc`, `61b719f` + lot 3) : BridgeClipper v2, F00-PUR ingest, onglet
PUR F03, rendu F04 parité, workflow `dev10_pur_render.yml`, bridge `--pur`,
docs (PUR_GATES / PUR_CAMPAIGN_LOG / PUR_IMPLEMENTATION / guide opérateur).

## Priorités canoniques

1. **Mode PUR — bras armé PERTURABO** (unique mission de dev10) :
   `F00-PUR → bridge --pur → F03 Preview ⚡ PUR → dev10_pur_render.yml`
2. **F00H (hook 2 s)** : implémenté, test réel REPORTÉ — non prioritaire.
   Reprendre via `TRACKING/F00H_GATES.md` quand décidé.
3. **Test réel Ranking dev9** : hérité de dev9, non exécuté. Non bloquant
   pour PUR — ne pas mélanger les assets.

## Prochaine étape exacte (PUR)

Le preview dispose des **panneaux de configuration opérateur** (texte
overlay, style blur/split/reframing, anti-détection) — voir
`TRACKING/GUIDE_BRAS_ARME_PUR.md` étape 3. État :

1. ✅ Clip pur_A01 réparé (la copie .mp4 était tronquée — moov atom absent)
2. ✅ Panneaux F03 branchés sur `style_params` (dev10.pur.v1) + rendu par
   style (blur dual-layer / split top-bas / reframing) + miroir F04 synchronisé
3. ✅ **Texte overlay v2 IMPLÉMENTÉ (2026-09-10)** — phases A-E de
   `TRACKING/PUR_TEXT_IMPLEMENTATION.md` : texte statique début→fin, auto-fit
   (1 ligne = 1 ligne visuelle, max 3, min 28 px), boîte coins arrondis +
   padding, preset « Référence TikTok » (boîte blanche, texte noir,
   Montserrat, casse mixte), curseur position verticale de la vidéo nette
   (blur). Boutons +/− lignes dans le panneau. Miroir F04 synchronisé.
4. ✅ **Codex de base PUR propre (2026-09-10)** : `public/codex.json`
   régénéré (racine pur_pack, manifeste = réglages opérateur validés,
   archive Spider-Man dans clips[0]) + exportCodex corrigé (review_mode
   racine synchronisé, pur_manifest racine rempli) + Montserrat ExtraBold
   embarquée F03/F04 (parité police preview/CI).
5. ✅ **Architecture MULTI-VIDÉOS IMPLÉMENTÉE (2026-09-10)** — voir
   `TRACKING/PUR_MULTI_VIDEOS.md` : 1 codex = N vidéos = 1 run = 1 zip.
   Chargeur multi-packs F03 (sélection multiple), `parsePurPackMulti`
   (style + texte GLOBAUX appliqués à toutes les vidéos), sélecteur ◀▶
   « VIDÉO X/N », workflow matrix (prepare → N renders parallèles 1-20 →
   aggregate strict), `tools/pur_aggregate.py` (refus de publier si un MP4
   manque), `convert_pur_pack.mjs --packs`, F05 `--batch`.
6. ✅ **Fix agrégateur (2026-09-11, commit `ba979c2`)** — le rendu matrix
   A01 réussissait (run 34575463702) mais l'agrégat refusait le bundle :
   identifiants d'entrée déjà préfixés (`pur_A01`) re-préfixés →
   `pur_pur_a01_finale.mp4` introuvable. `normalize_angle()` + 7 tests
   (`F00_INGEST/tests/test_pur_aggregate.py`). Doctrine de refus INTACTE.
   Récit complet des 2 runs du 11/09 : `TRACKING/PUR_CAMPAIGN_LOG.md`.
7. **Validation visuelle P1** par le Warsmith sur le preview — GO obligatoire
   avant tout run CI (règle du 2026-09-09)
8. ✅ E2E PUR réel post-fix RÉALISÉ (11/09) : run 34605484040 (jobs verts
   mais P2 échouée : fps écrasé par sequences.json hérité dev7 → 14,36 s),
   puis run 34616549605 après fix fps (`727b131` — Root.jsx voie PUR lit le
   fps du manifeste dev10.pur.v1) → **28,629 s mesurées, BUNDLE COMPLET
   1/1, P2 techniquement validée**. Récit : PUR_CAMPAIGN_LOG.md.
9. **Contrôle visuel du MP4 A01 (28,6 s)** par le Warsmith — artefact
   `lac-pur-final` du run 34616549605 : hook à 0 s, zoom 8,62 s, fade final,
   texte lisible, aucune accélération perceptible.
10. Tag canonique à la validation : pur-canon-v1

## Contrats à préserver

- Pack PUR : `production_pack_pur_*.json` — propriété PERTURABO F06_DIRECTOR.
  JAMAIS modifié côté dev10 ; corrections à remonter au monde forge.
- Manifeste : `dev10.pur.v1` produit par `parsePurPack()` (bridgeClipper.js).
- Parité preview/render : `_purPackComposition.jsx` identique en F03 et F04.
- Anti-détection obligatoire (mirror + speed + zoom) — doctrine
  `_PIEGES_APPRIS_PUR.md` de PERTURABO.

## Règles de reprise

Vérifier `git status --short --branch`, lire ce fichier et
`TRACKING/PUR_IMPLEMENTATION.md`. Chaque gate journalisé avec son commit /
run CI / artifact. Ne pas lancer F04 avant validation visuelle F03.
Les assets volumineux (clips téléchargés) ne sont JAMAIS commités : ils
transitent par les artefacts CI ou les Releases GitHub (SHA-256 si besoin).

## Migration sandbox

```bash
git clone https://github.com/kioka8877-ux/LACRIMAE.git
cd LACRIMAE
git fetch origin --prune
git checkout dev10            # ou dev10-pur pour le travail PUR
cat TRACKING/TODO_CONTINUATION.md
```

## Mise à jour 2026-09-11 (après-midi) — moteur unique posé

- ✅ Cause racine identifiée : re-routage ranking (`buildRankingFromPur`) qui masquait
  le moteur PUR en CI — supprimé (commit `4f1598ce`).
- ✅ PICTOR rend désormais avec le composant preview validé (voix ON, mapping boom→impact
  provisoire, portes assets `sfx_available` + P-AUD).
- ⏭ Prochaine étape : run A01 post-moteur-unique (GO Warsmith) → contrôle visuel
  (blur/zooms/SFX/voix) → tag `pur-canon-v1`.
- ⏭ En attente du Warsmith : fichier `boom.mp3` (pour lever le mapping provisoire) ;
  purge éventuelle du codex preview (héritages dev4/dev9).

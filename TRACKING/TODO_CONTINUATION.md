# LACRIMAE dev10 — TODO DE CONTINUATION

> Point d'entrée obligatoire après toute migration de sandbox.
> Dernière mise à jour : 2026-09-10.

## État confirmé

Le dépôt est `https://github.com/kioka8877-ux/LACRIMAE`, branche `dev10`
(commit de référence `704800b`). dev10 est canonisé **bras armé du mode PUR**
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
3. 📋 **NOUVEAU — Texte overlay v2 (plan dans
   `TRACKING/PUR_TEXT_IMPLEMENTATION.md`, décision Warsmith 2026-09-10)** :
   règle « pas de texte pendant le hook » ABROGÉE → texte statique du début
   à la fin, auto-fit 1 ligne = 1 ligne visuelle (max 3 lignes), boîte
   blanche coins arrondis façon référence TikTok (capture Aishah Sofey),
   casse mixte, police embarquée, curseur position verticale de la vidéo
   nette (blur). À implémenter (phases A-E du plan).
4. **Validation visuelle P1** par le Warsmith sur le preview — GO obligatoire
   avant tout run CI (règle du 2026-09-09)
5. Puis E2E PUR réel : GitHub Actions → "DEV10 PUR — Bras armé PERTURABO"
   (workflow_dispatch, inputs : pack_filter=pur_A01, canvas=9:16), vérifier
   G0-G3 + P2, contrôle visuel MP4, journaliser dans PUR_CAMPAIGN_LOG.md
6. Tag canonique à la validation : pur-canon-v1

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

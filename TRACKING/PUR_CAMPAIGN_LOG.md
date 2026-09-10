# LACRIMAE dev10 — JOURNAL DE CAMPAGNES PUR

| Date | Pack | Angle | Segment (s) | Canvas | Gates G0-G3 | P1 Preview | P2 Rendu | Run CI | Décision |
|---|---|---|---|---|---|---|---|---|---|
| 2026-09-09 | pur-A01 | A01 | 737.48 → 767.48 | 9:16 | G0 ✓ G1 ✓ G2 ✓ G3 ✓ (automatiques, script) | ❌ NON VALIDÉE | ⚠️ brouillon technique — lac_pur_final.mp4 12.6 Mo, 857/857 frames | [34340044745](https://github.com/kioka8877-ux/LACRIMAE/actions/runs/34340044745) | **TEST TECHNIQUE LANCÉ SANS AUTORISATION OPÉRATEUR — NON VALIDÉ.** Artefact à considérer comme brouillon jusqu'à visualisation et décision du Warsmith |
| — | — | — | — | — | — | — | — | — | — |

### Journal technique (2026-09-10)

- **Fix récupération clips (`f00_pur.py`)** : `find_downloaded_file()` ne
  considère plus que le fichier au stem exact téléchargé + purge des
  fichiers périmés au même stem avant chaque G1 (bug du 2026-09-10 :
  `reveal_02.mp4` périmé retenu à la place du segment frais ; ancien
  `pur_A01.mp4` de 4-6 s faisant échouer G2).
- **Fix clip tronqué** : `pur_A01.mp4` (2,88 Mo) était une copie interrompue
  (moov atom absent → vidéo invisible en preview) ; re-copié depuis le fichier
  complet `pur_A01` (5,33 Mo, h264 1920×1080 30,2 s @60fps).
- **Panneaux de configuration F03 (style_params)** : nouveau bloc
  `style_params` dans `dev10.pur.v1` (racine = réglages du style,
  `narrative.overlay.style_params` = réglages du texte). Panneaux éditeur :
  🎨 TEXTE OVERLAY (couleurs par ligne, police, fond case à cocher + couleur
  + opacité, contour couleur + épaisseur, taille, position X/Y), 🌫️ BLUR
  (degré, tailles fond/devant), ✂️ SPLIT (taille vidéo HAUT, taille élément
  BAS, taille/position du texte), 🎯 REFRAMING (échelle, décalage X/Y),
  🛡️ ANTI-DÉTECTION (miroir, vitesse, zoom respiration, crop).
- **Rendu par style** : `_purPackComposition.jsx` implémente les 4 mises en
  page (blur dual-layer, split top/bottom, reframing scale+offset, fullscreen)
  — miroir F04 synchronisé (`purPackCompilation.js` + `_purPackComposition.jsx`).
  Les réglages opérateur survivent à la reconversion d'un pack.

### Historique des runs CI (2026-09-09)

| Run | Résultat | Cause échec / note |
|---|---|---|
| [34338334121](https://github.com/kioka8877-ux/LACRIMAE/actions/runs/34338334121) | ❌ failure | codex injecté dans public/ au lieu de src/data/ → rendu sur route reveal (404 reveal_01.mp4). Fix a6b07f8 |
| [34339647085](https://github.com/kioka8877-ux/LACRIMAE/actions/runs/34339647085) | ❌ failure | codex.json committé avec clips[] vide → IndexError injection. Fix 4c7e524 |
| [34340044745](https://github.com/kioka8877-ux/LACRIMAE/actions/runs/34340044745) | ✅ success (technique) | Pack pur_A01 → yt-dlp → BridgeClipper → Remotion → 12.6 Mo. **⚠️ Déclenché par l'agent sans GO explicite de l'opérateur — procédure à ne pas reproduire : tout run CI réel exige l'autorisation préalable du Warsmith** |

Fixes notés pendant la mise en service : input `canvas` en string (le type choice avec « : » bloque le dispatch API), SFX désactivés par défaut (`sfx_available`, fichiers sfx/*.mp3 pas encore embarqués).

### Décisions Warsmith (2026-09-10) — texte overlay v2

- **ABROGATION** de la règle « jamais de texte pendant le hook 0-3 s » :
  le texte overlay sera statique du début à la fin, au même endroit
  (référence visuelle : capture TikTok Aishah Sofey — boîte blanche, 3
  lignes, casse mixte). Plan d'implémentation :
  `TRACKING/PUR_TEXT_IMPLEMENTATION.md` (phases A-E, non implémenté à ce
  jour — constat du bug « 6 lignes » : débordement des 2 lignes du pack à
  taille fixe). La position de la vidéo nette (blur) sera un curseur
  opérateur, pas un placement automatique.

### Implémentation texte v2 (2026-09-10) — FAIT

Phases A-E de `PUR_TEXT_IMPLEMENTATION.md` livrées :
- Texte statique début→fin (plus de hook sans texte, plus de pop_in)
- Auto-fit : 1 ligne = 1 ligne visuelle (mesure Canvas côté preview, ratio
  0.62 conservateur côté rendu Node), max 3 lignes, min 28 px
- Boîte coins arrondis + padding réglables ; preset « Référence TikTok »
  (boîte blanche, texte noir, Montserrat, size 44, sans contour)
- Casse mixte par défaut (toggle MAJUSCULES)
- Blur : curseur position verticale de la vidéo nette (fg_y_pct)
- pur_manifest.json régénéré avec le preset TikTok appliqué
- Miroir F04 synchronisé (purPackCompilation.js + _purPackComposition.jsx)

### Fix codex de base (2026-09-10) — FAIT

- `exportCodex` corrigé : review_mode racine toujours synchronisé avec le
  mode actif (pur_pack inclus), pur_manifest racine rempli, session de
  clips[0] cohérente avec la racine, clips[] ne perd plus rien si vide.
- `public/codex.json` régénéré : base PUR propre = réglages opérateur
  validés (size 39, Y 14, padding 25, blur fg 49 % @ 54 %) ; les anciens
  blocs Spider-Man ranking archivés dans clips[0].ranking_manifest.
- Police Montserrat ExtraBold embarquée (OFL, JulietaUla) :
  `public/fonts/Montserrat-ExtraBold.ttf` dans F03 et F04 + loader
  `ensurePurFont()` — parité preview/rendu au pixel.
- Le codex de base sert de référence aux prochaines vidéos PUR.

## Règle d'exploitation (ajoutée après incident du 2026-09-09)

**Aucun run CI réel (dispatch, render, consommation de minutes Actions) ne doit être
déclenché sans le GO explicite de l'opérateur.** Les gates G0-G3 sont des contrôles
automatiques de code : elles ne valident rien de créatif. La validation P1 (preview),
le rendu P2 en conditions réelles et la décision finale appartiennent au Warsmith seul.

## Règle de comparaison

Conserver toujours l'overlay du pack (copywriting.overlay_title) à côté du rendu.
Les frames de contrôle attendues : 0 s (hook pur, visage), 2.9 s (fin du hook),
3.1 s (overlay visible), un zoom frame-exact (ex. 8.62 s pour A01), dernière
seconde (fade_to_black).

## Colonnes minimales

Chaque ligne doit renseigner : pack, angle, segment, canvas, gates G0-G3,
P1 (preview validée), P2 (rendu CI), run GitHub Actions, décision.

# PUR — IMPLÉMENTATION TEXTE OVERLAY (statique, auto-fit, boîte blanche)

> Décision Warsmith du 2026-09-10. RÉFÉRENCE VISUELLE : capture TikTok
> « Aishah Sofey » — vidéo 9:16, texte en boîte blanche à coins arrondis,
> texte noir gras, 3 lignes, collé en haut au centre, **statique du début à
> la fin**, vidéo nette positionnée juste sous le texte.
> **IMPLÉMENTÉ le 2026-09-10** (phases A-E). Le preview affiche le texte
> statique avec auto-fit ; le preset « Référence TikTok » est disponible.

---

## Décisions opérateur (verrouillées)

1. **Règle « pas de texte pendant le hook 0-3 s » ABROGÉE.** Le texte est
   présent dès la frame 0, immobile, au même endroit, jusqu'à la fin de la
   vidéo. Plus aucune animation d'apparition (pop_in supprimé).
2. **Position de la vidéo nette (style blur)** : réglée par l'opérateur
   (panneau BLUR — curseur position verticale), pas de placement automatique.
3. **Lignes** : l'opérateur veut ses lignes telles quelles — 2 à 3 lignes
   éditables dans le panneau (ajout/suppression manuelle). PAS de découpage
   automatique du texte : ce que l'opérateur tape = ce qui s'affiche.
4. **Casse** : comme la référence — casse mixte conservée, plus de
   `text-transform: uppercase` forcé.

---

## État actuel (constat du bug « 6 lignes »)

Le pack contient 2 lignes mais à `font_size: 68` fixe avec `maxWidth: 88%`,
chaque ligne déborde et se replie sur 2-4 lignes visuelles → 6 lignes
affichées au lieu de 2. Aucune contrainte de largeur par ligne, aucune
gestion du nombre de lignes.

---

## Plan d'implémentation

### PHASE A — Texte statique (comportement)
1. `_purPackComposition.jsx` (F03 + miroir F04) : supprimer `popScale`,
   `popProgress`, l'animation pop_in — texte rendu dès `frame >= 0`,
   position fixe pour toute la durée.
2. `visible_from_frame` ignoré (gardé dans le manifeste pour rétro-compat).
   ✅ FAIT — F03 `_purPackComposition.jsx` + miroir F04 synchronisés.
3. Défauts `PUR_OVERLAY_DEFAULTS` : `visible_from_frame: 0`, nouveau champ
   `static: true`, `uppercase: false`.

### PHASE B — Auto-fit par ligne (anti-débordement)
1. Mesure de la largeur réelle de chaque ligne (canvas 2D ou `MeasuredText`)
   → réduction proportionnelle de la taille si la ligne dépasse la largeur
   utile (92 % du canvas), minimum lisible 28 px.
2. Le curseur taille du panneau reste la taille de base ; l'auto-fit ne fait
   que DESCENDRE la taille des lignes trop longues (jamais agrandir).
3. Max 3 lignes affichées — le panneau refuse la 4e.

### PHASE C — Boîte style référence TikTok
1. Nouveaux champs overlay : `box_radius` (coins arrondis, défaut 10),
   `box_padding` (défaut 10/16), le fond existant (`bg_enabled`, `bg_color`,
   `bg_opacity`) alimente la boîte.
2. Preset « RÉFÉRENCE TIKTOK » (bouton du panneau) : boîte blanche opaque,
   texte noir, coins 10, sans contour, Montserrat ExtraBold — applique les
   valeurs en un clic.
3. Police embarquée dans le repo (`public/fonts/` — Montserrat ExtraBold,
   ~50 Ko, licence OFL) chargée via `@font-face` + `staticFile` pour parité
   preview/rendu CI exacte.

### PHASE D — Panneaux F03 (édition)
1. Panneau TEXTE OVERLAY : boutons « + ligne » / « − ligne » (2-3 lignes),
   toggle MAJUSCULES on/off (défaut off), toggle « texte statique » (défaut
   on, présent du début à la fin).
2. Panneau BLUR : ajout curseur « position verticale de la vidéo nette »
   (0-100 %, opérateur decide le placement).
3. Toggle « casse mixte » (défaut) / « MAJUSCULES ».

### PHASE E — Parité F04 + docs
1. Miroir `_purPackComposition.jsx` F03_PICTOR synchronisé (mêmes valeurs).
2. Nouveaux champs dans `PUR_STYLE_PARAMS_DEFAULTS` / `PUR_OVERLAY_DEFAULTS`
   (bridgeClipper.js F03 ↔ purPackCompilation.js F04).
3. pur_manifest.json régénéré avec les nouveaux défauts + preset TikTok
   appliqué par défaut (boîte blanche, casse mixte, Montserrat, size 44).
4. Vérification : build Vite OK, preview visuel, frames de contrôle
   (0 s = texte présent, milieu = même position, fin = identique).

---

## Contrats préservés

- Pack PERTURABO jamais modifié — tous les réglages dans `style_params`.
- Parité F03/F04 par construction (même manifeste consommé).
- Anti-détection inchangée (mirror, speed, breathing, crop).

## Critère de validation (gate P1)

- Texte visible dès la frame 0, identique à la frame finale.
- Chaque ligne = 1 ligne visuelle (auto-fit), max 3 lignes.
- Boîte blanche coins arrondis optionnelle (preset référence).
- Casse mixte par défaut.

# NOTE À PERTURABO — 2026-09-12 (décisions Warsmith, run 34686817585)

> **Vocabulaire officiel** : un **asset** = A01, A02, A03… = 1 vidéo finale = 1 job runner.
> Le **pack** = l'ensemble des assets. Ne plus appeler « pack » un asset.
> Nommage recommandé des fichiers : `asset_pur_A01.json` (au lieu de `production_pack_pur_A01.json`).

## 1. speed (prioritaire — « l'accélération ne doit pas être perceptible pour un humain »)

Actuel : `anti_detection.speed = 1.05` → audible sur une voix parlée.
Cible : **1.01 – 1.02** (imperceptible pour un humain, toujours détectable par les robots YouTube).
Option : valeur légèrement aléatoire par vidéo (1.01 → 1.02) pour varier les empreintes.

## 2. Schéma des zooms → remplacé par le SWELL CONTINU (pas un zoom)

Décision Warsmith : le clip **grossit doucement** puis **revient tout seul à sa valeur normale**
en une seule courbe continue (montée douce → tenue légère → redescente douce).
PAS de cut, PAS de retour instantané — l'œil voit une respiration, jamais un zoom.

Champs attendus par le moteur (tous optionnels, défauts côté LACRIMAE) :

| Champ | Type | Défaut | Rôle |
|---|---|---|---|
| `moment_frame` | int | 0 | frame de départ du swell |
| `frames` | int | 3 | montée (attack) en frames |
| `hold_frames` | int | 0 | tenue au sommet |
| `release_frames` | int | 1.5 × attack | redescente douce vers 1.0 |
| `scale_from` | float | 1.0 | échelle de départ |
| `scale_to` | float | 1.06 | amplitude max (faible — respiration) |

Exemple : `{"moment_frame": 90, "frames": 12, "hold_frames": 4, "release_frames": 18, "scale_to": 1.05}`

## 3. Transitions = FLASH BLANC (décision Warsmith)

La transition officielle est un **flash blanc** aux frontières de segments.
Déclencheur par asset : `"white_flash": true` sur l'entrée de zoom du moment concerné.

| Champ | Type | Défaut | Rôle |
|---|---|---|---|
| `white_flash` | bool | false | active le flash sur ce moment |
| `frames` | int | 5 | durée totale (montée + descente symétriques) |
| `flash_opacity` | float | 1.0 | opacité du pic |

## 4. Rappel pipeline (confirmé côté LACRIMAE)

Run **sans filtre** = **tous les assets** en parallèle (matrix GitHub, jusqu'à 20 runners),
1 MP4 par asset, agrégation stricte : le zip final est refusé si un seul rendu manque.
Dernier run vert : [34686817585](https://github.com/jfbjfojfonf/LACRIMAE/actions/runs/34686817585) — pur_A01, 28,6 s, 19,3 Mo.

---

## Addendum (2026-09-12, après run 34721632577)

**Résultat tous assets** : A01 ✓, A02 ✓, A03 ✗ (G2 DUREE : 31.35s ≠ 30.0s ±0.5 —
dérive de fragments HLS Twitch malgré `--force-keyframes-at-cuts`).
L'agrégation stricte a refusé de publier un bundle incomplet → **règle respectée, aucun zip sorti**.

**Speed 1.05 maintenu par décision de l'opérateur** (2026-09-12) : le garde-fou G0
continue de signaler tout speed > 1.03, mais aucune correction n'est appliquée côté
moteur tant que PERTURABO n'a pas tranché. À revoir ici le jour où la valeur change.

**Côté LACRIMAE (déjà appliqué)** : G2 re-découpe localement (ffmpeg re-encode,
fenêtre ≤ +3 s) quand la durée dérape — la loterie aux keyframes ne peut plus tuer un job.

---

## Addendum 2 (2026-09-12, nuit — post run 34724140887)

**Speed 1.05 n'etait PAS la cause de l'acceleration percue.** Le vrai coupable était
côté LACRIMAE : `startFrom = localFrame * speed` doublait l'avance du clip (~2,1x).
Fix posé (`startFrom: 0`). La vitesse de lecture reste celle que tu as choisie.

**Breathing_zoom : template cachée.** Tes packs activent `breathing_zoom`
(1.02 <-> 1.08, cycle 8 s) dans l'anti_detection — découvert seulement au scan des
MP4 du run. LACRIMAE l'ignore désormais quand `fx_mode=off` (interrupteur workflow).
Si tu veux le garder pour PERTURABO, rends-le optionnel/doux ou documente-le dans les
packs : l'opérateur ne doit pas découvrir un effet par hasard.

**Aucun asset modifié** : les interrupteurs vivent dans le workflow LACRIMAE
(`fx_mode`, `mute_bg`). Les packs continuent de porter speed/crop/mirror/zooms.

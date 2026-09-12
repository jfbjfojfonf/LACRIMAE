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

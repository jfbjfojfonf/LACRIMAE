# 04 — Spécification du script JSX (application de `cc2.ffx`)

> **Statut : spécification uniquement.** Le script sera écrit en **Phase 1**,
> après validation de ce document. Rien n'est encore codé.

## Objectif

Appliquer le preset **`cc2.ffx`** sur le calque vidéo **à chaque job**, sans avoir à le
figer dans le template `.aep`. Le script s'exécute dans After Effects **avant le rendu**,
piloté par Nexrender (asset de type `script`).

## Pourquoi passer par un script

- Le `.aep` reste **propre et générique** (une comp + un calque `SRC`).
- Le preset est appliqué **à la volée** : on peut changer de preset sans rouvrir AE.
- Un seul template sert tous les jobs.

## Comportement attendu

1. Se localiser sur le calque vidéo nommé `SRC` dans la composition active.
2. Charger le fichier `cc2.ffx` depuis un chemin fixe sur le VPS
   (ex. `C:\nexrender\presets\cc2.ffx` — le `.ffx` reste sur le VPS, jamais committé).
3. Appliquer le preset sur le calque (`applyPreset`).
4. **Vérifications de robustesse** :
   - si le calque `SRC` est introuvable → erreur explicite (pas de rendu à l'aveugle) ;
   - si un effet du preset est absent (plugin non installé) → warning logué ;
   - jamais de popup : le script doit tourner silencieusement en mode `aerender`.
5. Termine proprement (pas de `confirm()`, pas de `alert()` — ils bloqueraient le rendu).

## Contraintes Nexrender

- Sur **notre VPS (self-hosted)** : aucun problème, les scripts sont libres.
- Sur Nexrender Cloud : les scripts doivent être pré-approuvés par le support —
  une raison de plus de rester en self-hosted.

## Décisions à valider avant Phase 1

1. Chemin canonique du `.ffx` sur le VPS (`C:\nexrender\presets\cc2.ffx` proposé).
2. Nom du calque (`SRC` proposé).
3. Que faire si un plugin est manquant : **échec du job** ou **rendu avec warning** ?

# 04 — Script JSX (application de `cc2.ffx`)

> **Statut : implémenté.** Fichier : `../scripts/apply_cc2.jsx`.

## Objectif

Appliquer `cc2.ffx` sur le calque `SRC` à chaque job, sans figer le preset dans le `.aep`.

## Comportement

1. Supprime les dialogs AE (`beginSuppressDialogs`).
2. Trouve le calque `SRC` (comp active, sinon premiere CompItem).
3. Charge `C:\nexrender\presets\cc2.ffx`.
4. `layer.applyPreset`.
5. Echec explicite si calque, preset ou plugin manquant (`missing_plugin_policy: fail_job`).
6. Jamais d'`alert()` / `confirm()`.

A copier sur le VPS vers `C:\nexrender\scripts\apply_cc2.jsx`.

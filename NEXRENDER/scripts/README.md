# NEXRENDER/scripts/

Script JSX qui applique `cc2.ffx` a la volee.

**Statut** : `apply_cc2.jsx` ecrit.

Regles :
- jamais de `.ffx` dans ce dossier (le preset reste sur le VPS,
  `C:\nexrender\presets\cc2.ffx`) ;
- pas d'`alert()` / `confirm()` : ca bloquerait `aerender`.

Comportement :
1. Trouve le calque `SRC`.
2. Applique `C:\nexrender\presets\cc2.ffx`.
3. Echec explicite si calque, preset ou plugin manquant.

A copier sur le VPS vers `C:\nexrender\scripts\apply_cc2.jsx`.

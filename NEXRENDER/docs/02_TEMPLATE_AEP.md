# 02 — Créer le template `.aep` SUR LE VPS

> **Pourquoi sur le VPS ?** Le PC local est trop faible pour installer After Effects.
> Le VPS a 64 Go de RAM : on crée le template là-bas, en RDP. Aucun AE sur le PC.

## Prérequis

- Phase 2 terminée (AE installé et fonctionnel sur le VPS).
- Connexion RDP ouverte.

## Étapes

1. **Ouvrir After Effects** sur le VPS (via RDP).
2. **Créer une composition** :
   - Résolution : **1920 × 1080**
   - FPS : identique à tes sources (ex. 120 ou 60)
   - Durée : couvrant la vidéo la plus longue à traiter
3. **Ajouter un calque vidéo placeholder** :
   - Nom du calque : **`SRC`** (figé Phase 1a)
   - Nom de la composition : **`MAIN`**
   - Le preset `cc2.ffx` ne PAS encore appliqué ici : c'est le script JSX
     (`04_SCRIPT_JSX.md`) qui l'appliquera à chaque job.
4. **Configurer l'Output Module (OBLIGATOIRE pour AE 2023+)** :
   - Fenêtre Render Queue → cliquer sur le nom du Output Module
   - Format : **H.264** (ou AVI/QuickTime si on veut un master non compressé)
   - Sortie : fichier, chemin de destination sur le VPS
   - Sans ça, `aerender` ne rend **rien** sans erreur explicite (cf. `05_DEPANNAGE.md`).
5. **Enregistrer le projet** :
   - Chemin canonique sur le VPS : `C:\nexrender\templates\template.aep`
   - Ce fichier **ne sera jamais committé** (règle `.gitignore` : `*.aep`).

## Validation de la phase

- [ ] Composition 1920×1080 créée
- [ ] Calque nommé exactement comme convenu
- [ ] Output Module configuré et testé (un rendu manuel via la Render Queue réussit)
- [ ] `.aep` sauvegardé dans `C:\nexrender\templates\`
- [ ] La vidéo déposée sur le calque placeholder lit correctement

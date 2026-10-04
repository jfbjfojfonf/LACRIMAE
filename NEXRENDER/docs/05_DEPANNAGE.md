# 05 — Dépannage des rendus Nexrender

> Erreurs fréquentes et solutions. À enrichir au fil des tests (Phase 4+).

## 1. Le rendu ne produit rien / composition absente

**Cause** : Output Module non configuré dans le template (exigence AE 2023+).
**Fix** : rouvrir le `.aep` → Render Queue → Output Module → configurer le format
(cf. `02_TEMPLATE_AEP.md`).

## 2. `aerender` bloque indéfiniment puis timeout

**Cause la plus fréquente** : une **fenêtre popup** en arrière-plan que personne ne clique.
- Pop-up de licence d'un plugin cracké / non licencié
- Pop-up « Sauvegarder avant de quitter »
- Fenêtre de bienvenue ou mise à jour d'AE au premier lancement

**Fix** :
1. Se connecter en RDP, lancer AE normalement, fermer toutes les pop-ups de premier
   lancement, puis relancer le job.
2. Vérifier que **tous** les plugins du preset sont installés et licenciés.
3. Aucune version crackée — c'est la cause n°1 de ce type de blocage.

## 3. Effet « Missing » dans le rendu (look incorrect)

**Cause** : un plugin du preset (`cc2.ffx`) n'est pas installé sur le VPS
(Magic Bullet Looks, Sapphire/S_Gradient).
**Fix** : installer les plugins manquants ; comparer le rendu avec un rendu de référence
fait sous AE.

## 4. `nexrender-server` ne reçoit pas les jobs

**Check-list** :
- Le serveur tourne-t-il ? (processus Node présent)
- Le port est-il ouvert en local ?
- Le worker est-il lancé **aussi** (server reçoit, worker exécute) ?
- Le job pointe-t-il vers le bon chemin de template (chemin Windows absolu) ?

## 5. « Asset not found » / vidéo introuvable

**Cause** : le `src` du job ne pointe pas vers un fichier existant sur le VPS.
**Fix** : vérifier le chemin exact (sens des `\`, majuscules Windows), déposer la vidéo
dans `C:\nexrender\inbox\` avant de lancer.

## 6. Rendu OK mais qualité dégradée / compression

**Cause** : paramètres d'encodage du Output Module (débit trop faible, pas de contrôle qualité).
**Fix** : revoir `03_JOB.md` — décider du master (AVI/QuickTime) puis de l'encodage final.

## 7. Le VPS s'arrête en plein rendu

**Cause** : crédit d'essai épuisé (100 $ / 30 jours) ou Power Off manuel.
**Fix** : vérifier la consommation sur le tableau de bord Kamatera ; couper le VPS
entre les sessions de rendu, jamais pendant.

## Journal des incidents

| Date | Phase | Symptôme | Cause | Fix |
|---|---|---|---|---|
| — | — | *(à compléter en Phase 4)* | — | — |

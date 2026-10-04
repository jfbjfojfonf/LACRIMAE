# NEXRENDER/jobs/

Les fichiers JSON de job de rendu vivent ici (un fichier par lot de vidéos).

**Statut** : vide — les jobs seront écrits en **Phase 1**, après validation de
`../docs/03_JOB.md`. Rien n'est encore codé.

Règles :
- aucun chemin secret, aucun token dans ces fichiers ;
- les vidéos (`*.mp4`) ne sont jamais committées — elles transitent par
  `C:\nexrender\inbox\` sur le VPS.

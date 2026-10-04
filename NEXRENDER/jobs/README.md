# NEXRENDER/jobs/

Les fichiers JSON de job de rendu vivent ici (un fichier par video).

**Statut** : job de reference ecrit — `job.reference.json`.

Regles :
- aucun chemin secret, aucun token dans ces fichiers ;
- les videos (`*.mp4`) ne sont jamais committees — elles transitent par
  `C:\nexrender\inbox\` sur le VPS ;
- un job = une video (`job_policy: one_job_per_video` dans `../paths.json`).

F02_RENDER genere le JSON a partir de ce modele, en substituant
`video_test` par l'`id` de l'item du manifeste F01.

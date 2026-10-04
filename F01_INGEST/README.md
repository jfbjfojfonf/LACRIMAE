# F01_INGEST — la frégate qui récupère les vidéos

## Rôle

**Une seule responsabilité** : récupérer les vidéos déjà créées (par une autre branche,
un autre pipeline, un stockage) et les rendre prêtes pour le traitement.

```
[source des vidéos] ──► F01_INGEST ──► file d'attente ──► F02_RENDER
```

## Ce qu'elle fait

1. **Lire la source** des vidéos à traiter (emplacement à définir — cf. TODO dans
   `CONTINUATION.md` : `output/` ? autre branche ? stockage Modal ?)
2. **Valider** chaque vidéo : format lisible, 1920×1080, durée, sans audio surprise.
3. **Déposer** la vidéo dans la file d'attente (dossier d'entrée du VPS,
   `C:\nexrender\inbox\` par convention).
4. **Émettre** la liste des vidéos prêtes pour F02_RENDER (un manifeste simple).

## Ce qu'elle ne fait PAS

- Pas de traitement, pas de colorimétrie, pas d'encodage → c'est le travail de **F02_RENDER**.
- Pas d'accès After Effects, pas de Nexrender.

## Contrat de sortie (vers F02_RENDER)

| Champ | Description |
|---|---|
| chemin vidéo | fichier mp4 déposé, prêt à traiter |
| métadonnées | résolution, fps, durée |
| identifiant | nom unique du rendu demandé |

## Statut

- [ ] Source des vidéos définie
- [ ] Contrat F01 → F02 figé
- [ ] Code écrit (Phase 1, après validation)

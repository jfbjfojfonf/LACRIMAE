# F02_RENDER — la frégate qui travaille les vidéos

## Rôle

Prendre les videos preparees par F01_INGEST, les envoyer a Nexrender sur le VPS avec `cc2.ffx`, recuperer la video finale.

```
F01_INGEST ──► F02_RENDER ──► [VPS: nexrender → aerender + cc2.ffx] ──► vidéo finie
```

## Ce qu'elle fait

1. Lire `C:\nexrender\queue\manifest.json`.
2. Construire un job par item a partir de `NEXRENDER/jobs/job.reference.json`.
3. Soumettre au `nexrender-server` (`http://127.0.0.1:3000`).
4. Suivre l'etat, livrer dans `C:\nexrender\outbox\<id>.mp4`.

## Ce qu'elle ne fait PAS

- Pas de recuperation des sources → **F01_INGEST**.
- Pas de pipeline OpenCV/Polyester → `f09-output`.

## Statut

- [x] Job JSON de reference ecrit
- [x] Script JSX ecrit
- [ ] Code F02 ecrit (Phase 1b)
- [ ] Premier rendu de test reussi (Phase 4)

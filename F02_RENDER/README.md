# F02_RENDER — la frégate qui travaille les vidéos

## Rôle

**Une seule responsabilité** : prendre les vidéos préparées par F01_INGEST, les envoyer
à **Nexrender** sur le VPS avec le preset **`cc2.ffx`**, et récupérer la vidéo finale.
Et basta.

```
F01_INGEST ──► F02_RENDER ──► [VPS: nexrender → aerender + cc2.ffx] ──► vidéo finie
```

## Ce qu'elle fait

1. **Construire le job** : un JSON Nexrender par vidéo (template `.aep`, calque `SRC`,
   chemin de la source, script JSX du preset, encodage) — cf. `NEXRENDER/docs/03_JOB.md`.
2. **Soumettre le job** au `nexrender-server` du VPS.
3. **Suivre l'état** du rendu (en attente / en cours / terminé / échoué).
4. **Récupérer la sortie** dans le dossier de rendu du VPS et la livrer
   (stockage ou dossier de sortie à définir).

## Ce qu'elle ne fait PAS

- Pas de récupération des sources → **F01_INGEST**.
- Pas de pipeline OpenCV/Polyester → tout ça reste sur `f09-output`.

## Points d'attention

- Le rendu est **synchronisé avec l'état du VPS** : si le VPS est éteint (crédit essai),
  le job attend — ne jamais supposer le VPS toujours allumé.
- En cas d'échec, se référer à `NEXRENDER/docs/05_DEPANNAGE.md`.

## Contrat d'entrée (depuis F01_INGEST)

| Champ | Description |
|---|---|
| chemin vidéo | fichier mp4 dans `C:\nexrender\inbox\` |
| identifiant | nom unique du rendu demandé |

## Contrat de sortie

| Champ | Description |
|---|---|
| vidéo finale | mp4 coloré avec `cc2.ffx` |
| statut | succès / échec + raison |
| durée de rendu | pour le suivi du crédit Kamatera |

## Statut

- [ ] Job JSON de référence écrit (Phase 1)
- [ ] Script JSX spec-validé puis écrit (Phase 1)
- [ ] Premier rendu de test réussi (Phase 4)
- [ ] Code écrit (Phase 1, après validation)

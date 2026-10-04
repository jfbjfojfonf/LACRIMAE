# F01_INGEST — la frégate qui récupère les vidéos

## Rôle

**Une seule responsabilité** : récupérer les vidéos déjà créées et les rendre prêtes pour F02_RENDER.

```
[source des vidéos] ──► F01_INGEST ──► file d'attente ──► F02_RENDER
```

## Usage

```
python F01_INGEST/ingest.py
python F01_INGEST/ingest.py --source C:\nexrender\sources --inbox C:\nexrender\inbox --queue C:\nexrender\queue
```

Exige `ffprobe` dans le PATH (install FFmpeg sur le VPS).

## Ce qu'elle fait

1. **Lire la source** : `C:\nexrender\sources` par defaut (`NEXRENDER/paths.json`).
2. **Valider** chaque video : mp4 lisible, 1920x1080, duree > 0.
3. **Deposer** dans `C:\nexrender\inbox\<id>.mp4`.
4. **Emettre** `C:\nexrender\queue\manifest.json`. Les skips vont dans `skipped.json`.

## Ce qu'elle ne fait PAS

- Pas de traitement, pas de colorimetrie, pas d'encodage → **F02_RENDER**.
- Pas d'acces After Effects, pas de Nexrender.

## Contrat de sortie

Voir `NEXRENDER/contract/f01_f02.schema.json`. Champs obligatoires : `id`, `video_path`.

## Statut

- [x] Source par defaut definie (`C:\nexrender\sources`)
- [x] Contrat F01 → F02 fige
- [x] Code ecrit (`ingest.py`)
- [x] Tests (`tests/test_ingest.py`)

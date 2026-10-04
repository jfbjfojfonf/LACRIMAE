# Contrat F01_INGEST → F02_RENDER

F01 emet un manifeste JSON. F02 le lit, un item = un job Nexrender.

- Schema : `f01_f02.schema.json`
- Exemple : `f01_f02.example.json`
- Chemin canonique VPS : `C:\nexrender\queue\manifest.json`

Champs obligatoires par item : `id`, `video_path`.

Decisions figees (Phase 1) :

| Cle | Valeur |
|---|---|
| Calque placeholder | `SRC` |
| Composition template | `MAIN` |
| Sortie | mp4 H.264 |
| Politique jobs | un job par video |
| Plugin manquant | echec du job |

# 03 — Format du job de rendu (JSON)

> **Statut : implemente.** Reference : `../jobs/job.reference.json`.

F02 genere un job par video, POST `http://127.0.0.1:3000/api/v1/jobs` avec header `nexrender-secret`.

## Decisions figées

| Cle | Valeur |
|---|---|
| Template | `file:///C:/nexrender/templates/template.aep` |
| Composition | `MAIN` |
| Calque | `SRC` |
| Output module AE 2023+ | `H.264 - Match Render Settings - 15 Mbps` |
| Script | `file:///C:/nexrender/scripts/apply_cc2.jsx` |
| Sortie | mp4 H.264 puis copy `C:/nexrender/outbox/<id>.mp4` |
| Politique | un job par video |
| Video asset | `useOriginal: true` (pas de copie temp inutile) |

API : `POST /api/v1/jobs`, `GET /api/v1/jobs/:uid`. Etats utiles : `queued`, `started`, `finished`, `error`.

# 03 — Format du job de rendu (JSON)

> **Statut : implémenté.** Fichier de référence : `../jobs/job.reference.json`.

## Rôle

Un job Nexrender décrit **un rendu**. F02_RENDER génère **un job par vidéo** et le soumet au `nexrender-server` du VPS.

## Décisions figées

| Cle | Valeur |
|---|---|
| Template | `file:///C:/nexrender/templates/template.aep` |
| Composition | `MAIN` |
| Calque | `SRC` |
| Script | `file:///C:/nexrender/scripts/apply_cc2.jsx` |
| Sortie | mp4 H.264 via `@nexrender/action-encode` |
| Destination | `C:/nexrender/outbox/<id>.mp4` |
| Politique | un job par video |

## Fichier de référence

Voir `../jobs/job.reference.json`. F02 substitue l'id video dans `assets[0].src` et `actions.postrender[1].output`.

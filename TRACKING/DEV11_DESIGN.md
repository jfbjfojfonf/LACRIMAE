# DEV11 — Design OCULUS / SANGUINOR / CALIX

Branche : `dev-11`
Statut : **cadrage + Groupe 0 scellés** — moteurs F01/F02/F03 non forgés
Date : 2026-10-04

---

## Ce que cette branche EST

Un **projet de flotte** autonome. Les autres branches LACRIMAE restent des usines à Shorts (match cut, reveal, ranking, PUR). `dev-11` est l'atelier de **camera virtuelle**. On lui donne des clips déjà 9:16 ; il rend les mêmes clips, visage collé, image stable.

## Ce que cette branche N'EST PAS

- Pas une F07 collée dans `dev10`.
- Pas un clone CapCut.
- Pas un ingest (pas de yt-dlp, pas de vidéo longue).
- Pas un monteur (pas de Remotion, pas de titre, pas de ranking).
- Pas un camouflage (F05/F06 restent chez l'appelant).
- Pas un job GitHub Actions qui décode 20 MP4 sur le runner.

---

## Pourquoi 3 frégates (pas 1, pas 7)

Une fonction = une frégate. Ici il y a **trois fonctions distinctes**, trois contrats JSON, trois raisons de relancer sans tout casser.

| Si on fusionnait | On perdrait |
|------------------|------------|
| F01+F02 | Impossible de retune la camera sans relancer MediaPipe |
| F02+F03 | Impossible de ré-encoder (codec, resolution) sans recalculer le path |
| F01+F02+F03 | Un monolithe. Contredit la Loi d'Isolement |

F00 n'existe pas : l'appelant pousse déjà des clips dans `F01_OCULUS/IN/clips/`.

F04+ n'existent pas : Signum / Camouflage / Luther sont le métier des branches de production.

---

## Hommage Blood Angels

| Nom | Référence | Pourquoi ce métier |
|-----|-----------|-------------------|
| **OCULUS** | L'œil de Sanguinius, vision au-delà du voile | Voir le visage : landmarks, pas encore bouger |
| **SANGUINOR** | L'Ange d'or qui **apparaît aux côtés** du guerrier | Suivre sans coller brut : inertie, deadzone, 1€ |
| **CALIX** | Le Red Grail, calice où le sang est **scellé** | Figer le mouvement dans un MP4 9:16 + audio |

Noms latins, comme CANTOR / VISIO / PICTOR / SIGNUM. Pas de F07_OCULUS dans une autre flotte.

---

## Flux de données

```
F01/IN/clips/<stem>.mp4
F01/IN/job_request.json          cible: face | nose | eyes
        │
        ▼  F01 OCULUS
F01/OUT/landmarks/<stem>.json
F01/OUT/oculus_report.json
        │  transit orchestrateur
        ▼
F02/IN/landmarks/<stem>.json
F02/IN/clips/<stem>.mp4          copie de transit, pas un accès F01
F02/IN/camera_request.json
        │
        ▼  F02 SANGUINOR
F02/OUT/camera_path/<stem>.json
F02/OUT/sanguinor_report.json
        │  transit orchestrateur
        ▼
F03/IN/camera_path/<stem>.json
F03/IN/clips/<stem>.mp4
        │
        ▼  F03 CALIX
F03/OUT/tracked/<stem>.mp4
F03/OUT/calix_manifest.json
F03/OUT/calix_report.json
```

Le transit copie les fichiers. F02 ne lit **jamais** `F01_OCULUS/OUT/` en production.

---

## Cibles camera (headless)

| Cible `job_request.target` | Landmark | Usage |
|----------------------------|----------|-------|
| `face` | centre de l'ovale | **défaut** — plus stable, talking-head |
| `nose` | tip du nez | effet "soudé" type CapCut |
| `eyes` | milieu des deux iris | yeux au tiers haut |

Le Magos choisit la cible **une fois** dans `job_request.json`. F02 ne redétecte pas. Il lit les IDs déjà écrits par F01.

---

## Cœur produit = F02, pas F01

MediaPipe est commodité. Sans **deadzone + 1€ + hold-last + zoom lent**, le crop tremble et **tue** la retention. F02 est la frégate qui justifie `dev-11`. F01 fournit des coordonnées. F03 applique un path déjà lisse.

---

## Compute

| Etape | Où | GPU ? |
|-------|-----|-------|
| F01 | Modal CPU (T4 optionnel) | Non requis v1 |
| F02 | Modal CPU | Non — filtre 2D |
| F03 | Modal GPU si `h264_nvenc`, sinon CPU libx264 | Optionnel |
| Actions | lint, tests contrat, `modal run` | Interdit de décoder les campagnes |

Videos : GitHub Release ou objet distant. Jamais dans git.

---

## Relation aux autres branches

```
dev / dev4 / dev8 / dev9 / dev10
        │  clips 9:16 (après FORMAT / F00-E / PUR)
        ▼
     dev-11  (cette flotte)
        │  tracked 9:16
        ▼
F03 PREVIEW → F04 SIGNUM → F05 → F06   (sur la branche appelante)
```

`dev-11` ne clone pas PICTOR. Il rend un MP4. L'appelant reprend son pipeline.

---

## Pile figée v1

- Detection : MediaPipe Face Landmarker (Tasks API, pas le Face Mesh legacy sauf fallback documenté)
- Lissage : One Euro Filter (implémentation à forger dans F02, référence casiez/OneEuroFilter)
- IO : PyAV lecture frames F01 ; FFmpeg crop+encode F03 ; audio `-c:a copy`
- Orchestration : GitHub Actions + Modal SDK

Hors v1 : YOLO-face, OpenReel, GitHub Actions GPU, OpenCV VideoWriter `mp4v`.

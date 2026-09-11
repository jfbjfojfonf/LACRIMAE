# LACRIMAE

> *For the Angel's Tears shall become gold.*

LACRIMAE est un pipeline de production de Shorts verticaux (YouTube/TikTok) avec plusieurs modes de production.

## Modes de production

| Branche | Mode | Description |
|---------|------|-------------|
| dev4 | Fast Match Cut | Montage automatique depuis une vidéo source |
| dev7 | Hybrid Audio Sync | Intro + Match Cut avec sync audio |
| dev8 | Reveal Compilation | Others vs This One — clips avec narration |
| **dev9** | **Ranking Compilation** | **Clips numérotés du rang N au rang 1** |

## Pipeline dev9 — Ranking Compilation

```text
Clips vidéo + (optionnel) audio
        │
        ▼
F00-E Reveal Clip Prep          F00-MUSIC (optionnel)
découpe les clips H.264         analyse la musique
        │                                │
        ▼                                ▼
    reveal_sources.json          music.mp3 + music_timeline.json
        │                                │
        ├──► F00-F Ranking Prep ◄────────┘
        │    (classe les clips en rangs)
        │         │
        │         ▼
        │    ranking_manifest.json
        │         │
        ▼         ▼
    F03 PREVIEW (validation interactive)
        │
        ▼
    F03_PICTOR (render Remotion → short_final.mp4)  [bras de rendu CI]
        |
        v
    F04 SIGNUM (sceau final FFmpeg : remux, faststart, Loi Duree)
        │
        ▼
    F05 CAMOUFLAGE → F06 LUTHER
        │
        ▼
    short_master.mp4 (livrable)
```

## Frégates dev9

| Étape | Nom | Mission | Sortie |
|-------|-----|---------|--------|
| **F00-E** | Reveal Clip Prep | Découpe les clips vidéo (H.264, 30fps) | `reveal_sources.json` + `clips/*.mp4` |
| **F00-F** | Ranking Prep | Classe les clips en rangs | `ranking_manifest.json` |
| **F00-MUSIC** | Audio Analysis | Analyse la musique (optionnel) | `music.mp3` |
| **F03** | Preview | Visualisation interactive du ranking | `codex.json` validé |
| **F04** | Signum | Sceau final FFmpeg (remux, metadonnees, Loi Duree) | `short_master.mp4` |
| **F05** | Camouflage | Réencodage H.264 yuv420p, faststart | `short_camouflaged.mp4` |
| **F06** | Luther | Nettoyage métadonnées | `short_master.mp4` |

## Format du Codex (ranking_compilation)

```json
{
  "review_mode": "ranking_compilation",
  "ranking_manifest": {
    "narrative": {
      "title_words": [
        { "text": "SPIDER-MAN", "color": "#FF4444" },
        { "text": "RANKING", "color": "#FFFFFF" }
      ],
      "global_controls": {
        "title_scale": 1,
        "number_scale": 2.3,
        "label_scale": 2.35,
        "clip_audio": true,
        "list_x_pct": 5,
        "list_y_pct": 95,
        "title_size": 42
      }
    },
    "entries": [
      {
        "rank": 4,
        "label_words": [{ "text": "CLIP", "color": "#FFFFFF" }],
        "number_color": "#FF4444",
        "number_size": 42,
        "label_size": 22,
        "duration_seconds": 6,
        "sfx": { "enabled": true, "file": "sfx/impact.mp3" }
      }
    ]
  }
}
```

## Workflows GitHub Actions

| Workflow | Branche | Rôle |
|----------|---------|------|
| `dev9_spiderman_ranking.yml` | dev9 | F00-E + F00-F (clips + ranking) |
| `dev9_spiderman_render.yml` | dev9 | F04 render (clips + ranking → MP4) |

## Quickstart

```bash
cd F03_PREVIEW/CODEBASE
npm ci
npm run dev
```

## Rendu F04

```bash
cd F03_PREVIEW/CODEBASE
npm ci
npm run build
npm run render
# → out/short_final.mp4
```

Ou via GitHub Actions : **DEV9 — Spider-Man Ranking Render**.

## Release

Le master final est sur :

```
https://github.com/kioka8877-ux/LACRIMAE/releases/download/f04_f05_f06_spiderman_master/short_master.mp4
```

## Notes techniques

- **Clips** : Doivent être H.264 (pas H.265/HEVC) — Chrome Headless ne supporte pas HEVC
- **Audio clips** : F00-E garde l'audio d'origine (`-an` retiré)
- **SFX** : Chaque rang peut avoir un son de transition (impact.mp3, king_reveal.mp3)
- **Numéros** : Permanent dans le temps (visibles de début en fin)
- **Labels** : Apparaissent du bas vers le haut (rank N → rank 1)
- **Rang 1** : Toujours le dernier, avec effet spécial (glow doré)
- **Titre** : Word-by-word avec couleur par mot, position configurable
- **Pas de musique de fond** : Contrairement à dev8, dev9 n'a pas de musique de fond

# F00_PUR

Ingest du segment VOD. Le pack ne contient pas la video : il contient
`vod_url` + `start_sec` + `end_sec`. F00_PUR telecharge **uniquement le
segment** (`yt-dlp --download-sections`), jamais la VOD complete.

## Contrats

| | Chemin |
|--|--------|
| IN | pack PUR (via Bridge) |
| OUT | `OUT/pur_<angle>.mp4` + `OUT/pur_sources.json` |
| Code (a venir) | `CODEBASE/f00_pur.py` |

## Gates

- **G0** pack exploitable
- **G1** VOD obtenue
- **G2** duree = end − start ± 0.5 s (re-decoupe locale si derive <= +3 s)
- **G3** codec lisible (h264 / vp9 / hevc / av1)

Sans F00_PUR, preview et rendu n'ont rien a monter.

Voir `TRACKING/PUR_GATES.md`.

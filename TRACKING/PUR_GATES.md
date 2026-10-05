# LACRIMAE dev10-v2 — PUR GATES

## Doctrine

dev10-v2 est le bras arme du mode PUR. PERTURABO analyse et ecrit le pack.
LACRIMAE execute : recupere, telecharge le segment, compose le look,
execute le temps, camoufle, livre.

```text
PERTURABO EXPORT/production_pack_pur_*.json
        |
        v
[BRIDGE]  fetch + G0 + conversion → pur_manifest.json
        |
        v
[F00_PUR]  yt-dlp --download-sections → clips/pur_<angle>.mp4
        |
        v
[F03_PREVIEW]  validation visuelle (blur / split / reframing)
        |
        v
[F03_PICTOR]  LOOK → MP4 compose (0 zoom)
        |
        v
[F04_HEISENBERG]  TEMPS → MP4 reel (cuts / SFX / B-roll / flash)
        |
        v
[F05] → [F06] → livrable
        |
        v
[TRACKING/PUR_CAMPAIGN_LOG.md]
```

## Gates

| Gate | Moment | Verification | Critere |
|------|--------|--------------|---------|
| **G0 PACK** | Avant tout | Pack exploitable | `mode=pur`, `vod_url`, `start_sec < end_sec`, segment <= 150 s, `montage_instructions` presente |
| **G0-S STYLE** | Conversion | Style identifie ET autorise | `blur` / `split_scene` / `reframing` declare par le pack OU `--style` operateur. Infere = REFUS (exit 2). Ranking refuse. |
| **G1 VOD** | Download | Segment obtenu | yt-dlp OK, fichier produit |
| **G2 DUREE** | Apres download | Duree clip | `duration == end_sec − start_sec ± 0.5 s` (re-decoupe locale si derive <= +3 s) |
| **G3 CODEC** | Apres download | Lisibilite | codec in {h264, vp9, hevc, av1}, dimensions > 0 |
| **P0 MANIFESTE** | Apres conversion | `pur_manifest.json` | `schema_version=dev10.pur.v1`, >= 1 entree, overlay non vide, `style_source` in {pack, operator} |
| **P1 PREVIEW** | Avant rendu | Validation visuelle | Overlay lisible, style correct, **aucun zoom a l'ecran** |
| **P2 LOOK** | Apres PICTOR | MP4 compose | Resolution canvas, duree ≈ manifeste, framing fixe |
| **P3 TEMPS** | Apres Heisenberg | MP4 reel | Jump cuts / SFX / B-roll / flash / punch-in-cut conformes au pack. Punch-in = cut, pas scale. Sortie = fichier video, jamais JSON seul. |
| **P-AUD AUDIO** | Agregation | Piste audio | `audio_codec` present (ffprobe). Rendu muet = rendu manquant. |
| **P-AGG MULTI** | Apres N rendus | Agregeur | Chaque asset a son MP4. Un manque = publication refusee. |
| **P-ZOOM ZERO** | PICTOR + Heisenberg | Interdit | Aucun zoom, swell, scale anime, breathing_zoom. Echec = job stoppe. |

## Politique d'echec

- G0-S echoue → RENDU BLOQUE. Deux sorties : regenerer le pack cote
  PERTURABO, ou relancer avec `--style blur|split_scene|reframing`.
- G0 echoue → retour PERTURABO. Jamais de correction manuelle du pack.
- G1/G2/G3 echouent → VOD expiree : basculer le clip en asset Release.
- P1 echoue → corriger dans le preview, re-valider avant PICTOR.
- P3 echoue → Heisenberg n'a pas produit de MP4 conforme. Pas de livraison.
- P-ZOOM ZERO echoue → code a reintroduire un zoom. Revert, pas de workaround.

## Contrats

| Contrat | Chemin | Proprietaire |
|---------|--------|--------------|
| Pack PUR | `production_pack_pur_*.json` | PERTURABO |
| Manifeste `dev10.pur.v1` | `BRIDGE_PERTURABO/OUT/pur_manifest.json` | LACRIMAE bridge |
| Sources segment | `F00_PUR/OUT/pur_sources.json` | F00_PUR |
| Parite LOOK | F03_PREVIEW ↔ F03_PICTOR | LACRIMAE |
| Execution TEMPS | F04_HEISENBERG → MP4 | LACRIMAE |

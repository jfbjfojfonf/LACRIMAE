# LACRIMAE — branche `dev11-F07` (base `dev10-v2`)

> *For the Angel's Tears shall become gold.*

Bras arme du mode PUR de PERTURABO. Pack in, MP4 out. Arbre neuf : aucune
heritage ranking / reveal / hybrid / Signum.

Branche `dev10-v2` : contrat + portes figes, salvage A–G (F05/F06,
F00_PUR, Bridge PUR, F03_PREVIEW LOOK, F03_PICTOR, F04_HEISENBERG,
workflow `dev10_pur_render.yml`).

Branche `dev11-F07` : F07_CAPTION H0–H4 (preview, Whisper, proof Blender,
overlay + F05/F06). Hors flux PUR jour 1.

## Doctrine

| Role | Qui | Decide | Ne fait PAS |
|------|-----|--------|-------------|
| Cerveau creatif | PERTURABO | Le OU et le QUOI (segment, overlay, moments, B-roll) | La physique des effets, le rendu, les gates |
| Bras arme | LACRIMAE | Le COMMENT (execution, portes, agregation) | Choisir un segment, ecrire une accroche, zoomer |
| Operateur | Warsmith | Validation aux portes | — |

Le pack PERTURABO n'est jamais modifie cote LACRIMAE. Correction = retour
forge.

## Pipeline

```text
PERTURABO EXPORT / production_pack_pur_*.json
        |
        v
[BRIDGE_PERTURABO]  fetch + conversion → pur_manifest.json
        |
        v
[F00_PUR]  yt-dlp --download-sections → pur_<angle>.mp4 + pur_sources.json
        |
        v
[F03_PREVIEW]  validation visuelle (blur / split / reframing)
        |
        v
[F03_PICTOR]  Remotion — LOOK only → mp4 compose (sans zoom)
        |
        v
[F04_HEISENBERG]  FFmpeg — TEMPS : jump cuts, SFX, B-roll, flash, punch-in-cut → MP4 reel
        |
        v
[F05_CAMOUFLAGE] → [F06_LUTHER] → livrable
```

1 asset (A01, A02, …) = 1 video finale = 1 job. Le pack = l'ensemble des assets.

## Frégates

| Frégate | Mission | Sortie |
|---------|---------|--------|
| BRIDGE_PERTURABO | Recupere le pack, gate G0, convertit en manifeste `dev10.pur.v1` | `pur_manifest.json` |
| F00_PUR | Telecharge UNIQUEMENT le segment VOD | `pur_<angle>.mp4` + `pur_sources.json` |
| F03_PREVIEW | Validation visuelle, 3 styles, overlay | manifeste valide |
| F03_PICTOR | Rendu LOOK (meme moteur que la preview) | MP4 compose, framing fixe |
| F04_HEISENBERG | Execute le temps du pack sur le MP4 | MP4 reel (cuts / SFX / B-roll) |
| F05_CAMOUFLAGE | Reencodage H.264 yuv420p, faststart | MP4 camoufle |
| F06_LUTHER | Nettoyage metadonnees | livrable |
| F07_CAPTION | Sous-titres 3D mot-a-mot (optionnel, hors PUR jour 1) | transcript + s1 + calque |

F07 n'entre pas dans le pipeline PUR obligatoire. Preview / preuve /
rendu captions : `TRACKING/GUIDE_CAPTION.md`. P-ZOOM ZERO inchange.

## Styles autorises (jour 1)

Uniquement trois : `blur`, `split_scene`, `reframing`. Ranking hors scope.

## Interdits (non negociables)

- Zoom, swell, scale anime, breathing_zoom — bannis PICTOR et Heisenberg.
- Punch-in = **cut**, jamais une animation : a `in` on coupe, on joue
  uniquement `[in, out]` recadre plus serre ; a `out` on recoupe, retour
  framing normal.
- SIGNUM n'existe plus.
- Le pack n'est jamais edite cote bras arme.

## Docs

| Document | Role |
|----------|------|
| `TRACKING/TODO_CONTINUATION.md` | Point d'entree apres toute reprise |
| `TRACKING/PUR_GATES.md` | Portes de validation |
| `TRACKING/GUIDE_BRAS_ARME_PUR.md` | Guide operateur PERTURABO → LACRIMAE |
| `TRACKING/GUIDE_UTILISATION.md` | Guide d'utilisation local / CI |
| `TRACKING/PUR_CAMPAIGN_LOG.md` | Journal des campagnes |
| `TRACKING/CAPTION_GATES.md` | Portes F07 (separees de PUR) |
| `TRACKING/GUIDE_CAPTION.md` | Guide operateur sous-titres 3D |

## Hors arbre (purge `dev10`)

F00H, F01_CANTOR, F02_VISIO, SeatRoom, modal, ORACLE, F04_SIGNUM,
ranking / reveal / hybrid / music, workflows dev4–dev9.

> LACRIMAE — le bras arme n'interprete pas : il execute, il bloque, il prouve.
> Warsmith tranche. PERTURABO cree.

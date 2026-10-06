# Guide Operateur — Bras arme PUR (dev10-v2)

> Pour le Warsmith qui veut transformer un pack PUR en video publiee.
> Pas besoin de connaitre le code. Suivre les portes.

## Principe en 3 lignes

1. **PERTURABO** exporte `production_pack_pur_*.json` (segment, overlay,
   instructions de montage).
2. **LACRIMAE** execute : bridge → F00_PUR → preview → PICTOR (look) →
   Heisenberg (temps) → F05 → F06.
3. Tu n'appuies que sur les portes. Jamais la VOD complete. Jamais de
   modification du pack cote LACRIMAE.

## Checklist

- Pack PUR recent dans `PERTURABO/MONDES_FORGES/CLIPPING/EXPORT/`
- VOD source joignable
- Style choisi parmi `blur`, `split_scene`, `reframing`
- Canvas (9:16 par defaut)

## Etape 0 — Le style : c'est TOI qui choisis

Si le pack ne declare pas `montage_style`, rien n'est rendu. Deux options :

```bash
# Option A : a la conversion
node tools/convert_pur_pack.mjs --pack ... --style blur ...

# Option B : champ style du workflow CI
```

Jamais de rendu en silence. Ranking refuse.

| Style | Rendu LOOK (PICTOR) |
|-------|---------------------|
| `blur` | couche arriere floutee + couche avant nette |
| `split_scene` | video en haut + element bas |
| `reframing` | recadrage fixe du clip (echelle / offset, **pas un zoom anime**) |

## Etape 1 — Bridge

```bash
python3 BRIDGE_PERTURABO/CODEBASE/lac_bridge_forge.py --pur --pack-filter pur_A01
```

Gate G0. Sortie : `pur_manifest.json` vers preview et PICTOR.

## Etape 2 — F00_PUR

```bash
python3 F00_PUR/CODEBASE/f00_pur.py \
  --pack BRIDGE_PERTURABO/IN/production_pack_pur_A01.json \
  --out F00_PUR/OUT
```

Gates G0–G3. Sortie : `pur_A01.mp4` + `pur_sources.json`.
Jamais la VOD complete.

## Etape 3 — Preview (P1)

Onglet PUR :

- Overlay 1–3 lignes, statique debut → fin
- Panneau du style actif uniquement
- Anti-detection : miroir, vitesse, crop % — **pas de zoom respiration**
- Validation visuelle obligatoire avant PICTOR

## Etape 4 — PICTOR (P2 LOOK)

Rendu Remotion, meme moteur que la preview. Framing fixe. Zero zoom.
Sortie : MP4 compose (look applique, timeline encore "plate").

```bash
cd F03_PICTOR/CODEBASE
npm ci
node render_pictor.mjs \
  --manifest ../../BRIDGE_PERTURABO/OUT/pur_manifest.json \
  --clips ../../F00_PUR/OUT \
  --out ../../F03_PICTOR/OUT
```

## Etape 5 — Heisenberg (P3 TEMPS)

Heisenberg prend le MP4 PICTOR + le manifeste et **ecrit un nouveau MP4**.

Il execute, dans l'ordre du pack :

- jump cuts (silences)
- punch-in **par cut** : a `in`, coupe et joue `[in, out]` recadre plus
  serre ; a `out`, coupe et revient au framing normal
- B-roll / memes
- flash blanc d'entree (jamais de sortie)
- SFX cales sur la meme frame, sous la voix
- ducking / smash audio

```bash
python3 F04_HEISENBERG/CODEBASE/heisenberg.py \
  --input F03_PICTOR/OUT/pur_A01_look.mp4 \
  --manifest BRIDGE_PERTURABO/OUT/pur_manifest.json \
  --out F04_HEISENBERG/OUT
```

Pas de JSON advisory. Pas de scale anime. Si Heisenberg ne sort pas un
MP4 lisible, le job echoue.

## Etape 6 — F05 / F06

Camouflage puis luther. Livrable pret publication.

## Multi-videos

1 codex = N videos = 1 run. Un asset manque → zip refuse.

## F07_CAPTION (hors ce guide)

Sous-titres 3D mot-a-mot : frégate optionnelle, pas une etape PUR.
Voir `TRACKING/GUIDE_CAPTION.md`. Ne pas regler le caption dans F03_PREVIEW.

## Rappels

- Pack intouchable cote LACRIMAE.
- Zoom banni.
- Punch-in = cut, pas animation.
- Voix ON. Rendu muet refuse.
- Pas de CTA. Finir sur la chute.

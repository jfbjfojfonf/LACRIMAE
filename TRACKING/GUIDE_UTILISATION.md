# Guide d'utilisation — LACRIMAE dev10-v2

Branche squelette. Les commandes ci-dessous sont le contrat cible.
Elles ne tournent pas tant que le code n'est pas pose (GO Warsmith).

## Vocabulaire

- **asset** : A01, A02, … = 1 video finale = 1 job
- **pack** : l'ensemble des assets
- **LOOK** : F03_PREVIEW + F03_PICTOR (blur / split / reframing, overlay)
- **TEMPS** : F04_HEISENBERG (cuts, SFX, B-roll, flash, punch-in-cut)

## Local (cible)

```bash
# 1. Bridge : pack PERTURABO → manifeste
python3 BRIDGE_PERTURABO/CODEBASE/lac_bridge_forge.py --pur --pack-filter pur_A01

# 2. Segment VOD uniquement
python3 F00_PUR/CODEBASE/f00_pur.py \
  --pack BRIDGE_PERTURABO/IN/production_pack_pur_A01.json \
  --out F00_PUR/OUT

# 3. Preview
cd F03_PREVIEW/CODEBASE
npm ci
npm run dev

# 4. Rendu LOOK
cd F03_PICTOR/CODEBASE
npm ci
npm run render

# 5. Execution TEMPS (MP4 reel)
python3 F04_HEISENBERG/CODEBASE/heisenberg.py \
  --input F03_PICTOR/OUT/pur_A01_look.mp4 \
  --manifest BRIDGE_PERTURABO/OUT/pur_manifest.json \
  --out F04_HEISENBERG/OUT

# 6. Camouflage + luther
python3 F05_CAMOUFLAGE/CODEBASE/lac_f05_camouflage.py \
  --input F04_HEISENBERG/OUT/pur_A01.mp4 \
  --out F05_CAMOUFLAGE/OUT
python3 F06_LUTHER/CODEBASE/lac_f06_luther.py \
  --input F05_CAMOUFLAGE/OUT/pur_A01.mp4 \
  --out F06_LUTHER/OUT
```

## CI (cible)

Un seul workflow : `.github/workflows/dev10_pur_render.yml`

Inputs prevus : `pack_filter`, `canvas`, `perturabo_branch`, `style`,
`max_parallel`, `max_duration`.

Flux : prepare (fetch + G0) → matrix 1 asset / 1 job → PICTOR →
Heisenberg → agregeur strict → F05/F06.

## Fichiers jamais commites

Clips, OUT/, `pur_manifest.json` genere, `codex.json` local.
Transit par artifacts CI ou GitHub Releases.

## En cas de probleme (cible)

| Symptome | Cause | Action |
|----------|-------|--------|
| G0 echoue | pack incomplet | retour PERTURABO |
| G1 echoue | VOD expiree | clip en Release, rejouer |
| G2 echoue | derive timestamps | verifier start/end_sec |
| CLIP PUR MANQUANT | F00_PUR pas lance | etape 2 |
| Zoom visible | P-ZOOM ZERO | revert, ne pas ship |
| Heisenberg JSON only | frégate incomplete | job rouge, pas de livraison |

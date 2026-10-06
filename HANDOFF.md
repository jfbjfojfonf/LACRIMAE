# HANDOFF — `dev6-F`

## Ou on en est

Copie de `dev6-E` @ `24a719d`. Pivot LUT (FFmpeg `lut3d`), plus de Nexrender.

| Phase | Statut |
|---|---|
| P0 docs + arbre | ✅ |
| P1 copie F05/F06 | ✅ verbatim `dev10-v2` |
| P2 F01+F02 LUT | ✅ ingest.py + lut.py, 10 tests, Nexrender purge |
| P3 Modal + Actions | bloque : `.cube` + `MODAL_TOKEN` (humain) |
| P4 cablage F05/F06 | apres 1 rendu LUT OK |

## Noms figes

- `F01_INGEST`
- `F02_RENDER` (LUT a l'interieur, **pas** de rename)
- `F05_CAMOUFLAGE` / `F06_LUTHER` copies verbatim `dev10-v2`

## Interdits

- Ne pas toucher `dev6-E`, `dev10-v2`, `main`
- Ne pas importer PUR / Remotion / PICTOR / Heisenberg
- Ne pas committer `.cube`, `.mp4`, tokens
- F05/F06 : pas de rewrite

## Reprise

```
git clone https://github.com/jfbjfojfonf/LACRIMAE.git
cd LACRIMAE
git fetch origin --prune
git checkout dev6-F
```

Lire `TRACKING/TODO_CONTINUATION.md` puis ce fichier.

Tests :

```
python3 -m unittest F01_INGEST.tests.test_ingest F02_RENDER.tests.test_lut -v
```

Doit faire 10/10. P3 : ne pas coder tant que `.cube` + `MODAL_TOKEN` absents.

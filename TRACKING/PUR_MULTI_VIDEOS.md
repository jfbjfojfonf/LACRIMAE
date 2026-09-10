# PUR — ARCHITECTURE MULTI-VIDÉOS (1 codex = N vidéos = 1 run = 1 zip)

> Décision Warsmith du 2026-09-10. Doctrine établie depuis dev4/dev9,
> appliquée au bras armé PUR : **un seul codex** décrit ce que TOUTES les
> vidéos finales ressemblent ; le rendu déclenche **un run** qui rend
> **N vidéos en parallèle** (matrix GitHub Actions, jusqu'à 20 runners),
> agrégées dans **un bundle (zip)** transmis aux frégates suivantes pour
> camouflage et nettoyage. **Zéro concat** : chaque vidéo reste un MP4
> distinct dans le bundle.
>
> **IMPLÉMENTÉ le 2026-09-10** — toutes les phases livrées et vérifiées.

---

## Le principe (verrouillé)

1. **1 codex PUR** multi-entrées (`entries: [A01, A02, A03…]`) — il montre
   ce que TOUTES les vidéos finales vont ressembler.
2. **Ce que l'opérateur valide sur l'aperçu s'applique À TOUTES les vidéos
   finales** : style (blur/split/reframing/ranking), texte overlay (lignes,
   couleurs, police, boîte, position), anti-détection — tout est GLOBAL.
3. **Le rendu déclenche UN run** : job `prepare` → job `render` en matrix
   (`max-parallel` 1-20, 1 runner = 1 vidéo) → job `aggregate`.
4. **Publication refusée si un seul rendu manque** (règle dev9 conservée).
5. **Sortie = bundle `lac-pur-final`** (N MP4 distincts + manifestes +
   rapport d'agrégation) — prêt pour F05_CAMOUFLAGE. Jamais de concat.

---

## Frégates touchées (livré)

| Frégate | Livraison |
|---|---|
| **F00_INGEST** | `f00_pur.py --append` : chaque pack ajoute son segment à `pur_sources.json` (multi-vidéos), G0-G3 inchangés |
| **F03_PREVIEW** | Chargeur MULTI-fichiers (1 pack = 1 vidéo), `parsePurPackMulti`, sélecteur ◀▶ « VIDÉO X/N », durée = somme des entrées |
| **F03_PICTOR/F04** | `extractPurEntryManifest` (1 runner = 1 vidéo), porte de style ouverte aux 4 styles PUR autorisés, composition miroir overlay global |
| **Workflow CI** | `dev10_pur_render.yml` réécrit : prepare (fetch packs + G0 dry-run + matrix) → render (N runners) → aggregate (`tools/pur_aggregate.py`, refus si incomplet) |
| **F05_CAMOUFLAGE** | `lac_f05_camouflage.py --batch <dossier>` : N MP4 → mêmes traitements 1:1 + rapport consolidé `camouflage_batch_report.json` |

## Outils (livrés)

- `tools/convert_pur_pack.mjs --packs "p1.json,p2.json,…"` : conversion
  multi-pack → manifeste multi-entrées, avec `--style-params <réf.json>`
  pour reprendre les réglages opérateur validés (le codex).
- `tools/pur_aggregate.py` : agrégateur strict — vérifie chaque entrée,
  renomme `pur_<angle>_finale.mp4`, produit le rapport, **code 1 si un MP4
  manque** (rien n'est publié).

---

## Flux complet (de bout en bout)

```
PERTURABO EXPORT (production_pack_pur_A01/A02/A03.json)
        │
        ▼
workflow dev10_pur_render — job PREPARE
  fetch des N packs (pack_filter ou TOUS) + G0 dry-run + matrix
        │
        ▼
job RENDER (matrix, max-parallel 1-20)  ×N runners
  F00-PUR (yt-dlp sections, G0-G3) → convert (style global +
  réglages opérateur du codex) → Remotion → pur_<angle>_finale.mp4
        │
        ▼
job AGGREGATE
  tools/pur_aggregate.py : vérifie N/N → refus si incomplet
  → artifact lac-pur-final (N MP4 + pur_manifest.json + rapport)
        │
        ▼
F05_CAMOUFLAGE --batch  → N MP4 H.264 faststart + rapport batch
        ▼
Frégates suivantes (nettoyage / publication)
```

---

## Vérifications effectuées (2026-09-10)

- Conversion multi : 3 packs A01/A02/A03 → 3 entrées, réglages opérateur
  repris (blur 24/118/72/62), 90 s cumulées, 2571 frames ✓
- `parsePurPackMulti` : style global, overlay copié par entrée, `pur.multi` ✓
- `extractPurEntryManifest` : extraction A02 → 1 entrée, 857 frames ✓
- Workflow YAML : 3 jobs prepare/render/aggregate, matrix fromJSON ✓
- `pur_aggregate.py` : 3/3 → bundle OK ; 2/3 → refus code 1 ✓
- F05 `--batch` : 2 MP4 → H.264 yuv420p faststart, rapport consolidé ✓
- Build Vite preview : ✓ (2,7 s)

## Ce qui reste à l'opérateur

1. Valider le rendu multi dans le preview (sélecteur ◀▶).
2. GO → premier run matrix (par défaut : TOUS les packs PUR, style blur).

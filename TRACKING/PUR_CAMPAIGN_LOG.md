# LACRIMAE dev10 — JOURNAL DE CAMPAGNES PUR

| Date | Pack | Angle | Segment (s) | Canvas | Gates G0-G3 | P1 Preview | P2 Rendu | Run CI | Décision |
|---|---|---|---|---|---|---|---|---|---|
| 2026-09-09 | pur-A01 | A01 | 737.48 → 767.48 | 9:16 | G0 ✓ G1 ✓ G2 ✓ G3 ✓ (automatiques, script) | ❌ NON VALIDÉE | ⚠️ brouillon technique — lac_pur_final.mp4 12.6 Mo, 857/857 frames | [34340044745](https://github.com/kioka8877-ux/LACRIMAE/actions/runs/34340044745) | **TEST TECHNIQUE LANCÉ SANS AUTORISATION OPÉRATEUR — NON VALIDÉ.** Artefact à considérer comme brouillon jusqu'à visualisation et décision du Warsmith |
| — | — | — | — | — | — | — | — | — | — |

### Historique des runs CI (2026-09-09)

| Run | Résultat | Cause échec / note |
|---|---|---|
| [34338334121](https://github.com/kioka8877-ux/LACRIMAE/actions/runs/34338334121) | ❌ failure | codex injecté dans public/ au lieu de src/data/ → rendu sur route reveal (404 reveal_01.mp4). Fix a6b07f8 |
| [34339647085](https://github.com/kioka8877-ux/LACRIMAE/actions/runs/34339647085) | ❌ failure | codex.json committé avec clips[] vide → IndexError injection. Fix 4c7e524 |
| [34340044745](https://github.com/kioka8877-ux/LACRIMAE/actions/runs/34340044745) | ✅ success (technique) | Pack pur_A01 → yt-dlp → BridgeClipper → Remotion → 12.6 Mo. **⚠️ Déclenché par l'agent sans GO explicite de l'opérateur — procédure à ne pas reproduire : tout run CI réel exige l'autorisation préalable du Warsmith** |

Fixes notés pendant la mise en service : input `canvas` en string (le type choice avec « : » bloque le dispatch API), SFX désactivés par défaut (`sfx_available`, fichiers sfx/*.mp3 pas encore embarqués).

## Règle d'exploitation (ajoutée après incident du 2026-09-09)

**Aucun run CI réel (dispatch, render, consommation de minutes Actions) ne doit être
déclenché sans le GO explicite de l'opérateur.** Les gates G0-G3 sont des contrôles
automatiques de code : elles ne valident rien de créatif. La validation P1 (preview),
le rendu P2 en conditions réelles et la décision finale appartiennent au Warsmith seul.

## Règle de comparaison

Conserver toujours l'overlay du pack (copywriting.overlay_title) à côté du rendu.
Les frames de contrôle attendues : 0 s (hook pur, visage), 2.9 s (fin du hook),
3.1 s (overlay visible), un zoom frame-exact (ex. 8.62 s pour A01), dernière
seconde (fade_to_black).

## Colonnes minimales

Chaque ligne doit renseigner : pack, angle, segment, canvas, gates G0-G3,
P1 (preview validée), P2 (rendu CI), run GitHub Actions, décision.

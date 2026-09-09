# LACRIMAE dev10 — JOURNAL DE CAMPAGNES PUR

| Date | Pack | Angle | Segment (s) | Canvas | Gates G0-G3 | P1 Preview | P2 Rendu | Run CI | Décision |
|---|---|---|---|---|---|---|---|---|---|
| 2026-09-09 | pur-A01 | A01 | 737.48 → 767.48 | 9:16 | G0 ✓ G1 ✓ G2 ✓ G3 ✓ (sandbox + CI) | ✓ code (E2E local) | ✓ **RUN 34340044745 SUCCESS** — lac_pur_final.mp4 12.6 Mo, 857/857 frames | [34340044745](https://github.com/kioka8877-ux/LACRIMAE/actions/runs/34340044745) | PREMIER RENDU PUR RÉUSSI — validation visuelle opérateur à faire |

### Historique des runs CI (2026-09-09)

| Run | Résultat | Cause échec / note |
|---|---|---|
| [34338334121](https://github.com/kioka8877-ux/LACRIMAE/actions/runs/34338334121) | ❌ failure | codex injecté dans public/ au lieu de src/data/ → rendu sur route reveal (404 reveal_01.mp4). Fix a6b07f8 |
| [34339647085](https://github.com/kioka8877-ux/LACRIMAE/actions/runs/34339647085) | ❌ failure | codex.json committé avec clips[] vide → IndexError injection. Fix 4c7e524 |
| [34340044745](https://github.com/kioka8877-ux/LACRIMAE/actions/runs/34340044745) | ✅ **success** | Pack pur_A01 → yt-dlp → BridgeClipper → Remotion → 12.6 Mo |

Fixes notés pendant la mise en service : input `canvas` en string (le type choice avec « : » bloque le dispatch API), SFX désactivés par défaut (`sfx_available`, fichiers sfx/*.mp3 pas encore embarqués).
| — | — | — | — | — | — | — | — | — | — |

## Règle de comparaison

Conserver toujours l'overlay du pack (copywriting.overlay_title) à côté du rendu.
Les frames de contrôle attendues : 0 s (hook pur, visage), 2.9 s (fin du hook),
3.1 s (overlay visible), un zoom frame-exact (ex. 8.62 s pour A01), dernière
seconde (fade_to_black).

## Colonnes minimales

Chaque ligne doit renseigner : pack, angle, segment, canvas, gates G0-G3,
P1 (preview validée), P2 (rendu CI), run GitHub Actions, décision.

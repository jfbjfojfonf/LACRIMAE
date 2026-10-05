# Workflows CI — dev10-v2

Un seul workflow cible : `dev10_pur_render.yml` (pas encore pose — 0 code).

Flux prevu :

1. prepare — fetch packs PERTURABO + G0 dry-run + matrix
2. render LOOK — 1 asset = 1 job (F03_PICTOR)
3. Heisenberg — TEMPS, MP4 reel (F04)
4. aggregate — refus si un rendu manque
5. F05 / F06

Inputs cibles : `pack_filter`, `canvas`, `perturabo_branch`, `style`,
`max_parallel`, `max_duration`.

Aucun workflow heritage dev4 / dev7 / dev8 / dev9.

Voir `TRACKING/GUIDE_UTILISATION.md`.

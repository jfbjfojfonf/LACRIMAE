# Workflows CI — dev10-v2

Un seul workflow : `dev10_pur_render.yml`.

Flux :

1. prepare — fetch packs PERTURABO + G0-S + matrix
2. render — 1 asset = 1 job (F00_PUR → F03_PICTOR → F04_HEISENBERG)
3. aggregate — refus si un rendu manque (P-AGG / P-AUD)
4. F05 / F06 batch

Inputs : `pack_filter`, `canvas`, `perturabo_branch`, `style`,
`max_parallel`, `max_duration`.

Aucun workflow heritage dev4 / dev7 / dev8 / dev9.

Voir `TRACKING/GUIDE_UTILISATION.md`.

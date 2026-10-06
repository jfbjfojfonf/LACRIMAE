# Portes — `dev6-F`

| Porte | Quand | Critere | Si fail |
|---|---|---|---|
| G0 | avant F02 | `SHARED/IN/*.cube` present et lisible | stop, pas de rendu |
| G1 | F01 | chaque video 1920x1080, duree > 0 | skip item, manifeste sans elle |
| G2 | F02 | `ffmpeg` + filtre `lut3d` OK | job rouge |
| G3 | fin F02 | `OUT/` contient N mp4 = N items manifeste | pas de F05 |
| G4 | P4 | F05 qa_pass puis F06 qa_pass | pas de livrable |

G0 et token Modal sont **humains**. G1–G3 = code.

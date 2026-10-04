# CONFIG — Camera `dev-11`

> Params F02. Relancer SANGUINOR sans relancer OCULUS.

## Fichiers

| Fichier | Rôle |
|---------|------|
| `camera_defaults.json` | Deadzone, 1€, zoom, jitter, hold-last |

`F02_SANGUINOR/IN/camera_request.json` peut overrider ces valeurs par campagne. Absent = ce fichier.

F01 et F03 **ne lisent pas** ce dossier (sauf F03 pour `output_width/height` via le path déjà écrit).

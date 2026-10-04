# Scripts VPS (Windows / PowerShell)

A lancer **sur le VPS**, en RDP, depuis le clone du repo.

| Script | Role |
|---|---|
| `bootstrap.ps1` | Cree `C:\nexrender\...` et copie `apply_cc2.jsx` |
| `start-nexrender.ps1` | Lance server + worker (exige `NEXRENDER_SECRET`) |
| `run-pipeline.ps1` | F01 puis F02 (`-DryRun` pour tester sans AE) |

Ordre : bootstrap → (toi : AE, plugins, .ffx, .aep) → start-nexrender → une video dans `sources` → run-pipeline.

Feuille de route complete : `ROADMAP_HUMAIN.md` a la racine du repo.

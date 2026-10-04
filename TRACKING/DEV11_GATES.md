# DEV11 — Gates

Branche : `dev-11`
Source de vérité : ce fichier. Les scripts CUSTOS **lisent** ces règles ; ils ne les inventent pas.

Convention : **P-OC** Oculus, **P-SG** Sanguinor, **P-CX** Calix. Rouge = bloquant. Ambre = advisory, n'empêche pas le transit.

---

## Porte I — Brief (avant F01)

| Gate | Niveau | Vérification |
|------|--------|--------------|
| P-OC-0 | rouge | `F01_OCULUS/IN/job_request.json` présent, JSON valide |
| P-OC-1 | rouge | `target` ∈ `{face, nose, eyes}` |
| P-OC-2 | rouge | au moins 1 fichier `IN/clips/*.mp4` |
| P-OC-3 | rouge | chaque clip : H.264, audio optionnel, durée > 0 |
| P-OC-4 | ambre | resolution 1080×1920 recommandée ; autre 9:16 accepté si déclaré |
| P-OC-5 | rouge | stems uniques, charset `[a-zA-Z0-9._-]` |

---

## Porte II — Landmarks (sortie F01)

| Gate | Niveau | Vérification |
|------|--------|--------------|
| P-OC-10 | rouge | un `landmarks/<stem>.json` par clip IN |
| P-OC-11 | rouge | schema `dev11.landmarks.v1` |
| P-OC-12 | rouge | `fps` > 0, `frame_count` = nombre d'entrées `frames[]` |
| P-OC-13 | rouge | chaque frame : `t_s`, `detected` bool, `target` {x,y} normalisé 0–1 si detected |
| P-OC-14 | rouge | taux `detected=true` ≥ 0.85 sur le clip (sinon HOLD, pas de transit F02) |
| P-OC-15 | ambre | gaps > 12 frames consécutives sans visage → noter dans report |
| P-OC-16 | rouge | `LAC_CUSTOS --frigate F01 --mode check-out` PASS |

---

## Porte III — Camera (sortie F02)

| Gate | Niveau | Vérification |
|------|--------|--------------|
| P-SG-0 | rouge | F02 ne lit que `F02_SANGUINOR/IN/` |
| P-SG-1 | rouge | un `camera_path/<stem>.json` par stem landmarks |
| P-SG-2 | rouge | schema `dev11.camera_path.v1` |
| P-SG-3 | rouge | `frames[].cx, cy, zoom` présents, zoom ≥ 1.0 |
| P-SG-4 | rouge | crop 9:16 toujours dans le cadre source (aucun débord) |
| P-SG-5 | rouge | jitter : déplacement centre frame-à-frame médian sous seuil `CONFIG/camera_defaults.json` |
| P-SG-6 | rouge | deadzone respectée : si cible dans la zone morte, camera **immobile** |
| P-SG-7 | rouge | hold-last si `detected=false` : pas de jump au centre frame |
| P-SG-8 | ambre | zoom ne varie pas plus vite que `zoom_max_delta_per_s` |
| P-SG-9 | rouge | `LAC_CUSTOS --frigate F02 --mode check-out` PASS |

---

## Porte IV — Calice (sortie F03)

| Gate | Niveau | Vérification |
|------|--------|--------------|
| P-CX-0 | rouge | F03 ne lit que `F03_CALIX/IN/` |
| P-CX-1 | rouge | un `tracked/<stem>.mp4` par camera_path |
| P-CX-2 | rouge | H.264 yuv420p, 9:16, même durée ±1 frame que la source |
| P-CX-3 | rouge | audio : stream copy si source a de l'audio ; silence explicite sinon (pas d'omission furtive) |
| P-CX-4 | rouge | `calix_manifest.json` liste tous les stems, chemins relatifs, hashes |
| P-CX-5 | rouge | faststart (`+faststart`) |
| P-CX-6 | rouge | zip / artifact refusé si **un** stem manque (agrégation stricte, doctrine PUR) |
| P-CX-7 | rouge | `LAC_CUSTOS --frigate F03 --mode check-out` PASS |

---

## Isolement (toutes portes)

| Gate | Niveau | Vérification |
|------|--------|--------------|
| P-ISO-1 | rouge | aucun script de frégate n'importe un path `F0[123]_*/OUT` d'une sœur |
| P-ISO-2 | rouge | pas d'accès réseau hors Modal / artifacts déclarés |
| P-ISO-3 | rouge | pas de secret LLM écrit dans un JSON de campagne |

---

## GitHub Actions / Modal

| Gate | Niveau | Vérification |
|------|--------|--------------|
| P-CI-1 | rouge | runner Actions : tests contrat + dispatch Modal. **Interdit** : decode campaign MP4 |
| P-CI-2 | rouge | Modal token en secret, jamais dans le repo |
| P-CI-3 | ambre | timeout Modal par clip documenté dans le workflow |

---

## HOLD vs REFUS

- **HOLD** : landmarks trop pauvres (P-OC-14). Clip mis de côté. Les autres stems passent.
- **REFUS** : schema cassé, isolement violé, agrégat incomplet. Job entier stoppé.

Le Directeur (humaine / Magos) tranche les ambre. Les rouge ne se négocient pas dans le code.

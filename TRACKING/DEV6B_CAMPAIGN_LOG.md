# LACRIMAE dev6-B — JOURNAL DE CAMPAGNES

Ce journal conserve une ligne par campagne et ne doit jamais remplacer une tentative précédente. Les sorties doivent toujours provenir de la source originale de la campagne.

| Date | Campagne | Source | Profil | Preset | Entrée | Sortie | Statut | Gate critique | Décision |
|---|---|---|---|---|---|---|---|---|---|
| 2026-08-28 | `v2_original_5s_run2` | `rife_input_5s.mp4` | `hdr_imperator` | non défini | 30 FPS / 1920×1080 | 120 FPS / 1920×1080 | SEALED | F08 transparent | Référence v2 à améliorer avec F09 |
| 2026-09-06 | `v2_tiktok4k_test` | `v2_original_5s_run2_final.mp4` | F09 preview v2.2.0 | `tiktok4k` (TikTok 4K) | 120 FPS / 1920×1080 (5 s) | 30 FPS / 720p, 1.1 Mo | OK | Mesures : chroma +43%, lum +12% vs source | Preset AE-parity (sharpen 3.2, exp 0.6, sat 1.45, vib 40, vign 75). Fixes: vibrance direction, contrast pivot adaptatif, glow intensity Python |
| 2026-09-06 | `v2_cleancc_test` | `v2_original_5s_run2_final.mp4` | F09 preview v2.2.0 | `cleanCC` (Clean CC) | 120 FPS / 1920×1080 (5 s) | 30 FPS / 720p, 0.9 Mo | OK | Mesures : chroma +15%, lum +7%, contraste préservé | Preset "correction naturelle" (glow 0, exp 0.35, sat 1.25, vign 50, clarity via detailReveal). Sortie : `output/v2_cleancc_test.mp4` |
| 2026-09-07 | `v2_polyester_test` | `v2_original_5s_run2_final.mp4` | F09 preview v2.2.0 | `polyester` (Polyester v2 — retune look réel) | 120 FPS / 1920×1080 (5 s) | 30 FPS / 720p, 1.2 Mo | OK | Mesures : chroma +39%, lum +9%, netteté +73% (variance Laplacien), noirs p5 crushés ~0 vs source (chroma mesuré max−min, indépendant de la luminosité) | Retune après retour utilisateur « juste plus lumineux / banal » : look polyester réel (visuel uniquement, zéro audio/beats) : preset `polyester` (sharpen 4.2 crunchy, contraste 1.42 noirs crushés, sat 1.5, vib 40, glow soyeux 0.75/80, exp 0.08, warmth 1.02, vign 45). Sortie : `output/v2_polyester_test.mp4` |
| 2026-09-07 | `v2_polyester_phase2_test` | `v2_original_5s_run2_final.mp4` | F09 preview v2.3.0 (moteur texture) | `polyester` + microContrast 55 / grain 32 | 120 FPS / 1920×1080 (5 s) | 30 FPS / 720p, 2,3 Mo | OK | Texture (passe-haut RMS hors contours) +37% vs source (+18% vs phase 1), netteté (variance Laplacien) +92%, chroma +34%, lum ≈ inchangée vs phase 1 | Phase 2 — diagnostic confirmé : la limite venait du moteur (sharpen edge-aware qui protège les zones plates = zéro texture), pas de la technologie. Nouvelles couches : micro-contraste large rayon (parité AE Unsharp Mask 20px, sans masque de contours) + grain fin mono­chromatique pondéré luminance, seed déterministe par frame. Sliders `Micro Contrast` et `Texture Grain` ajoutés preview + rendu. Sortie : `output/v2_polyester_test.mp4` |

## Règle de comparaison

Une comparaison doit conserver la source, l’intermédiaire RIFE, la sortie restaurée et la sortie finale. Les variantes doivent utiliser le même segment, le même nombre de frames et le même point de départ afin que la différence visuelle soit attribuable au preset ou à la Frégate testée.

## Colonnes minimales à compléter

Chaque nouvelle ligne doit renseigner le hash source, le workspace Modal, les versions de modèles, le profil AUSPEX, le stride facial, les paramètres Motus, le preset F09, la présence audio et les décisions G0 à G9. Une ligne sans ces données reste `NEEDS_REVIEW`.

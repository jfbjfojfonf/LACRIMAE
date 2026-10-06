# F03 PREVIEW — dev10 (mode PUR)

F03_PREVIEW est la salle de contrôle interactive du Short LACRIMAE. En 2026-10-06, les onglets Ranking et Reveal sont masqués. Le mode par défaut est **pur_pack**. Le double-clic sur la vidéo pose le logo (conservé). Zoom respiration et zooms ponctuels sont désactivés.

Le moteur ranking/reveal reste dans le code (héritage) mais n'est plus routé depuis l'UI.

## Mode de fonctionnement

| | dev8 (Reveal Compilation) | dev9 (Ranking Compilation) |
|---|---|---|
| **Concept** | Others vs This One | Clips numérotés du rang N au rang 1 |
| **Clips** | 3-6 clips | 3-10 clips |
| **Numéros** | Pas de numéros | Permanents (toujours visibles) |
| **Labels** | Texte par clip | Word-by-word avec couleur par mot |
| **Musique** | Loop + drop | Pas de musique de fond |
| **Audio clips** | Muted | Toggle on/off |
| **SFX** | Non | Par transition + rang #1 spécial |
| **Titre** | Simple | Word-by-word avec couleur |

## Panneau Ranking

### Apparence générale

| Contrôle | Type | Plage | Description |
|----------|------|-------|-------------|
| Taille numéros | Slider | 0.3x - 3x | Taille des "4.", "3.", etc. |
| Taille écritures | Slider | 0.3x - 3x | Taille des labels |
| Position liste X% | Slider | 0-100% | Position horizontale de la liste |
| Position liste Y% | Slider | 0-100% | Position verticale de la liste |
| Espacement rangs | Slider | -10 à 30 | Espace vertical entre rangs |
| 🔊 Son des clips | Checkbox | on/off | Jouer l'audio des clips |

### Titre

| Contrôle | Type | Description |
|----------|------|-------------|
| Mot 1-4 | Input + Color picker | Chaque mot a sa couleur |
| Taille titre | Slider | Taille du titre |
| Position haut% | Slider | Position verticale haut |
| Position bas% | Slider | Position verticale bas |
| Position X% | Slider | Position horizontale |

### Par rang

| Contrôle | Type | Description |
|----------|------|-------------|
| Label | Textarea | Le texte du rang (1-4 mots) |
| Couleur # | Color picker | Couleur du numéro |
| Taille # | Slider | Taille du numéro |
| Taille label | Slider | Taille du texte |
| Durée | Slider | Temps d'apparition (secondes) |
| SFX | Checkbox + Input | Son de transition |

## Composition Remotion

La composition `RankingCompilationComposition` dans `_rankingComposition.jsx` :

- **Numéros** : Permanents, rendus de bout en bout
- **Labels** : Apparaissent du bas vers le haut (rank N → rank 1)
- **Clip** : Plein écran, un à la fois
- **Titre** : Persistant, word-by-word
- **SFX** : Joue quand chaque label apparaît

## Contrat avec F00 et F04

```text
F00-E (clips) + F00-F (ranking)
    │ reveal_sources.json + ranking_manifest.json
    ▼
F03 Preview (validation)
    │ codex.json (ranking_compilation)
    ├──► Preview interactive
    └──► F04 Render → short_final.mp4
```

## Assets

```text
F03_PREVIEW/CODEBASE/public/
├── codex.json                ← manifeste principal
├── ranking_manifest.json     ← données ranking
├── clips/
│   ├── reveal_01.mp4         ← Rank N
│   ├── reveal_02.mp4         ← Rank N-1
│   └── ...
├── sfx/
│   ├── impact.mp3            ← SFX transition
│   └── king_reveal.mp3       ← SFX rang #1
└── audio/                    ← musique (optionnel)
```

## Notes techniques

- Les clips doivent être **H.264** (pas H.265/HEVC)
- F00-E garde l'audio d'origine des clips (pas de `-an`)
- Chaque clip est dans un `<Sequence>` Remotion avec `durationInFrames` limité
- Le `<Audio>` séparé joue le son du clip pendant sa durée
- Le rang 1 a un effet spécial (glow doré + shake)
- Pas de musique de fond dans dev9 (contrairement à dev8)

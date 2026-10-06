# F03 PREVIEW — TRACKING (récupération & correctifs)

> Date : 2026-08-08

## Contexte

Le code source du preview `F03_PREVIEW/CODEBASE` a été perdu après un reset du
sandbox (jamais poussé sur GitHub). Il a été **entièrement récupéré** depuis le
sandbox d'origine encore vivant, via son serveur Vite :
`https://5173-7b5fcbca1aa0247f.monkeycode-ai.live`

Sources originales extraites depuis les sourcemaps embarquées par Vite
(`sourcesContent`) — fichiers propres, pas du code transformé.

## Fichiers récupérés

```
src/App.jsx                  (829 lignes)
src/main.jsx
src/preview/OmniComposition.jsx   (548 lignes)
src/preview/BloomText.jsx         (303 lignes)
public/codex.json
public/clip_001.mp4               (11,3 Mo — 1920x1080)
public/logo.png                   (4,2 Mo)
public/backgrounds/               (7 PNG + manifest.json)
package.json / index.html / vite.config.js
```

## Correctifs appliqués

### 1. confirmLogoPlacement (App.jsx) — BUG PRINCIPAL
Trois `updateSession('logo', …)` séquentielles lisaient le même `session`
obsolète (closure) et React les batchait : seule la dernière (`y_pct`) survivait.
`position: 'custom'` et `x_pct` étaient **perdus** → le logo restait à son
preset. Remplacé par une **mise à jour atomique** via `setSession(s => …)`.

### 2. Priorité du logo (OmniComposition.jsx)
`logo={clip.logo || session.logo}` → `logo={session.logo || clip.logo}`.
Dès qu'un clip définissait un `logo`, les réglages de session (custom) étaient
ignorés.

### 3. logo.png
Le fichier était absent de la copie locale (404 → « image cannot be decoded »).
Récupéré depuis le sandbox.

## Vérification E2E (puppeteer, headless chromium)

Flux : double-clic vidéo → modal → Oui → position custom.
- Modal ouverte : OK
- Marqueur au point cliqué (70 / 29.8) : OK
- Select position → `custom` : OK
- Codex exporté : `session.logo = { position: 'custom', x_pct: 70, y_pct: 29.8 }` : OK

## Améliorations (2026-08-08)

### 4. Onglet « 🎬 Vidéo » + centrage vertical (session)
Nouvel onglet dédié (pour accueillir d'autres particularités vidéo). Slider
`session.video.offset_y` (-20 % à +20 %, pas de 0,5) appliqué en
`translateY(%)` au `<Video>` (OmniComposition L2). Réglage **session** →
appliqué à tous les clips (règle). `+` = bas, `-` = haut.

### 5. Échelle du logo élargie
Slider « Taille du logo » : `max` 60 → **90** (= 1,5 × l'ancien max). Min 5
conservé, pas 1. `LogoOverlay` gère déjà `width_pct` en % de la largeur.

## Vérification E2E (suite)
- Balise (régression) : OK
- Onglet Vidéo : présent, offset → `-12.5 %` reflété dans le label
- Export : `session.video.offset_y = -12.5` + `session.logo` custom conservés
- Slider logo `min=5 max=90` : OK

## Points d'attention (non corrigés, à trancher)

- **Ratio incohérent** : `clip_001.mp4` est du 1920x1080 (16:9 paysage) mais le
  codex le déclare 1080x1920 (9:16 portrait). Rendu en `object-fit: cover`
  (recadré). Le mapping clic→logo reste cohérent, mais le cadrage vidéo est à
  valider côté pipeline.
- **Zoom** : le logo est posé en % de la composition, il ne suit pas le zoom /
  pan de la vidéo (`zoom_keyframes`). Choix à valider.
- Le preview n'est **pas poussé sur GitHub** (commit à faire).

## dev8 — Reveal Compilation (2026-08-28)

La branche `dev8` est dédiée au format `OTHERS VS THIS ONE`. F00-E reçoit directement une à six sources, extrait les plages IN/OUT opérateur, applique le miroir horizontal après extraction et produit des clips H.264 verticaux sans audio. F00-MUSIC reste une étape séparée d’analyse audio. F03 reste la seule Preview de montage ; F04/Pictor rend le codex validé.

Éléments implémentés dans cette itération :

- `src/preview/revealCompilation.js` : normalisation du manifeste, scènes, sources, mouvements, rôles `other`/`final_reveal` et shake final.
- `App.jsx` : chargement de `reveal_sources.json`, onglet Reveal, textes globaux, durées par scène, transitions `with_sfx`/`silent`, mouvements et paramètres du reveal.
- `OmniComposition.jsx` Preview et PICTOR : rendu six sources, labels OTHERS/THIS ONE, audio, mouvement organique, assombrissement et shake vertical.
- Export : `session.review_mode: reveal_compilation` et `reveal_manifest` sont conservés dans le codex.
- Workflows isolés : `.github/workflows/dev8_f00e.yml`, `.github/workflows/dev8_f00_music.yml` et `.github/workflows/dev8_reveal_render.yml`.

Validation déjà effectuée :

- `python3 -m py_compile` sur F00-E et ses tests : OK.
- `pytest -q F00_INGEST/tests/test_reveal.py F00_INGEST/tests/test_manifest.py F00_INGEST/tests/test_motion_slow.py` : **9 tests réussis**.
- `npm run build` dans F03 Preview : OK.
- `npm run check` dans F03 PICTOR : OK ; composition existante listée à 300 frames.

Limite volontaire : dev8 ne contient pas de pack média réel. Le premier test réel doit fournir un artifact F00-E contenant `reveal_sources.json` et `clips/*.mp4`, ainsi qu’un artifact F00-MUSIC contenant `music_timeline.json` et la piste audio.

## dev9 Ranking — 2026-08-28

État : intégration initiale terminée. F00-E est inchangé. F00-F produit `ranking_manifest.json` à partir des clips F00-E. F03 charge le mode `ranking_compilation`, expose l’onglet Ranking et permet les corrections du titre, des labels, des durées, des positions, des tailles, des couleurs et des SFX optionnels. PICTOR reprend le même normaliseur et le même renderer.

Gates validés : syntaxe F00-F, tests unitaires F00-F et Reveal (`7 passed`), build Vite F03. Le check Remotion PICTOR a été remplacé par un bundling esbuild local lorsque le téléchargement de Chromium Headless Shell n’est pas disponible ; le bundling PICTOR et la compilation Python sont valides.

À valider sur un test réel : six clips F00-E, au moins une source horizontale, un miroir, un SFX activé et un rang 1 final.

## 2026-10-06 — Preview PUR : ranking / reveal / zoom masqués

La preview dev10 est conservée. Changements opérateur uniquement :

- Onglets Ranking et Reveal retirés de la barre. Le mode forcé est `pur_pack`.
- Zoom respiration et zooms ponctuels désactivés (preview). Miroir / crop / speed inchangés.
- Double-clic sur la vidéo pour poser le logo : **conservé** (modale Oui/Non, `session.logo.position = custom`). Le logo s'affiche aussi en mode PUR.
- PICTOR n'est pas lancé depuis cette preview. Validation visuelle P1 = GO Warsmith.

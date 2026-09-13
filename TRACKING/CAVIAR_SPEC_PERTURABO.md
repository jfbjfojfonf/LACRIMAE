# SPEC CAVIAR 99 % — Contrat de montage narratif entre PERTURABO et LACRIMAE

**À** : PERTURABO (le cerveau créatif — analyse virale, composition des packs)
**De** : LACRIMAE / F03 (le bras armé — gates, rendu, physique des effets)
**Date** : 2026-09-13 — **Statut** : NOTE DE CADRAGE (aucune implémentation lancée — GO opérateur requis à chaque étape, règle du 09-09)

---

## 0. Pourquoi cette note existe

Notre production actuelle sort un **clip propre** : bonne découpe, bon cadre 9:16,
audio sain, flashs de transition, SFX aux moments marqués. Mais c'est un clip
**sans montage narratif** — la forme « pureté 60 % » du marché : un extrait bien
habillé, pas une histoire. Cette note définit le contrat complet pour passer à la
« pureté 99 % » SANS casser ce qui marche : PERTURABO reste le décideur créatif,
LACRIMAE reste un exécutant physique avec des portes bloquantes, l'opérateur tranche
au gate.

---

## 1. L'analogie fondatrice (la lire avant tout le reste)

**Walter White** : la pureté, c'est tout. La concurrence coupe du flux et colle des
sous-titres — chimie à 60 %. Nous visons le 99 % : pas plus d'effets, une **précision
diabolique du dosage**. Le caviar naît de la milliseconde et de la règle, jamais de
l'empilement.

**Le flash decamétronique** : « ton flash est lent, mon flash est plus rapide, plus
de pognon. » Chez nous : le flash blanc n'est pas une décoration, c'est un
**marqueur de changement d'état** (histoire → réaction, réalité → meme). Il dure
3-5 frames, il est COUPLÉ à un SFX sur la même frame exacte, et il se pose à
**l'ENTRÉE d'un B-roll uniquement — jamais à la sortie** (la sortie se fait en Flow
Cut : le mouvement du B-roll lui-même ramène l'œil au gameplay ; flasher deux fois
= stroboscope = le marqueur perd son pouvoir).

**Les 4 éléments seulement** (la réduction Heisenberg) : cuts, B-roll/memes,
SFX, flash blanc. Tout le reste est interdit tant que ces quatre-là ne sont pas
maîtrisés au milliseconde près. Un plat simple exécuté parfaitement bat un plat
complexe exécuté moyennement.

---

## 2. État des lieux LACRIMAE — ce qui existe déjà (perturabo, sache ce que tu as)

| Concept « Caviar » | État dans LACRIMAE (dev10) |
|---|---|
| JSON qui dicte le comportement des calques au pixel/frame | ✅ `pur_manifest.json` (dev10.pur.v1/v2) — le rendu Remotion n'invente rien |
| SFX calés au millième de seconde | ✅ `entry.sfx_list[]` (moment_frame, volume) — rendus sous la voix |
| Punch-ins / zooms sur moments clés | ✅ `entry.zooms[]` + swell continu (montée douce → tenue → retour à `scale_from`, zéro discontinuité) |
| Marqueur de changement d'état | ✅ `entry.zooms[].white_flash` — flash blanc 5 frames symétrique |
| Gates qualité qui bloquent | ✅ G0-G3 + agrégation stricte (refus de publier un bundle incomplet — prouvé run 34721632577) |
| Anti-détection | ✅ mirror/crop/speed — interrupteurs workflow (`fx_mode`, `mute_bg`) |
| Orchestration parallèle | ✅ Workflow matrix GitHub Actions, 1 asset = 1 job, jusqu'à 20 |
| Protocole de preuve A/B | ✅ Mini-rendus 6 s d'isolation (prouvé run 34744097428 : synchro A/V rétablie) |

**Ce qui manque — le seul vrai goulot** : une **couche de décision** entre l'ingest
et le rendu. Aujourd'hui les moments (zooms, SFX, accroches) sont écrits à la main
dans les packs par PERTURABO. Demain : enrichis par analyse de signal
(silences, amplitudes, timestamps de mots) et **validés par l'opérateur au gate**.

---

## 3. La grammaire des 7 cuts — rôle, déclencheur, faisabilité

| # | Cut | Effet psychologique | Déclencheur mathématique | Faisabilité | Statut v1 Caviar |
|---|---|---|---|---|---|
| 1 | **Jump Cut** | Supprime l'attente, crée le rythme | Silence > 250 ms → coupe pile à la reprise d'amplitude vocale (percussion) | 🟢 CPU | **Implémenté Phase 1** |
| 2 | **Smash Cut** (audio) | Électrochoc, casse la routine | `is_climax` → ducking −12 dB (ou 0) pendant 0,5-1 s | 🟢 CPU | **Implémenté Phase 1** |
| 3 | **Pacing Cut** | Gère l'énergie globale (climax/release) | Longueurs de plans : serré (< 2 s) sur la montée, lent (2,5-3,5 s) sur la résolution | 🟢 CPU | **Implémenté Phase 1** |
| 4 | **Cut dans l'action** (punch-in) | Le cerveau suit le geste, rate le cut | Pic d'amplitude vocale ou de mouvement → zoom 1.15-1.3× sur 0,5-0,8 s, courbe douce | 🟡 CPU (optical flow léger) | Phase 2 |
| 5 | **Flow Cut** | L'œil glisse sans friction | Points d'intérêt X/Y maintenus de part et d'autre du cut | 🟠 Dur (webcam composée dans le flux) | Phase 3+ |
| 6 | **Match Cut** | « Ces deux choses appartiennent ensemble » | Similarité visuelle/phonétique entre deux plans | 🔴 GPU + bibliothèque | Phase 4 |
| 7 | **Large/Moyen/Gros plan** | Structure et clarté | Nécessite sources séparées (webcam + jeu) | 🔴 Impossible sur un VOD composite | Hors v1 |

> **Décision d'architecture** : les cuts 1-3 représentent ~80 % de la rétention
> gagnable et tournent sur le CPU de GitHub Actions (segments de 30 s seulement —
> pas de GPU/Modal nécessaire à ce stade). Les cuts 5-7 sont reportés, PAS abandonnés.

---

## 4. La doctrine — qui décide quoi (non négociable)

| Rôle | Qui | Décide | Ne fait PAS |
|---|---|---|---|
| **Cerveau créatif** | PERTURABO | Le **OÙ** et le **QUOI** : choix du segment, l'accroche (Narrative Reframing), `is_climax`, moments B-roll, frontières à flasher — selon SES règles de viralité | La physique des effets, le rendu, les gates |
| **Bras armé** | LACRIMAE | Le **COMMENT** : courbes, durées, synchro, budgets, portes bloquantes, agrégation | Choisir un segment, écrire une accroche, déplacer un zoom, relire/relancer un run, contredire une décision tranchée de l'opérateur |
| **Opérateur** | Warsmith | Validation au gate ; les décisions créatives finales (l'accroche reste un choix humain — l'analyse dit OÙ est la tension, pas QUOI écrire) | — |

L'analyse de signal **enrichit** les décisions de PERTURABO, elle ne les remplace pas.
Le montage narratif automatisé qui décide seul = la chimie à 60 % avec un budget plus gros.

---

## 5. Ce que PERTURABO devra ajouter aux packs (schéma JSON cible)

**Principe : additions OPTIONNELLES et rétrocompatibles.** Le schéma v2 tolère les
packs v1 (champs absents = comportement actuel inchangé). Validation G0 étendue
(refus si champ présent mais invalide — jamais si absent).

```jsonc
{
  "montage_instructions": {
    "segment": { "...": "inchangé" },
    "overlay": { "...": "inchangé — le texte d'accroche reste écrit par PERTURABO" },

    // ── NOUVEAU : la partition narrative ──
    "narrative": {
      "hook_type": "climax_first | reframe | question",
      // hook_type=climax_first : le clip commence in media res, l'intro est coupée
      // hook_type=reframe : l'overlay pose un enjeu fictif (le POV) dès la frame 0
      "is_climax": [14.2, 27.8],          // secondes — SMASH CUT + ducking + flash autorisé ici
      "resolution_at": 24.0,              // secondes — à partir d'ici : pacing lent, RIEN ne s'ajoute
      "energy_curve": ["rise", "peak", "fall"]  // gestion du tempo par LACRIMAE
    },

    "zooms": [ { "...": "inchangé",
                 "cause": "climax | action | manual" } ],  // cause optionnelle (traçabilité)

    "broll": [                           // NOUVEAU — v1 tolère l'absence totale
      {
        "asset_file": "broll/shrek_cut.png",   // fichier fourni dans le pack
        "start_sec": 8.5,
        "duration_frames": 36,           // ≤ 45 (1,5 s à 30 fps) — GATE BLOQUANT
        "entry_flash": true,             // flash blanc à l'ENTRÉE (jamais à la sortie)
        "sfx": "impact",                 // OBLIGATOIRE si entry_flash — GATE BLOQUANT
        "eye_line_match": true           // hint Flow Cut pour la sortie (Phase 3)
      }
    ],

    "audio_design": {                    // NOUVEAU — optionnel
      "duck_at_climax": { "db": -12, "duration_sec": 0.8 },
      "silence_before_punchline": true   // 0,3-0,5 s de silence total avant la chute
    }
  }
}
```

**Budgets anti-saturation (les portes les bloquent, pas des warnings)** :

| Ingrédient | Budget / clip de 30 s | Porte |
|---|---|---|
| B-roll / memes | 2-3 max, chacun ≤ 45 frames, jamais pendant la résolution | P-CAV2 → rouge si dépassé |
| Flash blanc | 2-3 max, espacés de ≥ 1,5-2 s, ENTRÉE de B-roll uniquement | P-CAV3 → rouge |
| Punch-ins | 3-4 max, espacés de ≥ 2 s | P-CAV2 |
| SFX | 1 par événement visuel, même frame exacte, sous la voix | P-CAV3 |
| Silence / ducking | 1-2 (avant punchline, au smash) | P-CAV2 |
| **Règle de l'élément unique** | Jamais 2 événements visuels forts sur la même frame (meme + flash de zoom, meme + texte qui apparaît…) | P-CAV3 |
| Respiration | La source occupe ≥ 60-70 % de la timeline | Audit G0 |

---

## 6. Ce que LACRIMAE commence à construire (dès GO de l'opérateur)

**Nouveau module : le DIRECTEUR** (`F03_PICTOR/CODEBASE/tools/narrative_director.py` ou
équivalent dans F00) — analyse le segment téléchargé et produit un JSON d'analyse :

1. **Carte des silences** : ffmpeg `silencedetect` (seuil 250 ms) → timestamps de trim → **PROPOSITION de Jump Cuts** (appliqués seulement si PERTURABO/manifeste les valide — le bras armé propose, le cerveau dispose, l'opérateur valide).
2. **Carte des amplitudes** : pics vocaux (cris, montées de ton) → ancres pour punch-ins et candidats `is_climax` à soumettre.
3. **Timestamps de mots** : faster-whisper **CPU** (30 s de segment = ~15-30 s de traitement, pas de GPU) → mots clés + fin de phrase → position de la punchline pour le timing de l'overlay (l'enjeu reste visible jusqu'au climax, puis s'efface — Point de Rupture).
4. **Gates P-CAV** (bloquantes, culture maison) : budgets ci-dessus + synchro flash/SFX + règle de l'élément unique.
5. **Protocole de preuve** : tout nouveau comportement passe d'abord en mini-rendus 6 s d'isolation (méthode éprouvée), comparaison A/B avant run complet.

**Ce que LACRIMAE ne fait PAS** : toucher au `speed` (décision opérateur 1.05),
déplacer les moments marqués par PERTURABO, écrire des accroches, décider du style.

---

## 7. Ce qui ne change PAS ( acquis verrouillés)

- Vocabulaire : **asset** = A01/A02/… (1 vidéo finale = 1 job), **pack** = l'ensemble.
- Le moteur est un exécutant : le manifeste dicte, Remotion obéit, rien n'est codé en dur.
- Flash blanc : rendu 5 frames symétriques, TOUJOURS actif, entrée de B-roll uniquement.
- `fx_mode=off` disponible comme mode « clip normal » (proofs, comparaisons).
- Rituel : mini-rendus d'isolation → validation opérateur → run tous assets → lien de suivi.
- L'opérateur suit les runs ; le bras armé code, commite, pousse, déclenche, donne le lien.

---

## 8. Ordre d'exécution proposé (chaque étape = GO opérateur séparé)

| Phase | Contenu | Qui porte | Prérequis |
|---|---|---|---|
| **0** | Cette note validée + schéma JSON v2 acté | PERTURABO + opérateur | Cette note |
| **1** | Jump Cuts (silences) + Smash audio (`is_climax` ducking) + Pacing + timing overlay (rupture au climax) — le SQUELETTE | LACRIMAE | Packs avec `narrative.is_climax` |
| **2** | Punch-in intelligent (pics vocaux → zooms, courbe swell existante) | LACRIMAE | Données d'amplitude |
| **3** | B-roll/memes (bibliothèque + gate 45 frames + flash d'entrée + SFX couplé) | PERTURABO fournit les assets, LACRIMAE la mécanique | Bibliothèque d'assets validée par l'opérateur |
| **4** | Flow cut / Match cut | LACRIMAE | Preuves de rétention des phases 1-3 |

**Ce dont PERTURABO a besoin pour démarrer la Phase 1** :
1. Validation (ou amendement) du schéma JSON §5.
2. Un pack de test avec `narrative` rempli (1 accroche reframe, 1-2 `is_climax`, `resolution_at`).
3. Confirmation : l'accroche et le choix du segment restent les siens, l'analyse propose le reste.

---
*LACRIMAE — le bras armé n'interprète pas : il exécute, il bloque, il prouve.*
*Warsmith tranche. PERTURABO crée.*

/* ═══════════════════════════════════════════════════════════════════
   caviarRender.js — GROUPE 3 : moteur de rendu narratif (HEISENBERG)
                 + GROUPE 2 v2 : panneau possédé par la partition F00D

   Consomme le bloc `caviar` du manifeste dev10.pur.v1 (décisions
   PERTURABO prises depuis le caviar_manifest émis par la frégate) et le
   transforme en primitives de rendu Remotion :
     - jump cuts : segments contigus timeline→source (silences trims)
     - punch-ins : courbe attack/hold/release — jamais de zoom libre
     - B-roll numéroté : overlay plein cadre (voix continue) + flash
       blanc à l'ENTRÉE uniquement + SFX couplé sur la même frame
     - smash audio : ducking musical au climax (exporté, utilisé dès
       qu'une piste musicale existe dans le mode courant)

   Doctrine (spec CAVIAR §1, §4, §5) :
     - flash blanc à l'ENTRÉE de chaque B-roll, JAMAIS à la sortie
     - SFX uniquement à l'entrée des B-rolls (règle anti-saturation)
     - pas de fichier B-roll résolu dans le pack = pas de B-roll
     - Budget d'Attention vérifié ICI AUSSI (double barrage) : si le
       pack dépense au-delà de 55 u ou dépasse un cap, les événements
       excédentaires sont DÉPOSÉS (les plus chers d'abord, les derniers
       dans le temps) et le gate passe ROUGE — le rendu reste propre,
       jamais saturé.
     - fx_mode=off (« clip normal », décision Warsmith) : punch-ins,
       flashs et B-rolls désactivés ; les jump cuts RESTENT (ce sont
       des coupes de montage, pas des effets).

   Zéro dépendance Remotion/React ici : fonctions pures testables en
   Node (npm run test:caviar). Le budget est passé en argument — la
   source de vérité unique reste HEISENBERG/caviar_budget.json, dont
   le   miroir data/caviar_budget.json est vérifié par caviar_gate.py.
   ═══════════════════════════════════════════════════════════════════ */

import { resolvePanelSpec } from './caviarPanel.js';

/** Bloc caviar brut (pack PERTURABO) → forme normalisée.
 *  `extra` (v2 F00D : resolution_at, run_id, budget_state…) est transporté
 *  tel quel — les événements gardent leurs champs additionnels. */
export function normalizeCaviarBlock(raw) {
  const r = raw && typeof raw === 'object' ? raw : {};
  return {
    enabled: r.enabled === true,
    source: String(r.source || 'heisenberg'),
    jump_cuts: Array.isArray(r.jump_cuts) ? r.jump_cuts : [],
    punchins: Array.isArray(r.punchins) ? r.punchins : [],
    brolls: Array.isArray(r.brolls) ? r.brolls : [],
    smash_audio: Array.isArray(r.smash_audio) ? r.smash_audio : [],
    extra: r.extra && typeof r.extra === 'object' ? r.extra : undefined,
  };
}

/** Comptage + dépense du pack en unités — MÊMES chiffres que la frégate. */
export function verifyCaviarBudget(events, budget) {
  const ev = (budget && budget.events) || {};
  const count = (ev2, key) => (Array.isArray(ev2[key]) ? ev2[key].length : 0);
  const counts = {
    broll: count(events, 'brolls'),
    smash: count(events, 'smash_audio'),
    punchin: count(events, 'punchins'),
    jumpcut: count(events, 'jump_cuts'),
  };
  const spend =
    counts.broll * (ev.broll?.cost_units ?? 12) +
    counts.smash * (ev.smash?.cost_units ?? 8) +
    counts.punchin * (ev.punchin?.cost_units ?? 6) +
    counts.jumpcut * (ev.jumpcut?.cost_units ?? 1);
  const caps = {
    broll: { count: counts.broll, max: ev.broll?.max_per_clip ?? 3 },
    smash: { count: counts.smash, max: ev.smash?.max_per_clip ?? 2 },
    punchin: { count: counts.punchin, max: ev.punchin?.max_per_clip ?? 4 },
    jumpcut: { count: counts.jumpcut, max: ev.jumpcut?.max_per_clip ?? 8 },
  };
  const reasons = [];
  const maxSpend = budget?.max_spend_units ?? 55;
  const total = budget?.total_budget_units ?? 100;
  if (spend > maxSpend) reasons.push(`dépense ${spend}u > ${maxSpend}u (Budget d'Attention)`);
  for (const [k, c] of Object.entries(caps)) {
    if (c.count > c.max) reasons.push(`cap ${k} dépassé : ${c.count} > ${c.max}`);
  }
  return {
    ok: reasons.length === 0,
    spend_units: spend,
    max_spend_units: maxSpend,
    total_units: total,
    breathing_units: total - spend,
    counts,
    caps,
    reasons,
  };
}

/** Ordre d'abandon quand le pack sature : le plus CHER d'abord, puis le
 *  plus TARDIF dans le temps (la respiration gagne, le début du clip vit). */
const DROP_PRIORITY = [
  ['broll', 'brolls', 12],
  ['smash', 'smash_audio', 8],
  ['punchin', 'punchins', 6],
  ['jumpcut', 'jump_cuts', 1],
];

/** Point temporel d'un événement (sec) — pour déposer le plus tardif. */
const eventTime = (key, e) =>
  key === 'jump_cuts' ? Number(e.cut_at_sec || 0) : Number(e.at_sec || 0);

/** Double barrage : retire les événements excédentaires (caps + dépense)
 *  et résout les conflits d'élément unique (note §3.5 : jamais 2 événements
 *  visuels forts sur la même frame — un punch-in sur la fenêtre d'un panneau
 *  est déposé, le panneau est l'événement fort).
 *  Retourne les événements appliqués, les déposés (avec raisons) et le
 *  verdict du gate rendu. */
export function enforceCaviarBudget(block, budget, ctx = {}) {
  const fps = Math.max(1, Number(ctx.fps || 30));
  const applied = {
    jump_cuts: [...block.jump_cuts],
    punchins: [...block.punchins],
    brolls: [...block.brolls],
    smash_audio: [...block.smash_audio],
  };
  const dropped = [];
  const dropFrom = (key, reason) => {
    if (!applied[key].length) return false;
    const idx = applied[key]
      .map((e, i) => [i, eventTime(key, e)])
      .sort((a, b) => b[1] - a[1])[0][0];
    dropped.push({ kind: key, event: applied[key][idx], reason });
    applied[key].splice(idx, 1);
    return true;
  };

  // 1) caps par catégorie — les plus tardifs d'abord
  const evCfg = (budget && budget.events) || {};
  const capOf = { brolls: evCfg.broll?.max_per_clip ?? 3, smash_audio: evCfg.smash?.max_per_clip ?? 2, punchins: evCfg.punchin?.max_per_clip ?? 4, jump_cuts: evCfg.jumpcut?.max_per_clip ?? 8 };
  const labelOf = { brolls: 'broll', smash_audio: 'smash', punchins: 'punchin', jump_cuts: 'jumpcut' };
  for (const [key, max] of Object.entries(capOf)) {
    while (applied[key].length > max) {
      dropFrom(key, `cap ${labelOf[key]} dépassé (max ${max})`);
    }
  }
  // 2) élément unique (note §3.5) : un punch-in qui CHEVAUCHE la fenêtre
  //    d'un panneau → déposé (le panneau est l'événement fort). Groupe 3 v2 :
  //    comparaison par INTERVALLES (le punch-in v2 porte duration_sec) — un
  //    punch démarré AVANT le panneau mais mordant sur son entrée est aussi
  //    un conflit (asf_c1 : punch @14.85 + 0.6 s → mord sur le panneau @15.0).
  const winSec = Math.max(0, Number(budget?.unique_element_rule?.window_sec ?? 0.05));
  const punchSpanSec = (p) => {
    const d = Number(p.duration_sec || 0);
    if (d > 0) return d;
    const attack = Math.max(1, Number(p.attack_frames || 3));
    const hold = Math.max(0, Number(p.hold_frames || 6));
    const release = Math.max(1, Number(p.release_frames || 9));
    return (attack + hold + release) / fps;
  };
  for (let i = applied.punchins.length - 1; i >= 0; i--) {
    const pf = Number(applied.punchins[i].at_sec || 0);
    const pEnd = pf + punchSpanSec(applied.punchins[i]);
    const conflict = applied.brolls.find((b) => {
      const bs = Number(b.at_sec || 0);
      const be = bs + Number(b.duration_frames || 0) / fps;
      return pEnd >= bs - winSec && pf <= be + winSec;
    });
    if (conflict) {
      dropped.push({ kind: 'punchins', event: applied.punchins[i], reason: 'élément unique : punch-in pendant un panneau B-roll (note §3.5)' });
      applied.punchins.splice(i, 1);
    }
  }
  // 3) dépense totale — du coût unitaire le plus élevé au plus faible
  const maxSpend = budget?.max_spend_units ?? 55;
  const costOf = { brolls: evCfg.broll?.cost_units ?? 12, smash_audio: evCfg.smash?.cost_units ?? 8, punchins: evCfg.punchin?.cost_units ?? 6, jump_cuts: evCfg.jumpcut?.cost_units ?? 1 };
  let gate = verifyCaviarBudget(applied, budget);
  const spendKey = { broll: 'brolls', smash: 'smash_audio', punchin: 'punchins', jumpcut: 'jump_cuts' };
  for (const [kind] of DROP_PRIORITY) {
    const key = spendKey[kind];
    while (!gate.ok && gate.spend_units > maxSpend && applied[key].length) {
      dropFrom(key, `dépense ${gate.spend_units}u > ${maxSpend}u — ${kind} déposé (respiration)`);
      gate = verifyCaviarBudget(applied, budget);
    }
  }
  gate = verifyCaviarBudget(applied, budget);
  return { applied, dropped, gate };
}

/** Construit TOUT le rendu narratif à partir du bloc caviar du manifeste.
 *  Retourne un objet consommé par PurPackComposition :
 *    - segments  : [{from, duration, sourceStart}] en FRAMES de timeline
 *                  (tuiles contiguës couvrant toute la durée)
 *    - punchins  : [{frame, scale_to, attack_frames, hold_frames, release_frames}]
 *    - brolls    : [{frame, frames, file, sfx, panel_spec?}] — panel_spec =
 *                  emballage v2 possédé par la partition (crop_zoom, blur,
 *                  panel) ; absent en v1 → rendu plein cadre historique
 *    - flashes   : [{frame, frames}] — ENTRÉE de B-roll uniquement
 *    - smash_audio : [{frame, duck_db, duration_sec}] (ducking musical)
 *    - gate      : verdict Budget d'Attention côté rendu
 *    - dropped   : événements retirés + raisons (traçabilité)
 *  Si le bloc est absent/désactivé : enabled=false, segments=[] — la
 *  composition historique est rendue à l'identique (zéro régression). */
export function buildCaviarTimeline(caviarRaw, budget, ctx = {}) {
  const fps = Number(ctx.fps || 30);
  const speed = Math.max(0.25, Number(ctx.speed || 1));
  const durationInFrames = Math.max(0, Number(ctx.durationInFrames || 0));
  const fxOff = ctx.fxOff === true;
  const block = normalizeCaviarBlock(caviarRaw);

  const inert = {
    enabled: false, source: block.source, segments: [], punchins: [], brolls: [],
    flashes: [], smash_audio: [], removed_sec: 0, dropped: [],
    gate: verifyCaviarBudget({ jump_cuts: [], punchins: [], brolls: [], smash_audio: [] }, budget),
    sourceToTimelineFrame: (s) => Math.round(Number(s || 0) * fps),
  };
  if (!block.enabled || durationInFrames <= 0) return inert;

  const { applied, dropped, gate } = enforceCaviarBudget(block, budget, { fps });
  const evCfg = (budget && budget.events) || {};

  // ── Jump cuts : validité (≥ min silences, pas de chevauchement) ──
  const minSil = budget?.silences?.min_duration_sec ?? 0.25;
  const cuts = applied.jump_cuts
    .map((c) => ({ cut_at_sec: Number(c.cut_at_sec), removes_sec: Number(c.removes_sec ?? 0) }))
    .filter((c) => Number.isFinite(c.cut_at_sec) && c.cut_at_sec > 0 && c.removes_sec > 0)
    .sort((a, b) => a.cut_at_sec - b.cut_at_sec);
  const keptCuts = [];
  let cursor = 0;
  for (const c of cuts) {
    if (c.removes_sec < minSil) {
      dropped.push({ kind: 'jump_cuts', event: c, reason: `silence < ${minSil}s — coupe inutile` });
      continue;
    }
    if (c.cut_at_sec - c.removes_sec < cursor) {
      dropped.push({ kind: 'jump_cuts', event: c, reason: 'chevauche un cut précédent' });
      continue;
    }
    keptCuts.push(c);
    cursor = c.cut_at_sec;
  }

  // ── Segments timeline→source (tuiles contiguës) ──
  // Une portion source de lenSec consomme lenSec/speed secondes de timeline
  // (playbackRate=speed) → len frames = lenSec * fps / speed.
  const segments = [];
  let tlFrame = 0;
  let srcSec = 0;
  // NOTE Groupe 3 v2 (bug asf_c1) : `srcSec = c.cut_at_sec` DOIT s'exécuter
  // même quand la tuile est vide (lenSec <= 0, ex. trim collé à 0 ou deux
  // trims adjacents qui fusionnent) — sinon le silence suivant est RÉINTÉGRÉ
  // dans la tuile qui suit (le trim géant d'intro de asf_c1 disparaissait).
  for (const c of keptCuts) {
    const cutStart = c.cut_at_sec - c.removes_sec;
    const lenSec = cutStart - srcSec;
    if (lenSec > 0) {
      const len = Math.round((lenSec * fps) / speed);
      if (len > 0) {
        segments.push({ from: tlFrame, duration: len, sourceStart: Math.round(srcSec * fps) });
        tlFrame += len;
      }
    }
    srcSec = c.cut_at_sec;
  }
  if (durationInFrames - tlFrame > 0) {
    segments.push({ from: tlFrame, duration: durationInFrames - tlFrame, sourceStart: Math.round(srcSec * fps) });
  }
  // Sécurité anti-dérive d'arrondi : rien au-delà de la durée, dernière
  // tuile tronquée proprement.
  for (let i = segments.length - 1; i >= 0; i--) {
    const s = segments[i];
    if (s.from >= durationInFrames) { segments.splice(i, 1); continue; }
    if (s.from + s.duration > durationInFrames) s.duration = durationInFrames - s.from;
  }

  /** Source (sec) → frame de timeline : retire le temps supprimé AVANT ce
   *  point ; un événement tombant DANS un silence retiré est recalé sur le
   *  point de coupe (il ne disparaît jamais avec le silence). */
  const sourceToTimelineFrame = (sourceSec) => {
    const T = Number(sourceSec || 0);
    let removedBefore = 0;
    for (const c of keptCuts) {
      const cutStart = c.cut_at_sec - c.removes_sec;
      if (T >= c.cut_at_sec) removedBefore += c.removes_sec;
      else if (T > cutStart) { removedBefore += T - cutStart; break; }
      else break;
    }
    return Math.max(0, Math.min(durationInFrames - 1, Math.round(((T - removedBefore) * fps) / speed)));
  };

  // ── Punch-ins ──
  // v2 asf : duration_sec (secondes SOURCE) → courbe attack/hold/release
  // proportionnelle (1/6, 2/6, 3/6 — les défauts 3f/6f/9f à 30 fps = 0.6 s).
  const punchins = fxOff ? [] : applied.punchins.map((p) => {
    const durSec = Number(p.duration_sec || 0);
    let attack = Math.max(1, Number(p.attack_frames || 3));
    let hold = Math.max(0, Number(p.hold_frames || 6));
    let release = Math.max(1, Number(p.release_frames || 9));
    if (durSec > 0 && p.attack_frames == null && p.hold_frames == null && p.release_frames == null) {
      const total = Math.max(3, Math.round((durSec * fps) / speed));
      attack = Math.max(1, Math.round(total / 6));
      hold = Math.max(0, Math.round(total / 3));
      release = Math.max(1, total - attack - hold);
    }
    return {
      frame: sourceToTimelineFrame(p.at_sec),
      scale_to: Math.min(1.15, Math.max(1.01, Number(p.scale_to || 1.08))),
      attack_frames: attack,
      hold_frames: hold,
      release_frames: release,
    };
  });
  if (fxOff && applied.punchins.length) {
    for (const p of applied.punchins) dropped.push({ kind: 'punchins', event: p, reason: 'fx_mode=off (clip normal)' });
  }

  // ── B-roll numéroté : PAS de fichier résolu = PAS de B-roll ──
  const maxBrollFrames = evCfg.broll?.max_frames ?? 45;
  const brolls = [];
  if (fxOff) {
    for (const b of applied.brolls) dropped.push({ kind: 'brolls', event: b, reason: 'fx_mode=off (clip normal)' });
  } else {
    for (const b of applied.brolls) {
      const file = String(b.file || '').trim();
      if (!file) {
        dropped.push({ kind: 'brolls', event: b, reason: `numéro ${b.numero} : fichier non résolu — pas de vidéo, pas de B-roll` });
        continue;
      }
      const rawFrames = Math.round(Number(b.duration_frames || maxBrollFrames));
      if (rawFrames > maxBrollFrames) {
        dropped.push({ kind: 'brolls', event: { at_sec: b.at_sec, duration_frames: b.duration_frames }, reason: `durée panneau ${rawFrames}f > cap ${maxBrollFrames}f — tronquée` });
      }
      // GROUPE 2 v2 : l'EMBALLAGE du panneau est possédé par la partition.
      const spec = resolvePanelSpec(b, ctx.registry);
      brolls.push({
        frame: sourceToTimelineFrame(b.at_sec),
        frames: Math.max(1, Math.min(maxBrollFrames, rawFrames)),
        file,
        sfx: String(b.sfx || 'impact'),
        numero: b.numero ?? null,
        extra: b.extra ?? null,
        panel_spec: spec,
      });
    }
  }

  // ── resolution_at (note §3.5) : AUCUN événement après la résolution.
  //    Le gate vérifie le pack ; ICI dernier filet sur la TIMELINE réelle.
  const resolutionSec = Number(block.extra?.resolution_at || 0);
  if (resolutionSec > 0) {
    const limit = Math.round(resolutionSec * fps);
    for (let i = punchins.length - 1; i >= 0; i--) {
      if (punchins[i].frame >= limit) {
        dropped.push({ kind: 'punchins', event: punchins[i], reason: `après resolution_at (${resolutionSec}s) — interdit (note §3.5)` });
        punchins.splice(i, 1);
      }
    }
    for (let i = brolls.length - 1; i >= 0; i--) {
      if (brolls[i].frame >= limit) {
        dropped.push({ kind: 'brolls', event: brolls[i], reason: `après resolution_at (${resolutionSec}s) — interdit (note §3.5)` });
        brolls.splice(i, 1);
      }
    }
  }

  // Flash : ENTRÉE de chaque B-roll uniquement — par construction.
  const flashes = brolls.map((b) => ({ frame: b.frame, frames: 5 }));

  // ── Smash audio (ducking au climax) — exporté pour la couche musicale ──
  let smash_audio = applied.smash_audio.map((s) => ({
    frame: sourceToTimelineFrame(s.at_sec),
    duck_db: Number(s.duck_db ?? -12),
    duration_sec: Math.max(0.1, Number(s.duration_sec || 0.8)),
  }));
  if (resolutionSec > 0) {
    const limit = Math.round(resolutionSec * fps);
    smash_audio = smash_audio.filter((s) => {
      if (s.frame >= limit) {
        dropped.push({ kind: 'smash_audio', event: s, reason: `après resolution_at (${resolutionSec}s) — interdit (note §3.5)` });
        return false;
      }
      return true;
    });
  }

  return {
    enabled: true,
    source: block.source,
    segments,
    punchins,
    brolls,
    flashes,
    smash_audio,
    removed_sec: keptCuts.reduce((sum, c) => sum + c.removes_sec, 0),
    dropped,
    gate: {
      ...gate,
      dropped_count: dropped.length,
      resolution_at: resolutionSec > 0 ? resolutionSec : null,
      resolution_violations: 0,
    },
    sourceToTimelineFrame,
  };
}

/** Punch-in caviar à un frame donné — multiplicateur d'échelle (1 = neutre).
 *  Montée sèche (attack linéaire), tenue, redescente vers 1.0. */
export function caviarPunchScaleAtFrame(punchins, frame) {
  let scale = 1;
  for (const p of punchins || []) {
    const start = Number(p.frame || 0);
    const attack = Math.max(1, Number(p.attack_frames || 3));
    const hold = Math.max(0, Number(p.hold_frames || 6));
    const release = Math.max(1, Number(p.release_frames || 9));
    if (frame >= start && frame < start + attack + hold + release) {
      const peak = Number(p.scale_to || 1.08);
      if (frame < start + attack) {
        scale *= 1 + (peak - 1) * ((frame - start) / attack);
      } else if (frame < start + attack + hold) {
        scale *= peak;
      } else {
        scale *= peak + (1 - peak) * ((frame - start - attack - hold) / release);
      }
    }
  }
  return scale;
}

/** Flash blanc caviar — ENTRÉE de B-roll uniquement, courbe symétrique.
 *  Visible DÈS la première frame du B-roll (le flash annonce l'entrée). */
export function caviarFlashOpacityAtFrame(flashes, frame) {
  let opacity = 0;
  for (const f of flashes || []) {
    const start = Number(f.frame || 0);
    const dur = Math.max(1, Number(f.frames || 5));
    const attack = Math.max(1, Math.round(dur / 2));
    const release = Math.max(1, dur - attack);
    if (frame >= start && frame < start + attack) {
      opacity = Math.max(opacity, (frame - start + 1) / attack);
    } else if (frame >= start + attack && frame < start + attack + release) {
      opacity = Math.max(opacity, 1 - (frame - start - attack) / release);
    }
  }
  return Math.min(1, Math.max(0, opacity));
}

/** Ducking caviar — multiplicateur de volume musical (1 = neutre).
 *  Descente rapide vers 10^(duck_db/20) (−12 dB ≈ ×0.25), tenue, remontée. */
export function caviarDuckVolumeAtFrame(smashAudio, frame, fps = 30, baseVolume = 1) {
  let volume = Math.max(0, Number(baseVolume || 1));
  for (const s of smashAudio || []) {
    const start = Number(s.frame || 0);
    const dur = Math.max(1, Math.round(Number(s.duration_sec || 0.8) * fps));
    const ramp = Math.max(1, Math.round(0.06 * fps)); // ~2 frames à 30 fps
    const dip = Math.pow(10, Number(s.duck_db ?? -12) / 20);
    if (frame >= start && frame < start + dur) {
      let factor;
      if (frame < start + ramp) factor = 1 - (1 - dip) * ((frame - start + 1) / ramp);
      else if (frame >= start + dur - ramp) factor = dip + (1 - dip) * ((frame - (start + dur - ramp)) / ramp);
      else factor = dip;
      volume *= factor;
    }
  }
  return volume;
}

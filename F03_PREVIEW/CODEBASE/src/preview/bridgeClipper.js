/* PERTURABO pack PUR → manifeste dev10.pur.v1 (LOOK : blur / split / reframing). */

const clamp = (value, min, max, fallback) => {
  const n = Number(value);
  return Number.isFinite(n) ? Math.max(min, Math.min(max, n)) : fallback;
};

const PUR_CANVAS = {
  '9:16': { width: 1080, height: 1920 },
  '16:9': { width: 1920, height: 1080 },
  '1:1': { width: 1080, height: 1080 },
};

export const PUR_STYLE_VALUES = ['reframing', 'blur', 'split_scene'];

export const PUR_STYLE_PARAMS_DEFAULTS = {
  blur: { degree: 24, bg_scale: 118, fg_scale: 72, fg_y_pct: 62 },
  split_scene: { top_scale: 62, bottom_scale: 38, text_size: 56, text_x_pct: 50, text_y_pct: 8 },
  reframing: { scale: 130, offset_x_pct: 0, offset_y_pct: -6 },
};

export const PUR_OVERLAY_DEFAULTS = {
  line1_color: '#FFFFFF',
  line2_color: '#FFD700',
  font_family: 'Arial Black, Impact',
  bg_enabled: false,
  bg_color: '#000000',
  bg_opacity: 0.65,
  outline_color: '#000000',
  outline_width: 3,
  size: 68,
  x_pct: 50,
  y_pct: 22,
  static_text: true,
  uppercase: false,
  box_radius: 10,
  box_padding: 14,
  auto_fit: true,
  min_size: 28,
};

export function extractOverlayLines(copywriting = {}) {
  const raw = copywriting.overlay_title || copywriting.title || '';
  const lines = String(raw).split(/\n/).map((l) => l.trim()).filter(Boolean).slice(0, 3);
  if (lines.length > 0) return lines;
  const ost = copywriting.on_screen_text || '';
  if (ost) return String(ost).split(/\n/).map((l) => l.trim()).filter(Boolean).slice(0, 3);
  return [];
}

export function normalizePurAntiDetection(mi = {}) {
  const block = mi.anti_detection || {};
  const techniques = Array.isArray(block.techniques) ? block.techniques : [];
  const out = {
    mirror: false,
    speed: 1.0,
    crop_pct: 0,
    principle: block.principle || '',
  };
  for (const t of techniques) {
    const name = String(t.name || '').toLowerCase();
    const optimal = String(t.optimal || t.action || '');
    if (name === 'mirror') out.mirror = true;
    else if (name === 'speed') {
      const m = optimal.match(/([0-9]+(?:\.[0-9]+)?)x/i);
      if (m) out.speed = Number(m[1]);
    } else if (name === 'crop') {
      const m = optimal.match(/([0-9]+(?:\.[0-9]+)?)\s*%/);
      if (m) out.crop_pct = Number(m[1]);
    }
  }
  return out;
}

export function normalizePurZooms(zooms = [], _cuts = [], fps = 30) {
  const list = Array.isArray(zooms) ? zooms : [];
  return list.map((z) => {
    const intensity = String(z.intensity_pct || '');
    const nums = intensity.match(/([0-9]+(?:\.[0-9]+)?)/g) || [];
    const from = nums.length > 0 ? Number(nums[0]) / 100 : 1.08;
    const to = nums.length > 1 ? Number(nums[1]) / 100 : from;
    const durMatch = String(z.duration_in || '').match(/([0-9]+(?:\.[0-9]+)?)\s*s/i);
    const seconds = durMatch ? Number(durMatch[1]) : 0.1;
    return {
      moment_sec: Number(z.moment_sec || 0),
      moment_frame: Math.round(Number(z.moment_sec || 0) * fps),
      type: z.type || 'zoom',
      scale_from: from,
      scale_to: to,
      frames: Math.max(1, Math.round(seconds * fps)),
      easing: z.easing || 'NONE',
      sfx_sync: z.sfx_sync || '',
    };
  });
}

export function normalizePurStyleParams(styleParams, style) {
  const base = PUR_STYLE_PARAMS_DEFAULTS[style] || PUR_STYLE_PARAMS_DEFAULTS.blur;
  return { ...base, ...(styleParams && typeof styleParams === 'object' ? styleParams : {}) };
}

export function normalizePurOverlayParams(styleParams) {
  return { ...PUR_OVERLAY_DEFAULTS, ...(styleParams && typeof styleParams === 'object' ? styleParams : {}) };
}

export function inferPurStyle(mi = {}) {
  const body = mi.body || {};
  const miAny = mi;
  if (miAny.split_scene?.layout || miAny.layout || body.layout) return 'split_scene';
  if (Array.isArray(body.layers) && body.layers.length >= 2) return 'blur';
  if (miAny.dual_layer === true || body.dual_layer === true) return 'blur';
  const zooms = Array.isArray(body.zooms) ? body.zooms : [];
  const cuts = Array.isArray(body.cuts) ? body.cuts : [];
  const pushIn = zooms.find((z) => String(z.type || z.note || '').includes('push'));
  if (pushIn && cuts.length <= 1) return 'reframing';
  return '';
}

export function normalizePurSfx(mi = {}) {
  const body = mi.body || {};
  const zooms = Array.isArray(body.zooms) ? body.zooms : [];
  const cuts = Array.isArray(body.cuts) ? body.cuts : [];
  const list = [];
  const pushSfx = (sync, momentSec) => {
    const text = String(sync || '');
    if (!text) return;
    const volMatch = text.match(/([0-9]+(?:\.[0-9]+)?)\s*%/);
    const typeMatch = text.match(/(impact|whoosh|boom|riser|hit|sub_drop)/i);
    list.push({
      moment_sec: Number(momentSec || 0),
      moment_frame: Math.round(Number(momentSec || 0) * 30),
      type: typeMatch ? typeMatch[1].toLowerCase() : 'impact',
      volume: volMatch ? clamp(Number(volMatch[1]) / 100, 0.1, 1) : 0.55,
    });
  };
  for (const z of zooms) pushSfx(z.sfx_sync, z.moment_sec);
  for (const c of cuts) pushSfx(c.sfx_sync, c.moment_sec);
  return list;
}

export function normalizePurCuts(cuts = [], fps = 30) {
  const list = Array.isArray(cuts) ? cuts : [];
  return list.map((c) => ({
    type: c.type || 'cut',
    moment_sec: Number(c.moment_sec || 0),
    moment_frame: Math.round(Number(c.moment_sec || 0) * fps),
    word_anchor: c.word_anchor || '',
    technique: c.technique || '',
    sfx_sync: c.sfx_sync || '',
  }));
}

export function normalizePurBroll(body = {}, fps = 30) {
  const raw = body.broll || body.b_roll || body.memes || [];
  const list = Array.isArray(raw) ? raw : [];
  return list.map((b) => {
    const inSec = Number(b.in_sec ?? b.moment_sec ?? 0);
    const duration = Number(b.duration_sec ?? 0.4);
    return {
      file: b.file || b.src || '',
      in_sec: inSec,
      out_sec: Number(b.out_sec ?? (inSec + duration)),
      in_frame: Math.round(inSec * fps),
      flash_in: b.flash_in !== false,
      duck: b.duck !== false,
    };
  });
}

function buildPurOverlay(lines, mainTitle = {}, hookDuration, fps, overlayParams) {
  return {
    lines,
    font: mainTitle.font || 'Montserrat ExtraBold / Bebas Neue (800-900)',
    fallback_font: mainTitle.fallback || 'Arial Black, Impact',
    color: mainTitle.color || '#FFFFFF',
    accent: mainTitle.accent || '#FFD700',
    outline: mainTitle.outline || '#000000',
    position: mainTitle.position || 'haut vers le centre',
    font_size: 68,
    style_params: { ...PUR_OVERLAY_DEFAULTS, ...(overlayParams && typeof overlayParams === 'object' ? overlayParams : {}) },
    visible_from_frame: Math.round(hookDuration * fps),
    visible: mainTitle.visible || 'toute la duree',
  };
}

function createEmptyPurManifest(fps) {
  return {
    schema_version: 'dev10.pur.v1',
    mode: 'pur_pack',
    fps,
    canvas: { ...PUR_CANVAS['9:16'], aspect: '9:16' },
    narrative: { category: '', energy_level: '', overlay: { lines: [] } },
    entries: [],
    duration_seconds: 0,
    total_frames: 0,
    pur: {},
  };
}

export function parsePurPack(pack, options = {}) {
  const fps = options.fps || 30;
  const clipFiles = options.clipFiles || [];
  if (!pack || typeof pack !== 'object') return createEmptyPurManifest(fps);

  const mi = pack.montage_instructions || {};
  const segment = mi.segment || pack.source || {};
  const hook = mi.hook || {};
  const body = mi.body || {};
  const outro = mi.outro || {};
  const style = mi.style || {};
  const platformRules = mi.platform_rules || {};
  const mainTitle = (body.text_overlays && body.text_overlays.main_title) || {};

  const declared = String(pack.montage_style || mi.metadata?.style || '').toLowerCase();
  const operatorStyle = String(options.style || '').toLowerCase();
  const resolvedStyle = operatorStyle || declared || inferPurStyle(mi);
  const styleKnown = PUR_STYLE_VALUES.includes(resolvedStyle);

  const overlayLines = extractOverlayLines(pack.copywriting || pack.text_payload || {});
  const hookDuration = clamp(hook.duration_sec ?? platformRules.hook_duration_sec ?? 3, 0, 15);
  const sourceDuration = clamp(
    Number(segment.duration_sec) || (Number(segment.end_sec) - Number(segment.start_sec)) || 30,
    0.5, 600);
  const bodyDuration = Number(body.duration_sec) || Math.max(1, sourceDuration - hookDuration);
  const outroDuration = clamp(outro.duration_sec ?? 1, 0, 5);
  const antiDetection = normalizePurAntiDetection(mi);
  const speed = clamp(antiDetection.speed || 1, 0.5, 2);
  const zooms = normalizePurZooms(body.zooms, body.cuts, fps);
  const clipFile = clipFiles[0] || '';
  const aspect = options.canvas || platformRules.aspect_ratio || '9:16';
  const canvas = PUR_CANVAS[aspect] || PUR_CANVAS['9:16'];

  const cuts = normalizePurCuts(body.cuts, fps);
  const broll = normalizePurBroll(body, fps);
  const punchIns = zooms.map((z) => ({
    in_sec: Number(z.moment_sec || 0),
    out_sec: Number(z.moment_sec || 0) + (Number(z.frames || 1) / fps),
    scale: Math.max(Number(z.scale_from || 1), Number(z.scale_to || 1)),
    sfx_sync: z.sfx_sync || '',
    type: z.type || 'punch_in_cut',
  }));
  const entry = {
    source_id: `pur_${pack.identite?.angle_id || pack.pack_id || 'clip'}`,
    clip_file: clipFile,
    duration_seconds: sourceDuration,
    start_frame: 0,
    role: 'pur_clip',
    anti_detection: antiDetection,
    zooms,
    punch_ins: punchIns,
    cuts,
    broll,
    sfx_list: normalizePurSfx(mi),
  };

  return {
    schema_version: 'dev10.pur.v1',
    mode: 'pur_pack',
    fps,
    style: styleKnown ? resolvedStyle : '',
    style_source: operatorStyle ? 'operator' : declared ? 'pack' : styleKnown ? 'inferred' : 'none',
    style_unknown: !styleKnown,
    canvas: { ...canvas, aspect },
    style_params: options.styleParams || (styleKnown ? { ...PUR_STYLE_PARAMS_DEFAULTS[resolvedStyle] } : { ...PUR_STYLE_PARAMS_DEFAULTS.blur }),
    narrative: {
      category: style.pacing || '',
      energy_level: style.energy_level || 'high',
      overlay: buildPurOverlay(overlayLines, mainTitle, hookDuration, fps, options.overlayParams),
    },
    entries: [entry],
    duration_seconds: sourceDuration,
    total_frames: Math.max(1, Math.round((sourceDuration / speed) * fps)),
    pur: {
      pack_id: pack.pack_id || '',
      angle_id: pack.identite?.angle_id || '',
      generated_at: pack.generated_at || mi.metadata?.generated_at || '',
      generator: mi.metadata?.generator || 'F06_DIRECTOR',
      source: segment.source_url || segment.vod_url || '',
      start_sec: Number(segment.start_sec || 0),
      end_sec: Number(segment.end_sec || 0),
      platform: platformRules.platform || 'youtube_shorts',
      hook: { duration_sec: hookDuration, philosophy: hook.philosophy || '' },
      body: { duration_sec: bodyDuration, energy_curve: body.energy_curve || [] },
      outro: { duration_sec: outroDuration, type: outro.type || 'fade_to_black', note: outro.note || '' },
      compliance: mi.compliance || pack.compliance || {},
    },
  };
}

export function parsePurPackMulti(packs, options = {}) {
  const list = (Array.isArray(packs) ? packs : [packs]).filter((p) => p && typeof p === 'object');
  if (list.length === 0) return createEmptyPurManifest(options.fps || 30);
  if (list.length === 1) return parsePurPack(list[0], options);

  const fps = options.fps || 30;
  const clipFiles = options.clipFiles || [];
  const first = list[0];
  const operatorStyle = String(options.style || '').toLowerCase();
  const declared = String(first.montage_style || first.montage_instructions?.metadata?.style || '').toLowerCase();
  const resolvedStyle = operatorStyle || declared || inferPurStyle(first.montage_instructions || {});
  const styleKnown = PUR_STYLE_VALUES.includes(resolvedStyle);

  const entries = list.map((pack, index) => {
    const single = parsePurPack(pack, {
      fps,
      canvas: options.canvas,
      clipFiles: [clipFiles[index] || clipFiles[0] || ''],
      style: operatorStyle || undefined,
    });
    const entry = single.entries[0] || null;
    if (!entry) return null;
    entry.overlay = JSON.parse(JSON.stringify(single.narrative?.overlay || {}));
    entry.pack_label = pack.pack_id || `pack_${index + 1}`;
    entry.angle_id = pack.identite?.angle_id || single.pur?.angle_id || `A${String(index + 1).padStart(2, '0')}`;
    return entry;
  }).filter(Boolean);

  const durationSeconds = entries.reduce((sum, e) => sum + Number(e.duration_seconds || 0), 0);
  const speed = Number(entries[0]?.anti_detection?.speed || 1);
  const base = parsePurPack(first, { fps, canvas: options.canvas, clipFiles: [], style: operatorStyle || undefined });

  return {
    ...base,
    style: styleKnown ? resolvedStyle : '',
    style_source: operatorStyle ? 'operator' : declared ? 'pack' : styleKnown ? 'inferred' : 'none',
    style_unknown: !styleKnown,
    style_params: options.styleParams || base.style_params,
    entries,
    duration_seconds: durationSeconds,
    total_frames: Math.max(1, entries.reduce((sum, e) => {
      const s = Number(e.anti_detection?.speed || 1);
      return sum + Math.round((Number(e.duration_seconds || 0) / s) * fps);
    }, 0) || Math.max(1, Math.round((durationSeconds / speed) * fps))),
    pur: {
      ...base.pur,
      pack_ids: list.map((p) => p.pack_id || ''),
      angle_ids: entries.map((e) => e.angle_id),
      pack_count: entries.length,
      multi: true,
    },
  };
}

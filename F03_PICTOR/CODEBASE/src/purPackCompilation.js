/* ═══════════════════════════════════════════════════════════════════
   purPackCompilation.js — Normaliseur manifeste dev10.pur.v1 (F04 RENDER)

   MIROIR de parsePurPack()/composant preview : mêmes valeurs, mêmes
   transformations — parité F03 Preview / F04 Render (doctrine dev9).
   Le manifeste consommé est celui stocké dans codex.pur_manifest.
   ═══════════════════════════════════════════════════════════════════ */

export const PUR_CANVAS = {
  '9:16': { width: 1080, height: 1920 },
  '16:9': { width: 1920, height: 1080 },
  '1:1': { width: 1080, height: 1080 },
};

export const PUR_STYLE_VALUES = ['ranking', 'reframing', 'blur', 'split_scene'];

/** Défauts style_params (opérateur) — MIROIR de bridgeClipper.js (F03 Preview). */
export const PUR_STYLE_PARAMS_DEFAULTS = {
  blur: { degree: 24, bg_scale: 118, fg_scale: 72 },
  split_scene: { top_scale: 62, bottom_scale: 38, text_size: 56, text_x_pct: 50, text_y_pct: 8 },
  reframing: { scale: 130, offset_x_pct: 0, offset_y_pct: -6 },
  ranking: {},
};

/** Défauts overlay éditorial — MIROIR de bridgeClipper.js (F03 Preview). */
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
};

export function normalizePurStyleParams(styleParams, style) {
  const base = PUR_STYLE_PARAMS_DEFAULTS[style] || PUR_STYLE_PARAMS_DEFAULTS.blur;
  return { ...base, ...(styleParams && typeof styleParams === 'object' ? styleParams : {}) };
}

export function normalizePurOverlayParams(styleParams) {
  return { ...PUR_OVERLAY_DEFAULTS, ...(styleParams && typeof styleParams === 'object' ? styleParams : {}) };
}

export function normalizePurManifest(raw, fps = 30) {
  const manifest = raw && typeof raw === 'object' ? raw : {};
  if (manifest.schema_version === 'dev10.pur.v1' && Array.isArray(manifest.entries)) {
    const speed = Number(manifest.entries?.[0]?.anti_detection?.speed || 1);
    const rawStyle = String(manifest.style || '');
    const style = PUR_STYLE_VALUES.includes(rawStyle) ? rawStyle
      : PUR_STYLE_VALUES.includes(String(manifest.pur?.montage_style || '')) ? String(manifest.pur.montage_style)
      : '';
    return {
      ...manifest,
      fps: Number(manifest.fps || fps),
      style,
      style_source: String(manifest.style_source || (style ? 'pack' : 'none')),
      style_unknown: style === '' || !['pack', 'operator'].includes(String(manifest.style_source || '')),
      total_frames: Number(manifest.total_frames) || Math.max(1, Math.round((Number(manifest.duration_seconds || 0) / speed) * fps)),
    };
  }
  return { ...emptyPurManifest(fps), ...manifest };
}

/** Zoom ponctuel à un frame donné — identique au preview (_purPackComposition). */
export function purZoomAtFrame(zooms, frame) {
  let scale = 1;
  for (const z of zooms || []) {
    const start = Number(z.moment_frame || 0);
    const end = start + Number(z.frames || 3);
    if (frame >= start && frame < end) {
      const p = (frame - start) / Math.max(1, end - start);
      scale *= z.easing === 'NONE' ? z.scale_to : (z.scale_from + (z.scale_to - z.scale_from) * p);
    }
  }
  return scale;
}

/** Anti-détection → transform CSS (mirror + breathing zoom + crop). */
export function purAntiTransform(anti, frame, fps = 30) {
  const parts = [];
  const cfg = anti || {};
  const breathing = cfg.breathing_zoom || {};
  if (breathing.enabled !== false) {
    const minS = Number(breathing.min_scale ?? 1.02);
    const maxS = Number(breathing.max_scale ?? 1.08);
    const cycleFrames = Number(breathing.cycle_seconds ?? 8) * fps;
    const t = (frame % cycleFrames) / cycleFrames;
    const sine = Math.sin(t * Math.PI * 2);
    parts.push(`scale(${(minS + (maxS - minS) * (sine * 0.5 + 0.5)).toFixed(4)})`);
  }
  if (cfg.mirror) parts.push('scaleX(-1)');
  if (Number(cfg.crop_pct || 0) > 0) parts.push(`scale(${(1 + 2 * (Number(cfg.crop_pct) / 100)).toFixed(4)})`);
  return parts.length > 0 ? parts.join(' ') : undefined;
}

function emptyPurManifest(fps) {
  return {
    schema_version: 'dev10.pur.v1',
    mode: 'pur_pack',
    fps,
    canvas: { ...PUR_CANVAS['9:16'], aspect: '9:16' },
    narrative: { category: '', energy_level: '', overlay: { lines: [] } },
    entries: [],
    rank_count: 0,
    final_rank: null,
    duration_seconds: 0,
    total_frames: 0,
    pur: {},
  };
}

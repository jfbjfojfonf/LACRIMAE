/* ═══════════════════════════════════════════════════════════════════
   antiDetection.js — Module partagé anti-detection pour Mode PUR
   
   Utilisé par : blur, ranking_split, reframing, split_scene
   Source : PERTURABO ARCHIVUM/montage/patterns/anti_detection.json
   ═══════════════════════════════════════════════════════════════════ */

export const ANTI_DETECTION_DEFAULTS = {
  breathing_zoom: { enabled: false, min_scale: 1.05, max_scale: 1.10, cycle_seconds: 8 },
  mirror: false,
  speed: 1.0,
  crop_offset_x: 0,
  crop_offset_y: 0,
};

/**
 * Retourne le scale du breathing zoom à un frame donné.
 * Cycle sinusoïdal entre min_scale et max_scale.
 */
export function breathingZoomScale(config, frame, fps = 30) {
  const cfg = config?.breathing_zoom || ANTI_DETECTION_DEFAULTS.breathing_zoom;
  if (!cfg.enabled) return 1;
  const minS = cfg.min_scale ?? 1.05;
  const maxS = cfg.max_scale ?? 1.10;
  const cycleFrames = (cfg.cycle_seconds ?? 8) * fps;
  const t = (frame % cycleFrames) / cycleFrames;
  const sine = Math.sin(t * Math.PI * 2);
  return minS + (maxS - minS) * (sine * 0.5 + 0.5);
}

/**
 * Retourne le CSS transform string pour l'anti-detection complète.
 */
export function antiDetectionTransform(config, frame, fps = 30) {
  const parts = [];
  const zoom = breathingZoomScale(config, frame, fps);
  if (zoom !== 1) parts.push(`scale(${zoom.toFixed(4)})`);
  const mirror = config?.mirror ?? ANTI_DETECTION_DEFAULTS.mirror;
  if (mirror) parts.push('scaleX(-1)');
  return parts.length > 0 ? parts.join(' ') : undefined;
}

/**
 * Retourne le playbackRate pour la speed anti-detection.
 */
export function antiDetectionSpeed(config) {
  return config?.speed ?? ANTI_DETECTION_DEFAULTS.speed;
}

/**
 * Applique l'anti-detection sur un style React (mutates).
 */
export function applyAntiDetection(style, config, frame, fps = 30) {
  const transform = antiDetectionTransform(config, frame, fps);
  if (transform) {
    style.transform = style.transform ? `${style.transform} ${transform}` : transform;
    style.transformOrigin = 'center center';
  }
  return style;
}

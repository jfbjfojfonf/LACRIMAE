export const ANTI_DETECTION_DEFAULTS = {
  mirror: false,
  speed: 1.0,
};

export function antiDetectionTransform(config) {
  const parts = [];
  const mirror = config?.mirror ?? ANTI_DETECTION_DEFAULTS.mirror;
  if (mirror) parts.push('scaleX(-1)');
  return parts.length > 0 ? parts.join(' ') : undefined;
}

export function antiDetectionSpeed(config) {
  return config?.speed ?? ANTI_DETECTION_DEFAULTS.speed;
}

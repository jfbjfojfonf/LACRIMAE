export const MOTION_VALUES = ['pop-in', 'bounce', 'slide'];

export const CANVAS = {
  '9:16': { width: 1080, height: 1920 },
  '16:9': { width: 1920, height: 1080 },
  '1:1': { width: 1080, height: 1080 },
};

export const DEFAULT_STYLE = {
  schema_version: 'dev11.caption.style.v1',
  id: 's1',
  font: 'Montserrat-ExtraBold.ttf',
  position: { x_pct: 50, y_pct: 78 },
  size: 72,
  color: '#FFFFFF',
  outline: { width: 4, color: '#000000' },
  glow: { intensity: 1.2, color: '#FFFFFF' },
  motion: 'pop-in',
  canvas: '9:16',
};

export function clamp(value, min, max) {
  const n = Number(value);
  if (!Number.isFinite(n)) return min;
  return Math.min(max, Math.max(min, n));
}

export function normalizeStyle(raw) {
  const src = raw && typeof raw === 'object' ? raw : {};
  const position = src.position && typeof src.position === 'object' ? src.position : {};
  const outline = src.outline && typeof src.outline === 'object' ? src.outline : {};
  const glow = src.glow && typeof src.glow === 'object' ? src.glow : {};
  const motion = MOTION_VALUES.includes(src.motion) ? src.motion : DEFAULT_STYLE.motion;
  const canvas = CANVAS[src.canvas] ? src.canvas : DEFAULT_STYLE.canvas;
  return {
    schema_version: 'dev11.caption.style.v1',
    id: typeof src.id === 'string' && src.id.trim() ? src.id.trim() : 's1',
    font: typeof src.font === 'string' && src.font.trim() ? src.font.trim() : DEFAULT_STYLE.font,
    position: {
      x_pct: clamp(position.x_pct, 0, 100),
      y_pct: clamp(position.y_pct, 0, 100),
    },
    size: clamp(src.size, 12, 240),
    color: typeof src.color === 'string' && src.color ? src.color : DEFAULT_STYLE.color,
    outline: {
      width: clamp(outline.width, 0, 24),
      color: typeof outline.color === 'string' && outline.color ? outline.color : DEFAULT_STYLE.outline.color,
    },
    glow: {
      intensity: clamp(glow.intensity, 0, 5),
      color: typeof glow.color === 'string' && glow.color ? glow.color : DEFAULT_STYLE.glow.color,
    },
    motion,
    canvas,
  };
}

export function parseTranscript(raw) {
  const src = raw && typeof raw === 'object' ? raw : {};
  const words = Array.isArray(src.words) ? src.words : [];
  const parsed = [];
  for (const item of words) {
    if (!item || typeof item !== 'object') continue;
    const word = String(item.word || '').trim();
    const start = Number(item.start);
    const end = Number(item.end);
    if (!word || !Number.isFinite(start) || !Number.isFinite(end) || end <= start) continue;
    parsed.push({ word, start, end });
  }
  return {
    schema_version: 'dev11.caption.transcript.v1',
    video: typeof src.video === 'string' ? src.video : '',
    language: typeof src.language === 'string' ? src.language : '',
    words: parsed,
  };
}

export function activeWords(transcript, timeSec) {
  if (!transcript || !Array.isArray(transcript.words)) return [];
  return transcript.words.filter((w) => timeSec >= w.start && timeSec < w.end);
}

export function firstWord(transcript) {
  if (!transcript || !transcript.words.length) return 'HOE';
  return transcript.words[0].word;
}

export function buildProofRequest(style, word, videoName) {
  return {
    schema_version: 'dev11.caption.proof.v1',
    style: normalizeStyle(style),
    word: String(word || 'HOE').trim() || 'HOE',
    video: videoName || '',
    frames: 3,
  };
}

export function downloadJson(filename, data) {
  const blob = new Blob([JSON.stringify(data, null, 2) + '\n'], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

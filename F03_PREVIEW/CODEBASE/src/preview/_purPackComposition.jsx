import React, { useMemo } from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig, Video } from 'remotion';
import { antiDetectionTransform } from './antiDetection';
import { normalizePurOverlayParams, normalizePurStyleParams } from './bridgeClipper';

function purCropTransform(cropPct) {
  if (!cropPct) return '';
  const s = 1 + 2 * (cropPct / 100);
  return `scale(${s.toFixed(4)})`;
}

function withAlpha(hex, alpha) {
  const m = String(hex || '').match(/^#?([0-9a-f]{6})$/i);
  if (!m) return hex;
  const n = parseInt(m[1], 16);
  return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${Number(alpha ?? 1).toFixed(3)})`;
}

const measureCtx = typeof document !== 'undefined'
  ? document.createElement('canvas').getContext('2d')
  : null;

function measureTextWidth(text, font) {
  if (!measureCtx) return 0;
  measureCtx.font = font;
  return measureCtx.measureText(text).width;
}

function fitOverlayLines(lines, baseSize, fontFamily, canvasWidth, minSize) {
  const list = (lines || []).slice(0, 3).map((l) => String(l));
  if (!measureCtx || !canvasWidth || list.length === 0) return { lines: list, size: baseSize };
  const usable = canvasWidth * 0.92;
  const font = `900 ${baseSize}px ${fontFamily}`;
  const widest = Math.max(...list.map((l) => measureTextWidth(l, font)));
  if (widest <= usable) return { lines: list, size: baseSize };
  const fitted = Math.max(Number(minSize || 28), Math.floor(baseSize * (usable / widest)));
  return { lines: list, size: fitted };
}

let purFontLoaded = false;
function ensurePurFont() {
  if (purFontLoaded || typeof document === 'undefined') return;
  purFontLoaded = true;
  const face = new FontFace('Montserrat', 'url(fonts/Montserrat-ExtraBold.ttf)', { weight: '900' });
  face.load().then((f) => document.fonts.add(f)).catch(() => {});
}

export function PurPackComposition({ purManifest, session: sessionProp, entryIndex = 0 }) {
  ensurePurFont();
  const frame = useCurrentFrame();
  const { fps, durationInFrames, width: canvasWidth } = useVideoConfig();
  const manifest = purManifest || sessionProp?.pur || {};
  const entries = Array.isArray(manifest.entries) ? manifest.entries : [];
  const safeIndex = Math.max(0, Math.min(Number(entryIndex) || 0, Math.max(0, entries.length - 1)));
  const entry = entries[safeIndex] || {};
  const isMulti = entries.length > 1;
  const globalOverlay = manifest.narrative?.overlay || {};
  const entryOverlay = entry.overlay || {};
  const overlayRaw = {
    ...entryOverlay,
    ...globalOverlay,
    lines: (globalOverlay.lines?.length ? globalOverlay.lines : entryOverlay.lines) || [],
    style_params: { ...(entryOverlay.style_params || {}), ...(globalOverlay.style_params || {}) },
  };
  const overlay = { ...overlayRaw, ...normalizePurOverlayParams(overlayRaw.style_params) };
  const pur = manifest.pur || {};

  const styleName = String(manifest.style || '');
  const styleLayout = styleName === 'blur' ? 'blur'
    : styleName === 'split_scene' ? 'split'
    : styleName === 'reframing' ? 'reframing'
    : 'blocked';
  const sp = normalizePurStyleParams(manifest.style_params, styleName || 'blur');

  const videoUrl = entry.clip_file ? entry.clip_file.replace(/^\.?\//, '') : null;
  const anti = entry.anti_detection || {};
  const speed = Number(anti.speed || 1);
  const antiTransform = [antiDetectionTransform(anti), purCropTransform(anti.crop_pct)]
    .filter(Boolean).join(' ');

  const overlayVisible = overlayRaw.lines?.length > 0;
  const lineColors = [overlay.line1_color || overlayRaw.color || '#FFFFFF', overlay.line2_color || overlayRaw.accent || '#FFD700'];
  const fontFamilyBase = overlay.font_family || overlayRaw.fallback_font || 'Arial Black, Impact';
  const uppercase = overlay.uppercase === true;
  const outlineWidth = Number(overlay.outline_width ?? 3);
  const outlineColor = overlay.outline_color || overlayRaw.outline || '#000000';
  const textX = Number(overlay.x_pct ?? 50);
  const textY = Number(overlay.y_pct ?? 22);
  const splitTextSize = styleLayout === 'split' ? Number(sp.text_size ?? overlay.size ?? 68) : Number(overlay.size ?? 68);
  const splitTextX = styleLayout === 'split' ? Number(sp.text_x_pct ?? textX) : textX;
  const splitTextY = styleLayout === 'split' ? Number(sp.text_y_pct ?? textY) : textY;

  const fitted = useMemo(() => fitOverlayLines(
    overlayRaw.lines, splitTextSize, `900 ${splitTextSize}px "${fontFamilyBase}"`,
    canvasWidth || 1080, overlay.min_size,
  ), [overlayRaw.lines, splitTextSize, fontFamilyBase, canvasWidth, overlay.min_size]);
  const renderLines = overlay.auto_fit === false ? (overlayRaw.lines || []).slice(0, 3) : fitted.lines;
  const renderSize = overlay.auto_fit === false ? splitTextSize : fitted.size;

  const bgEnabled = overlay.bg_enabled === true;
  const boxRadius = Number(overlay.box_radius ?? 10);
  const boxPadding = Number(overlay.box_padding ?? 14);
  const bgStyle = bgEnabled
    ? {
        background: withAlpha(overlay.bg_color || '#000000', overlay.bg_opacity ?? 0.65),
        borderRadius: boxRadius,
        padding: `${Math.round(boxPadding * 0.6)}px ${boxPadding}px`,
      }
    : {};

  const videoProps = {
    src: videoUrl,
    startFrom: 0,
    muted: true,
    playbackRate: speed,
  };

  if (styleLayout === 'blocked') {
    return (
      <AbsoluteFill style={{ backgroundColor: '#111', color: '#ff8866', alignItems: 'center', justifyContent: 'center', padding: 40, textAlign: 'center', fontSize: 28 }}>
        RENDU BLOQUE — STYLE PUR inconnu. Choisis blur / split_scene / reframing.
      </AbsoluteFill>
    );
  }

  return (
    <AbsoluteFill style={{ backgroundColor: '#050505', overflow: 'hidden' }}>
      {isMulti && (
        <div style={{ position: 'absolute', right: 14, bottom: 14, zIndex: 50, pointerEvents: 'none', padding: '4px 10px', borderRadius: 6, background: 'rgba(0,0,0,0.55)', color: '#00ff88', fontSize: 13, fontWeight: 800 }}>
          VIDEO {safeIndex + 1}/{entries.length} · {entry.angle_id || entry.source_id || '?'}
        </div>
      )}

      <AbsoluteFill style={{ transform: antiTransform || undefined, transformOrigin: 'center center' }}>
        {videoUrl ? (
          styleLayout === 'blur' ? (
            <>
              <Video {...videoProps}
                style={{ width: '100%', height: '100%', objectFit: 'cover', filter: `blur(${Number(sp.degree || 24)}px) brightness(0.6)`, transform: `scale(${(Number(sp.bg_scale || 118) / 100).toFixed(4)})` }} />
              <div style={{ position: 'absolute', left: 0, right: 0, top: `${Number(sp.fg_y_pct ?? 62)}%`, height: `${Number(sp.fg_scale || 72)}%`, transform: 'translateY(-50%)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Video {...videoProps}
                  style={{ width: '100%', height: '100%', objectFit: 'cover', boxShadow: '0 12px 48px rgba(0,0,0,0.65)' }} />
              </div>
            </>
          ) : styleLayout === 'split' ? (
            <>
              <div style={{ position: 'absolute', left: 0, top: 0, width: '100%', height: `${Number(sp.top_scale || 62)}%`, overflow: 'hidden' }}>
                <Video {...videoProps} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              </div>
              <div style={{ position: 'absolute', left: 0, top: `${Number(sp.top_scale || 62)}%`, width: '100%', height: `${Number(sp.bottom_scale || 38)}%`, background: 'linear-gradient(180deg, #0a0a12 0%, #050505 100%)', borderTop: '2px solid rgba(255,255,255,0.12)' }} />
            </>
          ) : (
            <Video {...videoProps}
              style={{ width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${(Number(sp.scale || 130) / 100).toFixed(4)}) translate(${Number(sp.offset_x_pct || 0)}%, ${Number(sp.offset_y_pct || 0)}%)` }} />
          )
        ) : (
          <div style={{ color: '#ff8866', fontSize: 40, textAlign: 'center', alignSelf: 'center' }}>
            CLIP PUR MANQUANT — lance F00_PUR
          </div>
        )}
      </AbsoluteFill>

      {overlayVisible && (
        <AbsoluteFill style={{ pointerEvents: 'none' }}>
          <div
            style={{
              position: 'absolute',
              left: `${splitTextX}%`,
              top: `${splitTextY}%`,
              maxWidth: '92%',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'flex-start',
              gap: 4,
              transform: 'translateX(-50%)',
            }}
          >
            {renderLines.map((line, index) => (
              <div
                key={`pur_line_${index}`}
                style={{
                  fontFamily: `"${fontFamilyBase}", sans-serif`,
                  fontSize: renderSize,
                  fontWeight: 900,
                  lineHeight: 1.12,
                  textTransform: uppercase ? 'uppercase' : 'none',
                  color: lineColors[index] || lineColors[0],
                  WebkitTextStroke: outlineWidth > 0 ? `${outlineWidth}px ${outlineColor}` : undefined,
                  paintOrder: 'stroke fill',
                  textShadow: outlineWidth > 0 ? undefined : '0 2px 12px rgba(0,0,0,0.5)',
                  ...bgStyle,
                  whiteSpace: 'nowrap',
                }}
              >
                {line}
              </div>
            ))}
          </div>
        </AbsoluteFill>
      )}

      {pur.outro?.type === 'fade_to_black' && (() => {
        const outroFrames = Math.round(Number(pur.outro.duration_sec || 1) * fps);
        const outroStart = durationInFrames - outroFrames;
        if (frame < outroStart) return null;
        const p = (frame - outroStart) / Math.max(1, outroFrames);
        return <AbsoluteFill style={{ background: `rgba(0,0,0,${(p * 0.95).toFixed(3)})`, pointerEvents: 'none' }} />;
      })()}
    </AbsoluteFill>
  );
}

export default PurPackComposition;

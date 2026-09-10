/* ═══════════════════════════════════════════════════════════════════
   PurPackComposition — Mode PUR côté RENDU (F04 PICTOR)
   Miroir exact du composant F03 Preview : mêmes calques, mêmes valeurs.
   Consomme codex.pur_manifest (dev10.pur.v1) + clips téléchargés par F00-PUR.
   Gère les 4 mises en page : blur / split / reframing / fullscreen.
   ═══════════════════════════════════════════════════════════════════ */
import React from 'react';
import { AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame, useVideoConfig, Video } from 'remotion';
import { normalizePurManifest, purZoomAtFrame, purAntiTransform, normalizePurStyleParams, normalizePurOverlayParams } from './purPackCompilation';

/** '#RRGGBB' + opacité 0-1 → 'rgba(r,g,b,a)'. */
function withAlpha(hex, alpha) {
  const m = String(hex || '').match(/^#?([0-9a-f]{6})$/i);
  if (!m) return hex;
  const n = parseInt(m[1], 16);
  return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${Number(alpha ?? 1).toFixed(3)})`;
}

export function PurPackComposition({ purManifest: rawManifest }) {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const manifest = normalizePurManifest(rawManifest, fps);
  const entry = manifest.entries?.[0] || {};
  const overlayRaw = manifest.narrative?.overlay || {};
  const overlay = { ...overlayRaw, ...normalizePurOverlayParams(overlayRaw.style_params) };
  const pur = manifest.pur || {};

  const styleName = String(manifest.style || '');
  const styleLayout = styleName === 'blur' ? 'blur'
    : styleName === 'split_scene' ? 'split'
    : styleName === 'reframing' ? 'reframing'
    : 'fullscreen';
  const sp = normalizePurStyleParams(manifest.style_params, styleName || 'blur');

  const videoUrl = entry.clip_file ? staticFile(entry.clip_file.replace(/^\.?\//, '')) : null;

  const anti = entry.anti_detection || {};
  const speed = Number(anti.speed || 1);
  const antiTransform = purAntiTransform(anti, frame, fps);
  const zoomScale = purZoomAtFrame(entry.zooms, frame);

  const overlayFrom = Number(overlayRaw.visible_from_frame ?? Math.round(3 * fps));
  const popFrames = Number(overlayRaw.animation_frames ?? 6);
  const popProgress = Math.min(1, (frame - overlayFrom) / Math.max(1, popFrames));
  const overlayVisible = frame >= overlayFrom && overlayRaw.lines?.length > 0;
  const popScale = overlayVisible ? (0.9 + 0.2 * Math.min(1, popProgress) - 0.1 * Math.max(0, popProgress - 0.55)) : 1;

  // Texte overlay : valeurs éditoriales (avec fallback legacy color/accent/font_size/outline)
  const lineColors = [overlay.line1_color || overlayRaw.color || '#FFFFFF', overlay.line2_color || overlayRaw.accent || '#FFD700'];
  const fontFamily = `${overlay.font_family || overlayRaw.fallback_font || 'Arial Black, Impact'}, sans-serif`;
  const fontSize = Number(overlay.size ?? overlayRaw.font_size ?? 68);
  const outlineWidth = Number(overlay.outline_width ?? 3);
  const outlineColor = overlay.outline_color || overlayRaw.outline || '#000000';
  const textX = Number(overlay.x_pct ?? 50);
  const textY = Number(overlay.y_pct ?? 22);
  const splitTextSize = styleLayout === 'split' ? Number(sp.text_size ?? fontSize) : fontSize;
  const splitTextX = styleLayout === 'split' ? Number(sp.text_x_pct ?? textX) : textX;
  const splitTextY = styleLayout === 'split' ? Number(sp.text_y_pct ?? textY) : textY;
  const bgEnabled = overlay.bg_enabled === true;
  const bgStyle = bgEnabled
    ? { background: withAlpha(overlay.bg_color || '#000000', overlay.bg_opacity ?? 0.65), padding: '4px 14px', borderRadius: 6 }
    : {};

  const videoProps = {
    src: videoUrl,
    startFrom: Math.round(frame * speed),
    muted: true,
    playbackRate: speed,
  };

  return (
    <AbsoluteFill style={{ backgroundColor: '#050505', overflow: 'hidden' }}>
      {(manifest.sfx_available === true ? entry.sfx_list || [] : []).map((sfx, index) => (
        Math.abs(frame - Number(sfx.moment_frame || 0)) < 1 && sfx.type ? (
          <Sequence key={`pur_sfx_${index}`} from={Number(sfx.moment_frame || 0)} durationInFrames={Math.max(1, durationInFrames - Number(sfx.moment_frame || 0))}>
            <Audio src={staticFile(`sfx/${sfx.type}.mp3`)} volume={Number(sfx.volume ?? 0.55)} />
          </Sequence>
        ) : null
      ))}

      <AbsoluteFill style={{ transform: antiTransform, transformOrigin: 'center center' }}>
        {videoUrl ? (
          styleLayout === 'blur' ? (
            /* ── BLUR : couche arrière floutée + couche avant nette ── */
            <>
              <Video {...videoProps}
                style={{ width: '100%', height: '100%', objectFit: 'cover', filter: `blur(${Number(sp.degree || 24)}px) brightness(0.6)`, transform: `scale(${(Number(sp.bg_scale || 118) / 100).toFixed(4)})` }} />
              <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Video {...videoProps}
                  style={{ width: '100%', height: `${Number(sp.fg_scale || 72)}%`, objectFit: 'cover', boxShadow: '0 12px 48px rgba(0,0,0,0.65)' }} />
              </div>
            </>
          ) : styleLayout === 'split' ? (
            /* ── SPLIT : vidéo en haut (top_scale%) + élément bas (bottom_scale%) ── */
            <>
              <div style={{ position: 'absolute', left: 0, top: 0, width: '100%', height: `${Number(sp.top_scale || 62)}%`, overflow: 'hidden' }}>
                <Video {...videoProps}
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              </div>
              <div style={{ position: 'absolute', left: 0, top: `${Number(sp.top_scale || 62)}%`, width: '100%', height: `${Number(sp.bottom_scale || 38)}%`, background: 'linear-gradient(180deg, #0a0a12 0%, #050505 100%)', borderTop: '2px solid rgba(255,255,255,0.12)' }} />
            </>
          ) : styleLayout === 'reframing' ? (
            /* ── REFRAMING : recadrage scale + offset X/Y ── */
            <Video {...videoProps}
              style={{ width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${(Number(sp.scale || 130) / 100).toFixed(4)}) translate(${Number(sp.offset_x_pct || 0)}%, ${Number(sp.offset_y_pct || 0)}%)` }} />
          ) : (
            /* ── FULLSCREEN (ranking / style inconnu) : clip plein écran ── */
            <Video {...videoProps}
              style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          )
        ) : (
          <div style={{ color: '#ff8866', fontSize: 40, textAlign: 'center', alignSelf: 'center' }}>
            CLIP PUR MANQUANT — F00-PUR doit télécharger le segment
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
              maxWidth: '88%',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'flex-start',
              gap: 6,
              transform: `translateX(-50%) scale(${popScale.toFixed(3)})`,
              transformOrigin: 'center top',
            }}
          >
            {overlayRaw.lines.map((line, index) => (
              <div
                key={`pur_line_${index}`}
                style={{
                  fontFamily,
                  fontSize: splitTextSize,
                  fontWeight: 900,
                  lineHeight: 1.04,
                  textTransform: 'uppercase',
                  color: lineColors[index] || lineColors[0],
                  WebkitTextStroke: `${outlineWidth}px ${outlineColor}`,
                  textShadow: '0 4px 18px rgba(0,0,0,0.85)',
                  ...bgStyle,
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

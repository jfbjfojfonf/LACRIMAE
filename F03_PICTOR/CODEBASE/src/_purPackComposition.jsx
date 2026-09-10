/* ═══════════════════════════════════════════════════════════════════
   PurPackComposition — Mode PUR côté RENDU (F04 PICTOR)
   Miroir exact du composant F03 Preview : mêmes calques, mêmes valeurs.
   v2 TEXTE (2026-09-10) : statique début→fin, auto-fit, boîte arrondie,
   casse mixte, blur positionnable — identique au preview.
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

/**
 * Auto-fit SANS Canvas API (rendu Node) : ratio de largeur moyenne d'un
 * glyphe en ExtraBold ≈ 0.62 × taille. Même formule que le preview ne
 * peut pas être garanti au pixel — on reste conservateur (0.62) pour ne
 * JAMAIS dépasser la largeur utile. Le preview reste la référence visuelle.
 */
function fitOverlayLinesNode(lines, baseSize, canvasWidth, minSize) {
  const list = (lines || []).slice(0, 3).map((l) => String(l));
  if (!canvasWidth || list.length === 0) return { lines: list, size: baseSize };
  const usable = canvasWidth * 0.92;
  const widest = Math.max(...list.map((l) => l.length * baseSize * 0.62));
  if (widest <= usable) return { lines: list, size: baseSize };
  const fitted = Math.max(Number(minSize || 28), Math.floor(baseSize * (usable / widest)));
  return { lines: list, size: fitted };
}

export function PurPackComposition({ purManifest: rawManifest }) {
  const frame = useCurrentFrame();
  const { fps, durationInFrames, width: canvasWidth } = useVideoConfig();
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

  // v2 : texte STATIQUE — visible du début à la fin, pas d'animation
  const staticText = overlay.static_text !== false;
  const overlayVisible = staticText
    ? overlayRaw.lines?.length > 0
    : frame >= Number(overlayRaw.visible_from_frame ?? Math.round(3 * fps)) && overlayRaw.lines?.length > 0;

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

  const fitted = fitOverlayLinesNode(overlayRaw.lines, splitTextSize, canvasWidth || 1080, overlay.min_size);
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
            /* ── BLUR : couche arrière floutée + couche avant nette positionnable ── */
            <>
              <Video {...videoProps}
                style={{ width: '100%', height: '100%', objectFit: 'cover', filter: `blur(${Number(sp.degree || 24)}px) brightness(0.6)`, transform: `scale(${(Number(sp.bg_scale || 118) / 100).toFixed(4)})` }} />
              <div style={{ position: 'absolute', left: 0, right: 0, top: `${Number(sp.fg_y_pct ?? 62)}%`, height: `${Number(sp.fg_scale || 72)}%`, transform: 'translateY(-50%)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Video {...videoProps}
                  style={{ width: '100%', height: '100%', objectFit: 'cover', boxShadow: '0 12px 48px rgba(0,0,0,0.65)' }} />
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

      {/* Overlay titre PUR : STATIQUE du début à la fin (v2) — pas d'animation */}
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

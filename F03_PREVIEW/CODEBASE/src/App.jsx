import React, { useMemo, useRef, useState } from 'react';
import { Player } from '@remotion/player';
import { PurPackComposition } from './preview/_purPackComposition';
import {
  parsePurPack,
  parsePurPackMulti,
  normalizePurOverlayParams,
  normalizePurStyleParams,
  PUR_STYLE_VALUES,
} from './preview/bridgeClipper';

const CANVAS = {
  '9:16': { width: 1080, height: 1920 },
  '16:9': { width: 1920, height: 1080 },
  '1:1': { width: 1080, height: 1080 },
};

export default function App() {
  const [packs, setPacks] = useState([]);
  const [manifest, setManifest] = useState(null);
  const [entryIndex, setEntryIndex] = useState(0);
  const [canvas, setCanvas] = useState('9:16');
  const [style, setStyle] = useState('blur');
  const [error, setError] = useState(null);
  const playerRef = useRef(null);

  const size = CANVAS[canvas] || CANVAS['9:16'];
  const overlay = normalizePurOverlayParams(manifest?.narrative?.overlay?.style_params);
  const styleParams = normalizePurStyleParams(manifest?.style_params, manifest?.style || style);

  const rebuild = (nextPacks, nextStyle, nextCanvas, styleParamsOverride, overlayOverride) => {
    if (!nextPacks.length) {
      setManifest(null);
      return;
    }
    const parsed = nextPacks.length === 1
      ? parsePurPack(nextPacks[0], { fps: 30, canvas: nextCanvas, clipFiles: [`clips/pur_${nextPacks[0].identite?.angle_id || 'A01'}.mp4`], style: nextStyle, styleParams: styleParamsOverride, overlayParams: overlayOverride })
      : parsePurPackMulti(nextPacks, {
          fps: 30,
          canvas: nextCanvas,
          clipFiles: nextPacks.map((p, i) => `clips/pur_${p.identite?.angle_id || p.pack_id || `clip${i + 1}`}.mp4`),
          style: nextStyle,
          styleParams: styleParamsOverride,
          overlayParams: overlayOverride,
        });
    setManifest(parsed);
    setError(parsed.style_unknown ? `Style refuse : ${parsed.style_source}. Choisis blur / split_scene / reframing.` : null);
  };

  const onFiles = async (fileList) => {
    const files = Array.from(fileList || []);
    const loaded = [];
    for (const file of files) {
      loaded.push(JSON.parse(await file.text()));
    }
    setPacks(loaded);
    setEntryIndex(0);
    rebuild(loaded, style, canvas);
  };

  const patchStyle = (partial) => {
    const next = { ...styleParams, ...partial };
    rebuild(packs, style, canvas, next, overlay);
  };

  const patchOverlay = (partial) => {
    const next = { ...overlay, ...partial };
    rebuild(packs, style, canvas, styleParams, next);
  };

  const durationInFrames = Math.max(1, Number(manifest?.entries?.[entryIndex]?.duration_seconds || manifest?.duration_seconds || 30) * 30);

  const composition = useMemo(() => (props) => (
    <PurPackComposition {...props} purManifest={manifest} entryIndex={entryIndex} />
  ), [manifest, entryIndex]);

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#0b0b0f', color: '#eee', fontFamily: 'sans-serif' }}>
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
        {manifest ? (
          <Player
            ref={playerRef}
            component={composition}
            durationInFrames={durationInFrames}
            fps={30}
            compositionWidth={size.width}
            compositionHeight={size.height}
            style={{ maxHeight: '90vh', width: 'auto' }}
            controls
          />
        ) : (
          <div style={{ opacity: 0.7 }}>Depose un production_pack_pur_*.json</div>
        )}
      </div>
      <aside style={{ width: 360, padding: 16, borderLeft: '1px solid #222', overflow: 'auto' }}>
        <h1 style={{ fontSize: 18 }}>F03 PREVIEW — PUR LOOK</h1>
        <p style={{ fontSize: 12, opacity: 0.7 }}>blur / split / reframing. Zero zoom.</p>
        <input type="file" accept="application/json" multiple onChange={(e) => onFiles(e.target.files)} />
        {error && <p style={{ color: '#ff8866' }}>{error}</p>}

        <label>Canvas</label>
        <select value={canvas} onChange={(e) => { setCanvas(e.target.value); rebuild(packs, style, e.target.value, styleParams, overlay); }}>
          <option value="9:16">9:16</option>
          <option value="16:9">16:9</option>
          <option value="1:1">1:1</option>
        </select>

        <label>Style</label>
        <select value={style} onChange={(e) => { setStyle(e.target.value); rebuild(packs, e.target.value, canvas, undefined, overlay); }}>
          {PUR_STYLE_VALUES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>

        {packs.length > 1 && (
          <div>
            <button type="button" onClick={() => setEntryIndex((i) => Math.max(0, i - 1))}>prev</button>
            <span> video {entryIndex + 1}/{packs.length} </span>
            <button type="button" onClick={() => setEntryIndex((i) => Math.min(packs.length - 1, i + 1))}>next</button>
          </div>
        )}

        {style === 'blur' && (
          <fieldset>
            <legend>blur</legend>
            <label>degree <input type="number" value={styleParams.degree} onChange={(e) => patchStyle({ degree: Number(e.target.value) })} /></label>
            <label>fg_y_pct <input type="number" value={styleParams.fg_y_pct} onChange={(e) => patchStyle({ fg_y_pct: Number(e.target.value) })} /></label>
          </fieldset>
        )}
        {style === 'split_scene' && (
          <fieldset>
            <legend>split</legend>
            <label>top_scale <input type="number" value={styleParams.top_scale} onChange={(e) => patchStyle({ top_scale: Number(e.target.value) })} /></label>
          </fieldset>
        )}
        {style === 'reframing' && (
          <fieldset>
            <legend>reframing (fixe)</legend>
            <label>scale <input type="number" value={styleParams.scale} onChange={(e) => patchStyle({ scale: Number(e.target.value) })} /></label>
            <label>offset_y <input type="number" value={styleParams.offset_y_pct} onChange={(e) => patchStyle({ offset_y_pct: Number(e.target.value) })} /></label>
          </fieldset>
        )}

        <fieldset>
          <legend>overlay</legend>
          <label>size <input type="number" value={overlay.size} onChange={(e) => patchOverlay({ size: Number(e.target.value) })} /></label>
          <label>y_pct <input type="number" value={overlay.y_pct} onChange={(e) => patchOverlay({ y_pct: Number(e.target.value) })} /></label>
        </fieldset>
      </aside>
    </div>
  );
}

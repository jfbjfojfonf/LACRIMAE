import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  CANVAS,
  DEFAULT_STYLE,
  MOTION_VALUES,
  activeWords,
  buildProofRequest,
  downloadJson,
  firstWord,
  normalizeStyle,
  parseTranscript,
} from './styleSchema';

const field = { display: 'block', margin: '8px 0 4px', fontSize: 12, opacity: 0.8 };
const input = { width: '100%', background: '#16161c', color: '#eee', border: '1px solid #333', padding: 6 };

export default function App() {
  const [style, setStyle] = useState(DEFAULT_STYLE);
  const [transcript, setTranscript] = useState(null);
  const [error, setError] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [videoName, setVideoName] = useState('');
  const [time, setTime] = useState(0);
  const [proof, setProof] = useState(null);
  const [proofBusy, setProofBusy] = useState(false);
  const videoRef = useRef(null);
  const size = CANVAS[style.canvas] || CANVAS['9:16'];
  const wordsNow = useMemo(() => activeWords(transcript, time), [transcript, time]);
  const punch = wordsNow[0]?.word || firstWord(transcript);

  useEffect(() => () => {
    if (videoUrl) URL.revokeObjectURL(videoUrl);
  }, [videoUrl]);

  const patch = (partial) => setStyle((prev) => normalizeStyle({ ...prev, ...partial }));
  const patchNested = (key, partial) => setStyle((prev) => normalizeStyle({
    ...prev,
    [key]: { ...(prev[key] || {}), ...partial },
  }));

  const onTranscript = async (file) => {
    if (!file) return;
    try {
      const parsed = parseTranscript(JSON.parse(await file.text()));
      if (!parsed.words.length) {
        setError('transcript.json : aucun mot valide (word + start < end)');
        setTranscript(null);
        return;
      }
      setTranscript(parsed);
      setError(null);
    } catch (exc) {
      setError(`transcript.json illisible : ${exc.message}`);
      setTranscript(null);
    }
  };

  const onStyleFile = async (file) => {
    if (!file) return;
    try {
      setStyle(normalizeStyle(JSON.parse(await file.text())));
      setError(null);
    } catch (exc) {
      setError(`style.json illisible : ${exc.message}`);
    }
  };

  const onVideo = (file) => {
    if (!file) return;
    if (videoUrl) URL.revokeObjectURL(videoUrl);
    setVideoUrl(URL.createObjectURL(file));
    setVideoName(file.name);
    setTime(0);
  };

  const onProofPng = (file) => {
    if (!file) return;
    if (proof?.url) URL.revokeObjectURL(proof.url);
    setProof({ name: file.name, url: URL.createObjectURL(file) });
  };

  const requestProof = async () => {
    const payload = buildProofRequest(style, punch, videoName);
    downloadJson('proof.json', payload);
    setProofBusy(true);
    setError(null);
    try {
      const res = await fetch('/api/proof', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        setError('Proof Modal indisponible (H3 via GHA). proof.json telecharge — depose le PNG ensuite.');
        return;
      }
      const blob = await res.blob();
      if (proof?.url) URL.revokeObjectURL(proof.url);
      setProof({ name: 'proof.png', url: URL.createObjectURL(blob) });
    } catch {
      setError('Proof Modal indisponible (H3 via GHA). proof.json telecharge — depose le PNG ensuite.');
    } finally {
      setProofBusy(false);
    }
  };

  const glowPx = Math.round(style.glow.intensity * 10);
  const scale = style.motion === 'pop-in' ? 1.08 : style.motion === 'bounce' ? 1.04 : 1;
  const previewRatio = size.width / size.height;

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#0b0b0f', color: '#eee', fontFamily: 'sans-serif' }}>
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
        <div style={{
          position: 'relative',
          width: Math.min(420, size.width * 0.35),
          aspectRatio: `${previewRatio}`,
          background: '#111',
          overflow: 'hidden',
          border: '1px solid #222',
        }}>
          {videoUrl ? (
            <video
              ref={videoRef}
              src={videoUrl}
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              controls
              onTimeUpdate={(e) => setTime(e.currentTarget.currentTime || 0)}
            />
          ) : (
            <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: 0.5 }}>
              Depose une video IN
            </div>
          )}
          {proof?.url ? (
            <img
              src={proof.url}
              alt="proof blender"
              style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'contain', pointerEvents: 'none' }}
            />
          ) : (
            <div style={{
              position: 'absolute',
              left: `${style.position.x_pct}%`,
              top: `${style.position.y_pct}%`,
              transform: `translate(-50%, -50%) scale(${scale})`,
              fontFamily: 'Montserrat ExtraBold, Montserrat, sans-serif',
              fontSize: style.size * 0.35,
              fontWeight: 800,
              color: style.color,
              WebkitTextStroke: `${style.outline.width * 0.35}px ${style.outline.color}`,
              textShadow: `0 0 ${glowPx}px ${style.glow.color}, 0 0 ${glowPx * 2}px ${style.glow.color}`,
              whiteSpace: 'nowrap',
              pointerEvents: 'none',
            }}>{punch}</div>
          )}
        </div>
      </div>
      <aside style={{ width: 360, padding: 16, borderLeft: '1px solid #222', overflow: 'auto' }}>
        <h1 style={{ fontSize: 18 }}>F07 PREVIEW — CAPTION s1</h1>
        <p style={{ fontSize: 12, opacity: 0.7 }}>Proxy JS. Glow reel = proof Blender (1 mot, 1–3 frames). Pas de live GPU.</p>

        <label style={field}>transcript.json</label>
        <input type="file" accept="application/json" onChange={(e) => onTranscript(e.target.files?.[0])} />
        <label style={field}>video IN</label>
        <input type="file" accept="video/*" onChange={(e) => onVideo(e.target.files?.[0])} />
        <label style={field}>style.json (optionnel)</label>
        <input type="file" accept="application/json" onChange={(e) => onStyleFile(e.target.files?.[0])} />
        {error && <p style={{ color: '#ff8866', fontSize: 12 }}>{error}</p>}
        {transcript && <p style={{ fontSize: 12 }}>C1 : {transcript.words.length} mots — punch « {punch} »</p>}

        <label style={field}>Canvas</label>
        <select style={input} value={style.canvas} onChange={(e) => patch({ canvas: e.target.value })}>
          {Object.keys(CANVAS).map((key) => <option key={key} value={key}>{key}</option>)}
        </select>
        <label style={field}>Police</label>
        <input style={input} value={style.font} onChange={(e) => patch({ font: e.target.value })} />
        <label style={field}>Taille {style.size}</label>
        <input type="range" min="12" max="240" value={style.size} onChange={(e) => patch({ size: Number(e.target.value) })} />
        <label style={field}>x_pct {style.position.x_pct}</label>
        <input type="range" min="0" max="100" value={style.position.x_pct} onChange={(e) => patchNested('position', { x_pct: Number(e.target.value) })} />
        <label style={field}>y_pct {style.position.y_pct}</label>
        <input type="range" min="0" max="100" value={style.position.y_pct} onChange={(e) => patchNested('position', { y_pct: Number(e.target.value) })} />
        <label style={field}>Couleur</label>
        <input type="color" value={style.color} onChange={(e) => patch({ color: e.target.value })} />
        <label style={field}>Contour {style.outline.width}</label>
        <input type="range" min="0" max="24" value={style.outline.width} onChange={(e) => patchNested('outline', { width: Number(e.target.value) })} />
        <input type="color" value={style.outline.color} onChange={(e) => patchNested('outline', { color: e.target.value })} />
        <label style={field}>Glow {style.glow.intensity}</label>
        <input type="range" min="0" max="5" step="0.1" value={style.glow.intensity} onChange={(e) => patchNested('glow', { intensity: Number(e.target.value) })} />
        <input type="color" value={style.glow.color} onChange={(e) => patchNested('glow', { color: e.target.value })} />
        <label style={field}>Mouvement</label>
        <select style={input} value={style.motion} onChange={(e) => patch({ motion: e.target.value })}>
          {MOTION_VALUES.map((m) => <option key={m} value={m}>{m}</option>)}
        </select>

        <fieldset style={{ marginTop: 16, borderColor: '#333' }}>
          <legend>C2 / C3</legend>
          <button type="button" onClick={() => downloadJson('style.json', normalizeStyle(style))}>exporter s1</button>
          <button type="button" onClick={requestProof} disabled={proofBusy} style={{ marginLeft: 8 }}>
            {proofBusy ? 'proof…' : `proof « ${punch} »`}
          </button>
          <label style={field}>deposer PNG proof Blender</label>
          <input type="file" accept="image/png,image/exr" onChange={(e) => onProofPng(e.target.files?.[0])} />
          {proof && <p style={{ fontSize: 12 }}>C3 plaque : {proof.name}</p>}
        </fieldset>
      </aside>
    </div>
  );
}

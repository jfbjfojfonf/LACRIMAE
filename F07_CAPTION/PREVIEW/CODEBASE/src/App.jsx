import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  CANVAS,
  DEFAULT_STYLE,
  MOTION_VALUES,
  buildProofRequest,
  captionCouple,
  downloadJson,
  firstWord,
  motionScale,
  normalizeStyle,
  parseTranscript,
} from './styleSchema';

const field = { display: 'block', margin: '8px 0 4px', fontSize: 12, opacity: 0.8 };
const input = { width: '100%', background: '#16161c', color: '#eee', border: '1px solid #333', padding: 6 };
const btn = { background: '#222', color: '#eee', border: '1px solid #444', padding: '6px 10px', cursor: 'pointer' };

function muteNativeCaptions(video) {
  if (!video || !video.textTracks) return;
  for (let i = 0; i < video.textTracks.length; i += 1) {
    video.textTracks[i].mode = 'disabled';
  }
}

function captionFace(style, extra) {
  const glowPx = Math.max(6, Math.round(style.glow.intensity * 12));
  return {
    fontFamily: '"Montserrat ExtraBold", Montserrat, sans-serif',
    fontWeight: 800,
    color: style.color,
    WebkitTextStroke: `${Math.max(1, style.outline.width * 0.28)}px ${style.outline.color}`,
    paintOrder: 'stroke fill',
    textShadow: `0 0 ${glowPx}px ${style.glow.color}, 0 2px 8px rgba(0,0,0,0.85)`,
    whiteSpace: 'nowrap',
    pointerEvents: 'none',
    lineHeight: 1,
    ...extra,
  };
}

export default function App() {
  const [style, setStyle] = useState(DEFAULT_STYLE);
  const [transcript, setTranscript] = useState(null);
  const [error, setError] = useState(null);
  const [saveMsg, setSaveMsg] = useState('');
  const [videoUrl, setVideoUrl] = useState(null);
  const [videoName, setVideoName] = useState('');
  const [time, setTime] = useState(0);
  const [proof, setProof] = useState(null);
  const [proofBusy, setProofBusy] = useState(false);
  const videoRef = useRef(null);
  const jsonRef = useRef(null);
  const size = CANVAS[style.canvas] || CANVAS['9:16'];
  const couple = useMemo(() => captionCouple(transcript, time), [transcript, time]);
  const spokenWord = couple.spoken === 'right' ? couple.right : couple.left;
  const punch = spokenWord?.word || firstWord(transcript);
  const packed = useMemo(() => normalizeStyle(style), [style]);
  const jsonText = useMemo(() => JSON.stringify(packed, null, 2) + '\n', [packed]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [trRes, stRes] = await Promise.all([
          fetch('/transcript.json'),
          fetch('/style.json'),
        ]);
        if (cancelled) return;
        if (trRes.ok) {
          const parsed = parseTranscript(await trRes.json());
          if (parsed.words.length) setTranscript(parsed);
        }
        if (stRes.ok) setStyle(normalizeStyle(await stRes.json()));
        const probe = await fetch('/target.mp4', { method: 'HEAD' });
        if (!cancelled && probe.ok) {
          setVideoUrl('/target.mp4');
          setVideoName('target.mp4');
        }
      } catch {
        /* preview assets optionnels */
      }
    })();
    return () => { cancelled = true; };
  }, []);

  useEffect(() => () => {
    if (videoUrl && videoUrl.startsWith('blob:')) URL.revokeObjectURL(videoUrl);
  }, [videoUrl]);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return undefined;
    muteNativeCaptions(video);
    let raf = 0;
    const tick = () => {
      setTime(video.currentTime || 0);
      raf = requestAnimationFrame(tick);
    };
    const onMeta = () => muteNativeCaptions(video);
    video.addEventListener('loadedmetadata', onMeta);
    raf = requestAnimationFrame(tick);
    return () => {
      cancelAnimationFrame(raf);
      video.removeEventListener('loadedmetadata', onMeta);
    };
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
    if (videoUrl && videoUrl.startsWith('blob:')) URL.revokeObjectURL(videoUrl);
    setVideoUrl(URL.createObjectURL(file));
    setVideoName(file.name);
    setTime(0);
  };

  const onProofPng = (file) => {
    if (!file) return;
    if (proof?.url) URL.revokeObjectURL(proof.url);
    setProof({ name: file.name, url: URL.createObjectURL(file) });
  };

  const saveStyle = async () => {
    setSaveMsg('');
    setError(null);
    try {
      const res = await fetch('/api/save-style', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: jsonText,
      });
      const body = await res.json().catch(() => ({}));
      if (!res.ok || !body.ok) {
        setError('Save s1 echoue — JSON non ecrit');
        return;
      }
      setSaveMsg(`C2 : ${body.path}`);
    } catch {
      setError('Save s1 indisponible');
    }
  };

  const selectAllJson = () => {
    const el = jsonRef.current;
    if (!el) return;
    el.focus();
    el.select();
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

  const elapsed = spokenWord ? Math.max(0, time - spokenWord.start) : 0;
  const spokenScale = motionScale(style.motion, elapsed, style.motion_speed);
  const popMs = `${(0.42 / Math.max(0.25, style.motion_speed)).toFixed(2)}s`;
  const previewRatio = size.width / size.height;
  const basePx = Math.max(28, style.size * 0.42);

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
              style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
              controls
              crossOrigin="anonymous"
              disablePictureInPicture
              onLoadedMetadata={(e) => muteNativeCaptions(e.currentTarget)}
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
              style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'contain', pointerEvents: 'none', zIndex: 4 }}
            />
          ) : (
            <div style={{
              position: 'absolute',
              left: `${style.position.x_pct}%`,
              top: `${style.position.y_pct}%`,
              transform: 'translate(-50%, -100%)',
              display: 'flex',
              flexDirection: 'row',
              alignItems: 'baseline',
              gap: 18,
              zIndex: 3,
              overflow: 'visible',
              pointerEvents: 'none',
              maxWidth: '92%',
            }}>
              {couple.left && (
                <div
                  key={`L-${couple.left.start}-${couple.left.word}`}
                  style={captionFace(style, {
                    fontSize: basePx,
                    transform: couple.spoken === 'left' && style.motion !== 'pop-in' ? `scale(${spokenScale})` : 'scale(1)',
                    transformOrigin: 'center',
                    animation: couple.spoken === 'left' && style.motion === 'pop-in'
                      ? `f07-popin ${popMs} cubic-bezier(0.16, 1.2, 0.3, 1) both`
                      : 'none',
                  })}
                >{couple.left.word}</div>
              )}
              {couple.right && (
                <div
                  key={`R-${couple.right.start}-${couple.right.word}`}
                  style={captionFace(style, {
                    fontSize: basePx,
                    transform: couple.spoken === 'right' && style.motion !== 'pop-in' ? `scale(${spokenScale})` : 'scale(1)',
                    transformOrigin: 'center',
                    animation: couple.spoken === 'right' && style.motion === 'pop-in'
                      ? `f07-popin ${popMs} cubic-bezier(0.16, 1.2, 0.3, 1) both`
                      : 'none',
                  })}
                >{couple.right.word}</div>
              )}
            </div>
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
        {saveMsg && <p style={{ color: '#8f8', fontSize: 12 }}>{saveMsg}</p>}
        {transcript && <p style={{ fontSize: 12 }}>C1 : {transcript.words.length} mots — couple « {couple.left?.word || ''} {couple.right?.word || ''} » — in « {punch} »</p>}

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
        {style.motion === 'pop-in' && (
          <>
            <label style={field}>Vitesse in {style.motion_speed}</label>
            <input
              type="range"
              min="0.25"
              max="3"
              step="0.05"
              value={style.motion_speed}
              onChange={(e) => patch({ motion_speed: Number(e.target.value) })}
            />
          </>
        )}

        <fieldset style={{ marginTop: 16, borderColor: '#333' }}>
          <legend>C2 / C3</legend>
          <button type="button" style={btn} onClick={saveStyle}>Save s1</button>
          <button type="button" style={{ ...btn, marginLeft: 8 }} onClick={selectAllJson}>tout selectionner</button>
          <label style={field}>s1 JSON</label>
          <textarea
            ref={jsonRef}
            readOnly
            value={jsonText}
            style={{ ...input, height: 160, fontFamily: 'monospace', fontSize: 11, resize: 'vertical' }}
          />
          <button type="button" style={{ ...btn, marginTop: 8 }} onClick={() => downloadJson('style.json', packed)}>exporter s1</button>
          <button type="button" style={{ ...btn, marginLeft: 8 }} onClick={requestProof} disabled={proofBusy}>
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

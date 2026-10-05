import React from 'react';
import { Composition } from 'remotion';
import { PurLook } from './PurLook';

export const RemotionRoot = () => (
  <Composition
    id="PurLook"
    component={PurLook}
    durationInFrames={900}
    fps={30}
    width={1080}
    height={1920}
    defaultProps={{
      purManifest: { schema_version: 'dev10.pur.v1', entries: [], style: 'blur', fps: 30, canvas: { width: 1080, height: 1920 } },
      entryIndex: 0,
      muted: false,
    }}
    calculateMetadata={({ props }) => {
      const manifest = props.purManifest || {};
      const entries = Array.isArray(manifest.entries) ? manifest.entries : [];
      const index = Math.max(0, Math.min(Number(props.entryIndex) || 0, Math.max(0, entries.length - 1)));
      const entry = entries[index] || {};
      const fps = Number(manifest.fps || 30);
      const duration = Number(entry.duration_seconds || manifest.duration_seconds || 30);
      const speed = Number(entry.anti_detection?.speed || 1) || 1;
      const canvas = manifest.canvas || {};
      return {
        durationInFrames: Math.max(1, Math.round((duration / speed) * fps)),
        fps,
        width: Number(canvas.width || 1080),
        height: Number(canvas.height || 1920),
      };
    }}
  />
);

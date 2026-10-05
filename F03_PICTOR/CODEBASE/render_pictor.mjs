#!/usr/bin/env node
/**
 * F03_PICTOR — rendu LOOK Remotion, miroir de F03_PREVIEW.
 * 1 asset = 1 MP4 compose (framing fixe, 0 zoom).
 *
 *   node F03_PICTOR/CODEBASE/render_pictor.mjs \
 *     --manifest BRIDGE_PERTURABO/OUT/pur_manifest.json \
 *     --clips F00_PUR/OUT \
 *     --out F03_PICTOR/OUT \
 *     [--entry 0] [--dry-run]
 */
import { spawnSync } from 'node:child_process';
import { copyFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(here, '../..');
const ALLOWED = new Set(['blur', 'split_scene', 'reframing']);
const ZOOM_BANNED = /\b(zoompan|breathing_zoom|swell|scaleX\(|scaleY\()\b/i;

const args = process.argv.slice(2);
const get = (flag) => {
  const i = args.indexOf(flag);
  return i >= 0 ? args[i + 1] : undefined;
};
const has = (flag) => args.includes(flag);

const manifestPath = get('--manifest') || resolve(ROOT, 'BRIDGE_PERTURABO/OUT/pur_manifest.json');
const clipsDir = get('--clips') || resolve(ROOT, 'F00_PUR/OUT');
const outDir = get('--out') || resolve(ROOT, 'F03_PICTOR/OUT');
const entryArg = get('--entry');
const dryRun = has('--dry-run');

function fail(msg, code = 1) {
  console.error(`✗ PICTOR : ${msg}`);
  process.exit(code);
}

if (!existsSync(manifestPath)) fail(`manifeste introuvable : ${manifestPath}`);
const manifest = JSON.parse(readFileSync(manifestPath, 'utf-8'));
if (manifest.schema_version !== 'dev10.pur.v1') fail(`schema_version=${manifest.schema_version}, attendu dev10.pur.v1`);
if (!ALLOWED.has(String(manifest.style || ''))) fail(`style « ${manifest.style} » hors blur/split_scene/reframing (G0-S / P2)`, 2);

const compositionSrc = resolve(here, 'src/PurLook.jsx');
const previewSrc = resolve(ROOT, 'F03_PREVIEW/CODEBASE/src/preview/_purPackComposition.jsx');
for (const src of [compositionSrc, previewSrc]) {
  if (!existsSync(src)) fail(`source LOOK absente : ${src}`);
  const text = readFileSync(src, 'utf-8');
  if (ZOOM_BANNED.test(text)) fail(`P-ZOOM ZERO : motif zoom/swell detecte dans ${src}`, 3);
}

const publicDir = resolve(here, 'public');
const publicClips = resolve(publicDir, 'clips');
mkdirSync(publicClips, { recursive: true });
const publicManifest = resolve(publicDir, 'pur_manifest.json');
writeFileSync(publicManifest, JSON.stringify(manifest, null, 2) + '\n');

const entries = Array.isArray(manifest.entries) ? manifest.entries : [];
if (!entries.length) fail('manifeste sans entrees');
const indices = entryArg != null ? [Number(entryArg)] : entries.map((_, i) => i);

function angleOf(entry) {
  const raw = String(entry.angle_id || entry.source_id || 'clip');
  return raw.toLowerCase().startsWith('pur_') ? raw.slice(4) : raw;
}

function resolveClip(entry) {
  const name = String(entry.clip_file || '').split('/').pop();
  const angle = angleOf(entry);
  const candidates = [
    name ? resolve(clipsDir, name) : null,
    resolve(clipsDir, `pur_${angle}.mp4`),
    name ? resolve(publicClips, name) : null,
  ].filter(Boolean);
  return candidates.find((p) => existsSync(p)) || null;
}

mkdirSync(outDir, { recursive: true });
const rendered = [];

for (const index of indices) {
  const entry = entries[index];
  if (!entry) fail(`entry ${index} hors bornes`);
  const angle = angleOf(entry);
  const clip = resolveClip(entry);
  if (!clip) fail(`CLIP PUR MANQUANT pour ${angle} — lance F00_PUR (P2)`);
  const publicClip = resolve(publicClips, `pur_${angle}.mp4`);
  if (clip !== publicClip) copyFileSync(clip, publicClip);
  entry.clip_file = `clips/pur_${angle}.mp4`;

  const props = { purManifest: manifest, entryIndex: index, muted: false };
  const dest = resolve(outDir, `pur_${angle}_look.mp4`);
  const propsFile = resolve(outDir, `pur_${angle}_look.props.json`);
  writeFileSync(propsFile, JSON.stringify(props));

  const cmd = [
    'npx', 'remotion', 'render', 'src/index.jsx', 'PurLook', dest,
    `--props=${propsFile}`,
    '--overwrite',
  ];
  console.log(`  [..] P2 LOOK ${angle} (${manifest.style}) → ${dest}`);
  if (dryRun) {
    console.log(`  [dry-run] ${cmd.join(' ')}`);
    rendered.push({ angle, dest, dryRun: true });
    continue;
  }
  const result = spawnSync(cmd[0], cmd.slice(1), { cwd: here, stdio: 'inherit', env: process.env });
  if (result.status !== 0) fail(`remotion render echoue pour ${angle} (exit ${result.status})`);
  rendered.push({ angle, dest });
  console.log(`  [ok] P2 LOOK ${angle}`);
}

writeFileSync(resolve(outDir, 'pictor_report.json'), JSON.stringify({
  schema_version: 'dev10-v2.pictor.v1',
  style: manifest.style,
  rendered,
}, null, 2) + '\n');
console.log(`✓ PICTOR : ${rendered.length} LOOK MP4 → ${outDir}`);

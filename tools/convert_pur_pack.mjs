#!/usr/bin/env node
/**
 * convert_pur_pack.mjs — pack(s) PUR PERTURABO → pur_manifest.json (dev10.pur.v1)
 *
 * Usage :
 *   node tools/convert_pur_pack.mjs --pack pack_pur_A01.json --out pur_manifest.json \
 *     [--canvas 9:16] [--clip clips/pur_A01.mp4] [--fps 30] [--style blur]
 *
 * MULTI-VIDEOS :
 *   node tools/convert_pur_pack.mjs --packs "EXPORT/pack_A01.json,EXPORT/pack_A02.json" \
 *     --out pur_manifest.json [--style blur] [--canvas 9:16]
 *
 * G0-S : style declare par le pack OU --style operateur.
 * Styles autorises : blur | split_scene | reframing.
 * Infere = REFUS (exit 2). Ranking refuse.
 */
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ALLOWED_STYLES = new Set(['blur', 'split_scene', 'reframing']);
const here = dirname(fileURLToPath(import.meta.url));

const args = process.argv.slice(2);
const get = (flag) => {
  const i = args.indexOf(flag);
  return i >= 0 ? args[i + 1] : undefined;
};
const packPath = get('--pack');
const packsList = get('--packs');
const outPath = get('--out');
const canvas = get('--canvas') || '9:16';
const clip = get('--clip') || '';
const fps = Number(get('--fps') || 30);
const refManifest = get('--style-params') || '';
const styleArg = get('--style');

if ((!packPath && !packsList) || !outPath) {
  console.error('usage: convert_pur_pack.mjs (--pack <pack.json> | --packs <p1.json,p2.json,…>) --out <manifest.json> [--canvas 9:16] [--clip clips/x.mp4] [--fps 30] [--style blur|split_scene|reframing] [--style-params ref_manifest.json]');
  process.exit(1);
}

if (styleArg && !ALLOWED_STYLES.has(String(styleArg).toLowerCase())) {
  console.error(`✗ REFUSÉ : --style « ${styleArg} » non autorisé.`);
  console.error('  → blur | split_scene | reframing uniquement. Ranking refuse.');
  process.exit(2);
}

const bridgeClipperUrl = new URL('../F03_PREVIEW/CODEBASE/src/preview/bridgeClipper.js', `file://${resolve(here)}/`);
const { parsePurPack, parsePurPackMulti } = await import(bridgeClipperUrl.href);

let refStyleParams;
let refOverlayParams;
if (refManifest) {
  try {
    const ref = JSON.parse(readFileSync(resolve(refManifest), 'utf-8'));
    refStyleParams = ref.style_params;
    refOverlayParams = ref.narrative?.overlay?.style_params;
    console.log(`  reglages operateur repris de ${refManifest}`);
  } catch (err) {
    console.error(`✗ --style-params illisible : ${err.message}`);
    process.exit(1);
  }
}

const loadPack = (p) => JSON.parse(readFileSync(resolve(p), 'utf-8'));

const checkStyleDeclared = (pack, source) => {
  const declaredStyle = String(pack.montage_style || pack.montage_instructions?.metadata?.style || '').toLowerCase();
  if (declaredStyle && !ALLOWED_STYLES.has(declaredStyle) && !styleArg) {
    console.error(`✗ REFUSÉ : style pack « ${declaredStyle} » non autorisé (${source}).`);
    console.error('  → relance avec --style blur|split_scene|reframing, ou regenere le pack cote PERTURABO.');
    process.exit(2);
  }
  if (!declaredStyle && !styleArg) {
    console.error(`✗ REFUSÉ : pack sans style déclaré (${source} : montage_style/metadata.style absent).`);
    console.error('  → relance avec --style blur|split_scene|reframing (ton choix),');
    console.error('    ou regenere le pack cote PERTURABO avec montage_style.');
    process.exit(2);
  }
};

const refuseUnknown = (manifest) => {
  if (manifest.style_source === 'inferred') {
    console.error('✗ REFUSÉ : style infere — BLOQUE par G0-S. C\'est TOI qui choisis.');
    process.exit(2);
  }
  if (manifest.style_unknown) {
    console.error(`✗ REFUSÉ : style « ${manifest.style_source} » non reconnu — BLOQUE par G0-S.`);
    process.exit(2);
  }
  if (!ALLOWED_STYLES.has(String(manifest.style || '').toLowerCase())) {
    console.error(`✗ REFUSÉ : style « ${manifest.style} » hors blur/split_scene/reframing.`);
    process.exit(2);
  }
};

let manifest;
if (packsList) {
  const packPaths = packsList.split(',').map((s) => s.trim()).filter(Boolean);
  const packs = packPaths.map((p) => loadPack(p));
  packs.forEach((pack, i) => checkStyleDeclared(pack, packPaths[i]));
  manifest = parsePurPackMulti(packs, {
    fps,
    canvas,
    clipFiles: packs.map((pack, i) => `clips/pur_${pack.identite?.angle_id || pack.pack_id || `clip${i + 1}`}.mp4`),
    style: styleArg,
    styleParams: refStyleParams,
    overlayParams: refOverlayParams,
  });
  if (!manifest.entries.length) {
    console.error('✗ Packs PUR illisibles (montage_instructions manquante ?)');
    process.exit(1);
  }
  refuseUnknown(manifest);
  console.log(`  style GLOBAL: ${manifest.style} (source: ${manifest.style_source}) — applique a ${manifest.entries.length} videos`);
  for (const e of manifest.entries) {
    console.log(`  ▸ ${e.source_id || e.angle_id || e.pack_label} → ${e.clip_file} (${e.duration_seconds}s, punch_in: ${e.zooms?.length || 0}, mirror: ${e.anti_detection?.mirror})`);
  }
} else {
  const pack = loadPack(packPath);
  checkStyleDeclared(pack, packPath);
  manifest = parsePurPack(pack, { fps, canvas, clipFiles: clip ? [clip] : [], style: styleArg, styleParams: refStyleParams, overlayParams: refOverlayParams });
  if (!manifest.entries.length) {
    console.error('✗ Pack PUR illisible (montage_instructions manquante ?)');
    process.exit(1);
  }
  refuseUnknown(manifest);
  console.log(`  style: ${manifest.style} (source: ${manifest.style_source})`);
}

const sfxDir = resolve('F03_PICTOR/CODEBASE/public/sfx');
const requiredSfx = [...new Set(manifest.entries
  .flatMap((e) => (e.sfx_list || []).map((s) => String(s.type || '')))
  .filter(Boolean))];
const missingSfx = [...new Set(requiredSfx.map((t) => (t === 'boom' ? 'impact' : t)))]
  .filter((t) => !existsSync(resolve(sfxDir, t + '.mp3')));
manifest.sfx_available = missingSfx.length === 0;
if (!manifest.sfx_available) {
  console.log('  SFX absents du codebase de rendu : ' + missingSfx.join(', ') + ' → sfx_available=false (rendu sans SFX)');
} else if (requiredSfx.length) {
  console.log('  SFX disponibles : ' + requiredSfx.join(', '));
}
manifest.clip_audio_available = true;

writeFileSync(resolve(outPath), JSON.stringify(manifest, null, 2) + '\n');
console.log(`✓ ${manifest.schema_version} ecrit : ${outPath}`);
console.log(`  entrees=${manifest.entries.length} duree=${manifest.duration_seconds}s frames=${manifest.total_frames} canvas=${manifest.canvas.width}x${manifest.canvas.height}`);
const first = manifest.entries[0];
if (first) {
  console.log(`  overlay: ${JSON.stringify(manifest.narrative?.overlay?.lines || [])}`);
  console.log(`  anti-detection[0]: mirror=${first.anti_detection.mirror} speed=${first.anti_detection.speed} crop=${first.anti_detection.crop_pct}%`);
}

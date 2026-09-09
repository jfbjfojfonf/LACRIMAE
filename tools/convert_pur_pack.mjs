#!/usr/bin/env node
/**
 * convert_pur_pack.mjs — CLI : pack PUR PERTURABO → pur_manifest.json (dev10.pur.v1)
 * Utilisé par .github/workflows/dev10_pur_render.yml et en local.
 *
 * Usage :
 *   node tools/convert_pur_pack.mjs --pack pack_pur_A01.json --out pur_manifest.json \
 *     [--canvas 9:16] [--clip clips/pur_A01.mp4] [--fps 30] [--style ranking]
 *
 * Règle opérateur (2026-09-09) : si le style du pack est inconnu (ni déclaré,
 * ni inférable) et que --style n'est pas fourni → CONVERSION REFUSÉE.
 * C'est TOI qui choisis le style, jamais le code en silence.
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const here = dirname(fileURLToPath(import.meta.url));

// Parse args
const args = process.argv.slice(2);
const get = (flag) => {
  const i = args.indexOf(flag);
  return i >= 0 ? args[i + 1] : undefined;
};
const packPath = get('--pack');
const outPath = get('--out');
const canvas = get('--canvas') || '9:16';
const clip = get('--clip') || '';
const fps = Number(get('--fps') || 30);

if (!packPath || !outPath) {
  console.error('usage: convert_pur_pack.mjs --pack <pack.json> --out <manifest.json> [--canvas 9:16] [--clip clips/x.mp4] [--fps 30]');
  process.exit(1);
}

// Import ES module du preview (chemin relatif au script)
const bridgeClipperUrl = new URL('../F03_PREVIEW/CODEBASE/src/preview/bridgeClipper.js', `file://${resolve(here)}/`);
const { parsePurPack } = await import(bridgeClipperUrl.href);

const styleArg = get('--style');
const pack = JSON.parse(readFileSync(resolve(packPath), 'utf-8'));

// Contrôle opérateur AVANT conversion : style déclaré ?
const declaredStyle = String(pack.montage_style || pack.montage_instructions?.metadata?.style || '').toLowerCase();
if (!declaredStyle && !styleArg) {
  console.error('✗ REFUSÉ : pack sans style déclaré (montage_style/metadata.style absent).');
  console.error('  → relance avec --style ranking|reframing|blur|split_scene (ton choix),');
  console.error('    ou regénère le pack côté PERTURABO avec --style (packs récents).');
  process.exit(2);
}

const manifest = parsePurPack(pack, { fps, canvas, clipFiles: clip ? [clip] : [], style: styleArg });

if (!manifest.entries.length) {
  console.error('✗ Pack PUR illisible (montage_instructions manquante ?)');
  process.exit(1);
}
if (manifest.style_unknown) {
  console.error(`✗ REFUSÉ : style « ${manifest.style_source} » non reconnu — BLOQUÉ par règle opérateur.`);
  process.exit(2);
}
console.log(`  style: ${manifest.style} (source: ${manifest.style_source})`);

writeFileSync(resolve(outPath), JSON.stringify(manifest, null, 2) + '\n');
console.log(`✓ ${manifest.schema_version} écrit : ${outPath}`);
console.log(`  pack=${manifest.pur.pack_id} angle=${manifest.pur.angle_id} durée=${manifest.duration_seconds}s frames=${manifest.total_frames} canvas=${manifest.canvas.width}x${manifest.canvas.height}`);
console.log(`  overlay: ${JSON.stringify(manifest.narrative.overlay.lines)}`);
console.log(`  anti-detection: mirror=${manifest.entries[0].anti_detection.mirror} speed=${manifest.entries[0].anti_detection.speed} crop=${manifest.entries[0].anti_detection.crop_pct}%`);

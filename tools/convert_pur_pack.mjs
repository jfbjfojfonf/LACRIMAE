#!/usr/bin/env node
/**
 * convert_pur_pack.mjs — CLI : pack(s) PUR PERTURABO → pur_manifest.json (dev10.pur.v1/v2)
 * Utilisé par .github/workflows/dev10_pur_render.yml et en local.
 *
 * Usage :
 *   node tools/convert_pur_pack.mjs --pack pack_pur_A01.json --out pur_manifest.json \
 *     [--canvas 9:16] [--clip clips/pur_A01.mp4] [--fps 30] [--style ranking]
 *
 * MULTI-VIDÉOS (2026-09-10) :
 *   node tools/convert_pur_pack.mjs --packs "EXPORT/pack_A01.json,EXPORT/pack_A02.json" \
 *     --out pur_manifest.json [--style blur] [--canvas 9:16]
 *   → 1 manifeste multi-entrées : 1 pack = 1 vidéo finale. Style + texte
 *     GLOBAUX (validés par l'opérateur) appliqués à toutes les vidéos.
 *   Réglages opérateur : --style-params <manifeste_ref.json> reprend les
 *   style_params + overlay éditorial d'un manifeste déjà validé (le codex).
 *
 * Règle opérateur (2026-09-09) : si le style du pack est inconnu (ni déclaré,
 * ni inférable) et que --style n'est pas fourni → CONVERSION REFUSÉE.
 * C'est TOI qui choisis le style, jamais le code en silence.
 */
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
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
const packsList = get('--packs'); // MULTI-VIDÉOS : liste séparée par des virgules
const outPath = get('--out');
const canvas = get('--canvas') || '9:16';
const clip = get('--clip') || '';
const fps = Number(get('--fps') || 30);
const refManifest = get('--style-params') || '';

if ((!packPath && !packsList) || !outPath) {
  console.error('usage: convert_pur_pack.mjs (--pack <pack.json> | --packs <p1.json,p2.json,…>) --out <manifest.json> [--canvas 9:16] [--clip clips/x.mp4] [--fps 30] [--style ranking] [--style-params ref_manifest.json]');
  process.exit(1);
}

// Import ES module du preview (chemin relatif au script)
const bridgeClipperUrl = new URL('../F03_PREVIEW/CODEBASE/src/preview/bridgeClipper.js', `file://${resolve(here)}/`);
const { parsePurPack, parsePurPackMulti } = await import(bridgeClipperUrl.href);

const styleArg = get('--style');

// Réglages opérateur depuis un manifeste de référence (le codex validé)
let refStyleParams;
let refOverlayParams;
if (refManifest) {
  try {
    const ref = JSON.parse(readFileSync(resolve(refManifest), 'utf-8'));
    refStyleParams = ref.style_params;
    refOverlayParams = ref.narrative?.overlay?.style_params;
    console.log(`  réglages opérateur repris de ${refManifest}`);
  } catch (err) {
    console.error(`✗ --style-params illisible : ${err.message}`);
    process.exit(1);
  }
}

const loadPack = (p) => JSON.parse(readFileSync(resolve(p), 'utf-8'));

// Contrôle opérateur AVANT conversion : style déclaré ?
const checkStyleDeclared = (pack, source) => {
  const declaredStyle = String(pack.montage_style || pack.montage_instructions?.metadata?.style || '').toLowerCase();
  if (!declaredStyle && !styleArg) {
    console.error(`✗ REFUSÉ : pack sans style déclaré (${source} : montage_style/metadata.style absent).`);
    console.error('  → relance avec --style ranking|reframing|blur|split_scene (ton choix),');
    console.error('    ou regénère le pack côté PERTURABO avec --style (packs récents).');
    process.exit(2);
  }
};

let manifest;
if (packsList) {
  // ── MULTI-VIDÉOS : 1 pack = 1 vidéo finale, style + texte globaux ──
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
  if (manifest.style_unknown) {
    console.error(`✗ REFUSÉ : style « ${manifest.style_source} » non reconnu — BLOQUÉ par règle opérateur.`);
    process.exit(2);
  }
  console.log(`  style GLOBAL: ${manifest.style} (source: ${manifest.style_source}) — appliqué à ${manifest.entries.length} vidéos`);
  for (const e of manifest.entries) {
    // Fix 2026-09-11 : la clé d'identité est source_id (angle_id n'existe pas
    // dans dev10.pur.v1) — le log affichait « ▸ undefined → … ».
    console.log(`  ▸ ${e.source_id || e.angle_id || e.pack_label} → ${e.clip_file} (${e.duration_seconds}s, zooms: ${e.zooms?.length || 0}, mirror: ${e.anti_detection?.mirror})`);
  }
} else {
  // ── MONO-VIDÉO (compatibilité) ──
  const pack = loadPack(packPath);
  checkStyleDeclared(pack, packPath);
  manifest = parsePurPack(pack, { fps, canvas, clipFiles: clip ? [clip] : [], style: styleArg, styleParams: refStyleParams, overlayParams: refOverlayParams });
  if (!manifest.entries.length) {
    console.error('✗ Pack PUR illisible (montage_instructions manquante ?)');
    process.exit(1);
  }
  if (manifest.style_unknown) {
    console.error(`✗ REFUSÉ : style « ${manifest.style_source} » non reconnu — BLOQUÉ par règle opérateur.`);
    process.exit(2);
  }
  console.log(`  style: ${manifest.style} (source: ${manifest.style_source})`);
}

// ── PORTES ASSETS (anti-404, calculées jamais déclarées) ──
// sfx_available : true seulement si chaque type de SFX du codex existe dans
// F03_PICTOR/CODEBASE/public/sfx/ — sinon rendu SANS SFX, jamais de crash 404.
// boom n'existe pas encore (fichier à fournir) → mapping boom→impact côté
// composition, journalisé le 2026-09-11.
const sfxDir = resolve('F03_PICTOR/CODEBASE/public/sfx');
const requiredSfx = [...new Set(manifest.entries
  .flatMap((e) => (e.sfx_list || []).map((s) => String(s.type || '')))
  .filter(Boolean))];
// boom n'existe pas encore (fichier à fournir) → mapping provisoire boom→impact
const missingSfx = [...new Set(requiredSfx.map((t) => (t === 'boom' ? 'impact' : t)))]
  .filter((t) => !existsSync(resolve(sfxDir, t + '.mp3')));
manifest.sfx_available = missingSfx.length === 0;
if (!manifest.sfx_available) {
  console.log('  ⚠ SFX absents du codebase de rendu : ' + missingSfx.join(', ') + ' → sfx_available=false (rendu sans SFX)');
} else if (requiredSfx.length) {
  console.log('  SFX disponibles : ' + requiredSfx.join(', '));
}
// Voix du clip ON — décision Warsmith 2026-09-11 (codex : « voix claire » hook).
manifest.clip_audio_available = true;

writeFileSync(resolve(outPath), JSON.stringify(manifest, null, 2) + '\n');
console.log(`✓ ${manifest.schema_version} écrit : ${outPath}`);
console.log(`  entrées=${manifest.entries.length} durée=${manifest.duration_seconds}s frames=${manifest.total_frames} canvas=${manifest.canvas.width}x${manifest.canvas.height}`);
const first = manifest.entries[0];
if (first) {
  console.log(`  overlay: ${JSON.stringify(manifest.narrative?.overlay?.lines || [])}`);
  console.log(`  anti-detection[0]: mirror=${first.anti_detection.mirror} speed=${first.anti_detection.speed} crop=${first.anti_detection.crop_pct}%`);
}

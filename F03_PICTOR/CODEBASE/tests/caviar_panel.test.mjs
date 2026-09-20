/* ═══════════════════════════════════════════════════════════════════
   Tests GROUPE 2 v2 — le panneau B-roll possédé par la partition F00D
   Exécution : node tests/caviar_panel.test.mjs (inclus dans npm run test:caviar)
   Emballage v2 : crop_zoom, blur_radius_px, panel vertical_text_overlay,
   cap 45 frames, élément unique, resolution_at, non-régression v1.
   ═══════════════════════════════════════════════════════════════════ */
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { test, runSuite } from './harness.mjs';

import {
  PANEL_MAX_FRAMES,
  PANEL_TYPES,
  normalizePanelType,
  resolvePanelSpec,
  panelVerticalTextOverlayStyle,
} from '../src/caviarPanel.js';
import {
  buildCaviarTimeline,
} from '../src/caviarRender.js';
import { normalizeCaviarPartition, packToCaviarBlock, toEngineBlock } from '../src/caviarV2.js';

const budget = JSON.parse(readFileSync(new URL('../src/data/caviar_budget.json', import.meta.url), 'utf8'));
const registry = JSON.parse(readFileSync(new URL('../src/data/caviar_registry.json', import.meta.url), 'utf8'));

let realPack = null;
try { realPack = JSON.parse(readFileSync(new URL('./pack_voxc2_blur_v2.json', import.meta.url), 'utf8')); } catch { /* skip */ }

/* ── resolvePanelSpec : l'emballage sort de la partition/registre ── */

test('spec : extra v2 → crop_zoom/blur/panel transportés', () => {
  const spec = resolvePanelSpec({
    numero: 'BLUR-01',
    file: 'broll/BLUR-01.mp4',
    extra: { broll_id: 'BLUR-01', crop_zoom: 1.3, blur_radius_px: 18, panel: 'vertical_text_overlay' },
  }, registry);
  assert.equal(spec.panel, 'vertical_text_overlay');
  assert.equal(spec.crop_zoom, 1.3);
  assert.equal(spec.blur_radius_px, 18);
  assert.equal(spec.broll_id, 'BLUR-01');
});

test("spec : repli registre sémantique si la partition omet l'emballage", () => {
  // Le registre ne porte pas crop_zoom → fallback doctrinal 1.3/18.
  const spec = resolvePanelSpec({ numero: 'BLUR-01', file: 'x.mp4', extra: { broll_id: 'BLUR-01' } }, registry);
  assert.ok(spec, 'entrée sémantique connue → panneau v2');
  assert.equal(spec.crop_zoom, 1.3);
  assert.equal(spec.blur_radius_px, 18);
  assert.equal(spec.panel, 'plain', 'pas de panel demandé → plain');
});

test('spec : broll v1 SANS emballage ni registre → null (rendu historique)', () => {
  assert.equal(resolvePanelSpec({ numero: 2, file: 'broll/broll_02.mp4' }, registry), null);
  assert.equal(resolvePanelSpec({ numero: '1', file: 'broll/broll_01.mp4' }, { clips: { 1: { file: 'broll/broll_01.mp4' } } }), null);
  assert.equal(resolvePanelSpec(null, registry), null);
});

test('spec : valeurs hors doctrine → plafonnées (crop ≤ 2, blur ≤ 60)', () => {
  const spec = resolvePanelSpec({
    extra: { broll_id: 'BLUR-01', crop_zoom: 3.5, blur_radius_px: 200, panel: 'chose_inconnue' },
  }, registry);
  assert.equal(spec.crop_zoom, 2.0);
  assert.equal(spec.blur_radius_px, 60);
  assert.equal(spec.panel, 'plain', 'type inconnu → plain, le rendu ne casse jamais');
});

test('doctrine : PANEL_MAX_FRAMES == budget.events.broll.max_frames == 45', () => {
  assert.equal(PANEL_MAX_FRAMES, 45);
  assert.equal(budget.events.broll.max_frames, 45);
  assert.ok(PANEL_TYPES.includes('vertical_text_overlay'));
});

/* ── Intégration moteur : le panneau traverse buildCaviarTimeline ── */

test('moteur : partition v2 → brolls portent panel_spec (emballage F00D)', () => {
  const block = normalizeCaviarPartition({
    bound: true,
    panels: [{ broll_id: 'BLUR-01', start_sec: 8, duration_frames: 36, crop_zoom: 1.3, blur_radius_px: 18, panel: 'vertical_text_overlay' }],
  }, registry);
  const t = buildCaviarTimeline(block, budget, { fps: 30, speed: 1, durationInFrames: 900, registry });
  assert.equal(t.brolls.length, 1);
  assert.equal(t.brolls[0].panel_spec.crop_zoom, 1.3);
  assert.equal(t.brolls[0].panel_spec.blur_radius_px, 18);
  assert.equal(t.brolls[0].panel_spec.panel, 'vertical_text_overlay');
  // Flash entrée-seule inchangé :
  assert.deepEqual(t.flashes.map((f) => f.frame), [t.brolls[0].frame]);
});

test('moteur : bloc v1 (broll numéroté) → panel_spec null, rendu historique', () => {
  const t = buildCaviarTimeline({
    enabled: true,
    brolls: [{ at_sec: 8, duration_frames: 30, numero: 2, file: 'broll/broll_02.mp4', sfx: 'impact' }],
  }, budget, { fps: 30, speed: 1, durationInFrames: 900, registry: null });
  assert.equal(t.brolls.length, 1);
  assert.equal(t.brolls[0].panel_spec, null);
});

test('moteur : panneau > 45 frames → tronqué au cap (dépôt tracé)', () => {
  const block = normalizeCaviarPartition({
    bound: true,
    panels: [{ broll_id: 'BLUR-01', start_sec: 5, duration_frames: 60 }],
  }, registry);
  const t = buildCaviarTimeline(block, budget, { fps: 30, speed: 1, durationInFrames: 900, registry });
  assert.equal(t.brolls[0].frames, 45, 'cap doctrinal appliqué');
  assert.ok(t.dropped.some((d) => String(d.reason).includes('tronquée')));
});

test('moteur : élément unique — punch-in pendant un panneau → déposé', () => {
  const block = {
    enabled: true,
    brolls: [{ at_sec: 8, duration_frames: 36, numero: 'BLUR-01', file: 'broll/BLUR-01.mp4', extra: { broll_id: 'BLUR-01', crop_zoom: 1.3, blur_radius_px: 18 } }],
    punchins: [
      { at_sec: 8.5, scale_to: 1.1 },   // DANS le panneau → déposé
      { at_sec: 15, scale_to: 1.08 },   // loin → conservé
    ],
  };
  const t = buildCaviarTimeline(block, budget, { fps: 30, speed: 1, durationInFrames: 900, registry });
  assert.equal(t.punchins.length, 1, 'seul le punch-in hors panneau survit');
  assert.equal(t.punchins[0].frame, 450);
  assert.ok(t.dropped.some((d) => String(d.reason).includes('élément unique')));
});

test('moteur : resolution_at — AUCUN événement après (dernier filet rendu)', () => {
  const block = {
    enabled: true,
    extra: { resolution_at: 20 },
    brolls: [{ at_sec: 8, duration_frames: 30, numero: 'BLUR-01', file: 'broll/BLUR-01.mp4' }],
    punchins: [{ at_sec: 12, scale_to: 1.08 }, { at_sec: 25, scale_to: 1.08 }],
    smash_audio: [{ at_sec: 30, duck_db: -12, duration_sec: 0.8 }],
  };
  const t = buildCaviarTimeline(block, budget, { fps: 30, speed: 1, durationInFrames: 1200, registry });
  assert.equal(t.punchins.length, 1, 'punch-in après résolution déposé');
  assert.equal(t.smash_audio.length, 0, 'smash après résolution déposé');
  assert.ok(t.dropped.filter((d) => String(d.reason).includes('resolution_at')).length >= 2);
  assert.equal(t.gate.resolution_at, 20);
  assert.equal(t.gate.resolution_violations, 0);
});

/* ── Habillage vertical_text_overlay ── */

test('habillage : styles du décor vertical (cadre + jauge, texte ≠ F00D)', () => {
  const s = panelVerticalTextOverlayStyle({ broll_id: 'BLUR-01', panel: 'vertical_text_overlay' });
  assert.ok(s.frame && s.rail && s.id === 'BLUR-01');
  assert.equal(s.frame.position, 'absolute');
  assert.ok(!('fontSize' in s.frame), 'F00D ne possède PAS le texte (F06 seul)');
});

/* ── Pack réel voxc-2 : les panneaux portent l'emballage de la note ── */

test('pack réel : BLUR-01/02 → crop_zoom 1.3, blur 18px, vertical_text_overlay', () => {
  if (!realPack) { console.log('  ↷ pack réel absent — sauté'); return; }
  const block = packToCaviarBlock(realPack, registry);
  const t = buildCaviarTimeline(block, budget, { fps: 30, speed: 1.05, durationInFrames: Math.round((51.301 / 1.05) * 30), registry });
  assert.equal(t.brolls.length, 2);
  for (const b of t.brolls) {
    assert.equal(b.panel_spec.crop_zoom, 1.3, 'note §4 : crop_zoom 1.3');
    assert.equal(b.panel_spec.blur_radius_px, 18, 'note §4 : blur 18px');
    assert.equal(b.panel_spec.panel, 'vertical_text_overlay');
    assert.ok(b.frames <= 45);
  }
  assert.ok(t.gate.ok, `budget ok — dépense ${t.gate.spend_units}u`);
});

/* ── Assets réels (rendu vrai) : sautés tant que les MP4 sont absents ── */

test('rendu réel : BLUR-01/02 présents dans public/ (sinon sauté)', () => {
  const pub = new URL('../public/', import.meta.url).pathname;
  const ok = existsSync(`${pub}broll/BLUR-01.mp4`) && existsSync(`${pub}broll/BLUR-02.mp4`);
  if (!ok) { console.log('  ↷ MP4 BLUR-01/02 absents de public/broll/ — rendu réel sauté (dépose propre au rendu)'); return; }
  const sfxOk = existsSync(`${pub}sfx/impact.mp3`);
  assert.ok(sfxOk, 'sfx/impact.mp3 présent (SFX couplé entrée)');
});

runSuite();

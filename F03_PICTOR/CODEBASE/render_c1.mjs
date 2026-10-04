import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { packToCaviarBlock } from './src/caviarV2.js';
import { buildCaviarTimeline } from './src/caviarRender.js';

const root = fileURLToPath(new URL('.', import.meta.url));
const pack = JSON.parse(readFileSync(root + 'tests/pack_asf_c1.json', 'utf8'));
const budget = JSON.parse(readFileSync(root + 'src/data/caviar_budget.json', 'utf8'));
const registry = JSON.parse(readFileSync(root + 'src/data/caviar_registry.json', 'utf8'));

const block = packToCaviarBlock(pack, registry);
console.log('=== BLOCK ===');
console.log(JSON.stringify(block, null, 2));
const t = buildCaviarTimeline(block, budget, { fps: 30, speed: 1, durationInFrames: 1800 });
console.log('=== TIMELINE ===');
console.log(JSON.stringify(t, null, 2));

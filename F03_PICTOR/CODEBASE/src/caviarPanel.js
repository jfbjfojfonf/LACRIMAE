/* ═══════════════════════════════════════════════════════════════════
   caviarPanel.js — GROUPE 2 v2 : le panneau B-roll possédé par la
   partition F00D (note technique PERTURABO 2026-09-15, §3.3/§3.5/§3.6).

   En v2, F00D ne demande pas seulement UN B-roll : il possède
   l'EMBALLAGE du panneau —
     - crop_zoom     : zoom de recadrage demandé (ex. 1.3) ;
     - blur_radius_px: rayon de flou du panneau (ex. 18 px) — style blur ;
     - panel         : type d'habillage ('vertical_text_overlay', …).

   Règles verrouillées (note §3.5) : flash à l'ENTRÉE uniquement, SFX
   uniquement à l'entrée (couplé même frame), élément unique (jamais 2
   événements visuels forts sur la même frame), aucun événement après
   resolution_at, trio = pacing local raccourci. La vérification vit dans
   caviarRender.js (rendu, dernier filet) et caviar_gate.py (pack) —
   ce module ne porte QUE la résolution et l'habillage.

   Zéro dépendance Remotion/React : fonctions pures (npm run test:caviar).
   ═══════════════════════════════════════════════════════════════════ */

/** Plafond doctrinal : durée d'un panneau ≤ max_frames du budget (45).
 *  Source de vérité : caviar_budget.json events.broll.max_frames —
 *  ce miroir sert aux tests de cohérence. */
export const PANEL_MAX_FRAMES = 45;

/** Types d'habillage de panneau connus (extensible côté bras armé).
 *  F00D commande ; si le type est inconnu → 'plain' (B-roll brut) et
 *  le rendu ne casse jamais. */
export const PANEL_TYPES = ['vertical_text_overlay', 'plain'];

/** Habillage par défaut si le type demandé est absent/inconnu. */
export function normalizePanelType(panel) {
  const p = String(panel || '').trim();
  return PANEL_TYPES.includes(p) ? p : 'plain';
}

/** Résout l'EMBALLAGE d'un panneau depuis un broll du moteur (v2).
 *  Les valeurs sortent de `extra` (transporté par caviarV2.js) ; repli
 *  sur le registre sémantique si la partition ne les précise pas ;
 *  replis finaux doctrinaux : crop_zoom 1.3, blur 18 px, panel 'plain'.
 *  Retourne null si pas un panneau v2 (broll v1 sans emballage ni entrée
 *  sémantique) → la composition garde le rendu plein cadre historique. */
export function resolvePanelSpec(broll, registry = null) {
  const b = broll && typeof broll === 'object' ? broll : {};
  const extra = b.extra && typeof b.extra === 'object' ? b.extra : {};
  const id = String(extra.broll_id || b.numero || '').trim();
  const sem = registry && registry.semantic && typeof registry.semantic === 'object' ? registry.semantic : null;
  const reg = sem ? (sem[id] || sem[id.toUpperCase()] || sem[id.toLowerCase()] || null) : null;

  const cropZoom = Number(extra.crop_zoom ?? reg?.crop_zoom ?? 0);
  const blurPx = Number(extra.blur_radius_px ?? reg?.blur_radius_px ?? 0);
  const panelType = extra.panel ?? reg?.panel ?? undefined;
  const isV2 = cropZoom > 1 || blurPx > 0 || Boolean(panelType) || Boolean(reg);

  if (!isV2) return null;
  return {
    broll_id: extra.broll_id ?? b.numero ?? null,
    panel: normalizePanelType(panelType),
    crop_zoom: Math.min(2.0, Math.max(1.0, cropZoom > 1 ? cropZoom : 1.3)),
    blur_radius_px: Math.min(60, Math.max(0, blurPx > 0 ? blurPx : 18)),
  };
}

/** Habillage 'vertical_text_overlay' : cadre vertical sombre + jauge
 *  latérale (esthétique panneau vertical, 9:16 friendly).
 *  Retourne les styles pour la composition (décor SEUL — le texte
 *  éditorial reste possédé par F06, jamais par F00D). */
export function panelVerticalTextOverlayStyle(spec) {
  const s = spec && typeof spec === 'object' ? spec : {};
  return {
    frame: {
      position: 'absolute',
      inset: '7% 4%',
      borderRadius: 14,
      border: '2px solid rgba(255,255,255,0.22)',
      background: 'linear-gradient(180deg, rgba(0,0,0,0.42) 0%, rgba(0,0,0,0.14) 45%, rgba(0,0,0,0.5) 100%)',
      boxShadow: 'inset 0 0 60px rgba(0,0,0,0.55)',
      pointerEvents: 'none',
    },
    rail: {
      position: 'absolute',
      left: '5.5%',
      top: '10%',
      bottom: '10%',
      width: 4,
      borderRadius: 2,
      background: 'linear-gradient(180deg, rgba(255,255,255,0.85) 0%, rgba(255,255,255,0.25) 100%)',
      pointerEvents: 'none',
    },
    id: String(s.broll_id || ''),
  };
}

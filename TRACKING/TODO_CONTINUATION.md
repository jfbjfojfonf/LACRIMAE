# LACRIMAE dev6-F — TODO DE CONTINUATION

> Point d'entree obligatoire apres toute reprise.
> Branche : `dev6-F` sur `jfbjfojfonf/LACRIMAE`.
> Source : copie de `dev6-E` @ `24a719d`, pivot LUT.

## Mission

Prendre un 3D LUT (`.cube`), l'appliquer sur N videos, declenchement
GitHub Actions, execution Modal. Puis F05/F06 (copie `dev10-v2`).

## Doctrine figee

1. Deux fregates maintenant : `F01_INGEST`, `F02_RENDER`. Noms **intouchables**.
2. Modal + GitHub Actions = pile **dans** ces deux fregates, pas des fregates.
3. F02 applique `ffmpeg lut3d`, plus Nexrender / AE / VPS.
4. F05_CAMOUFLAGE + F06_LUTHER = copie verbatim `dev10-v2`, plus tard.
5. LUT != clone de `cc2.ffx`. Look pack YouTube, pas glow Sapphire.

## Phases

| Phase | Contenu | Statut |
|---|---|---|
| P0 | Docs + arbre CODEBASE/IN/OUT | ⬜ |
| P1 | Copie F05/F06 depuis `dev10-v2` | ⬜ |
| P2 | Code F01 + F02 LUT, tests, purge Nexrender | ⬜ |
| P3 | Modal app + workflow Actions | ⬜ bloque humain |
| P4 | Cablage F02 OUT → F05 → F06 | ⬜ |

## Contrats

- Manifeste F01→F02 : `id`, `video_path` (schema herite E).
- Gabarit fregate : `CODEBASE/` `IN/` `OUT/` `tests/` (comme `dev10-v2`).
- `.cube` dans `SHARED/IN/` — jamais commite.

## Interdits

- Ranking / Remotion / PICTOR / Heisenberg / SIGNUM.
- Rename F01 / F02.
- GPU Modal pour lut3d (CPU).
- Commit `.cube` / `.mp4` / token.

## Prochaine etape exacte

P0 puis P1 puis P2 (agent). P3 des que l'humain a un `.cube` et `MODAL_TOKEN`.

## Reprise sandbox

```
git clone https://github.com/jfbjfojfonf/LACRIMAE.git
cd LACRIMAE
git fetch origin --prune
git checkout dev6-F
```

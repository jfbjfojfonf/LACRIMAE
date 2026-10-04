# 03 — Format du job de rendu (JSON)

> **Statut : spécification uniquement.** Le fichier JSON de référence sera écrit en
> **Phase 1**, après validation de ce document. Rien n'est encore codé.

## Rôle

Un job Nexrender décrit **un rendu** : quel template, quelle vidéo, quels remplacements,
quel encodage. F02_RENDER génère un job par vidéo (ou par lot) et le soumet au
`nexrender-server` du VPS.

## Structure attendue

| Champ | Type | Rôle |
|---|---|---|
| `template` | string | chemin du `.aep` sur le VPS (ex. `C:\nexrender\templates\template.aep`) |
| `assets` | array | liste des éléments à remplacer dans le template |
| `assets[].type` | string | `video` (la vidéo source) + `script` (le JSX du preset) |
| `assets[].layerName` | string | nom du calque cible dans le `.aep` (ex. `SRC`) |
| `assets[].src` | string | chemin/URL de la vidéo à traiter |
| `output` | object | encodage de la sortie (format, débit, résolution) |
| `frameStart` / `frameEnd` | number | plage de frames (optionnel, pour tests courts) |

## Exemple illustratif (à valider, pas encore écrit comme fichier)

```json
{
  "template": "C:\\nexrender\\templates\\template.aep",
  "assets": [
    {
      "type": "video",
      "layerName": "SRC",
      "src": "C:\\nexrender\\inbox\\video_test.mp4"
    },
    {
      "type": "script",
      "src": "C:\\nexrender\\scripts\\apply_cc2.jsx"
    }
  ],
  "output": {
    "format": "mp4",
    "codec": "h264"
  }
}
```

## Décisions à valider avant Phase 1

1. **Format de sortie** : mp4 H.264 ? master AVI/QuickTime ? quel débit ?
2. **Résolution/fps** : identiques à la source (1920×1080, 120 fps) ou conformés ?
3. **Batch** : un job par vidéo, ou un job multi-vidéos ?

## Où ça vit

- Les jobs réels : `NEXRENDER/jobs/` dans le repo (pas de secret dedans).
- Les vidéos source/restées privées : jamais dans le repo (`*.mp4` ignoré),
  elles vont directement dans `C:\nexrender\inbox\` sur le VPS.

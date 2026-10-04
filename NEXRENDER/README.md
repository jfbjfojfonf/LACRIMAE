# NEXRENDER — flux de rendu `dev6-E`

## Le principe

On ne réinvente rien : on prend **des vidéos déjà créées**, on les envoie à **Nexrender**
(orchestrateur open-source d'After Effects), qui applique **notre preset `cc2.ffx`** sur le
VPS Kamatera — et basta.

```
F01_INGEST ──► F02_RENDER ──► [VPS: nexrender-server → aerender + cc2.ffx] ──► vidéo finie
```

- **Nexrender** = chef d'orchestre. Il ne rend pas lui-même : il pilote `aerender`
  (After Effects en mode ligne de commande, sans interface).
- **Le VPS** (Windows Server 2025, 6 vCPU, 64 Go RAM) fait tout le travail.
  Le PC local ne sert qu'à envoyer les commandes.
- **Pas de version crackée** : pop-ups invisibles qui figent les rendus en arrière-plan,
  risque malware + bannissement Kamatera. On utilise le mode Render Only officiel d'Adobe.

## Pourquoi une machine personnelle plutôt que Nexrender Cloud

| | Nexrender Cloud (SaaS) | Notre VPS (open-source) |
|---|---|---|
| Coût | 99 €/mois + 0,18 €/min | crédit essai 100 $ / 30 jours (gratuit si on coupe le VPS) |
| Plugins tiers (Magic Bullet, Sapphire) | seulement sur nœuds dédiés / Enterprise | **on installe ce qu'on veut** |
| Scripts JSX | pré-approbation requise | **libre** |
| Contrôle | limité | total |

## Documentation

| Doc | Contenu |
|---|---|
| [`docs/01_VPS_SETUP.md`](docs/01_VPS_SETUP.md) | Installer Node, Nexrender, AE, plugins sur le VPS |
| [`docs/02_TEMPLATE_AEP.md`](docs/02_TEMPLATE_AEP.md) | Créer le template `.aep` **sur le VPS** (via RDP) |
| [`docs/03_JOB.md`](docs/03_JOB.md) | Format du JSON de job de rendu |
| [`docs/04_SCRIPT_JSX.md`](docs/04_SCRIPT_JSX.md) | Spécification du script qui applique `cc2.ffx` |
| [`docs/05_DEPANNAGE.md`](docs/05_DEPANNAGE.md) | Erreurs fréquentes et solutions |

## Dossiers

- `jobs/` — les JSON de job de rendu (un fichier par lot de vidéos)
- `scripts/` — le JSX d'application du preset
- `templates/` — **vide dans le repo, par design** : le `.aep` vit uniquement sur le VPS
  (binaire privé, jamais committé)

## Règles absolues

1. `*.ffx` et `*.aep` ne quittent jamais le VPS / le poste local — jamais dans le repo.
2. Tout code est écrit **après validation** de la phase correspondante (cf. `CONTINUATION.md`).
3. La branche ne contient que le flux Nexrender : pas de Polyester, pas de pipeline OpenCV.

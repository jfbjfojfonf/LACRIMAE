# 01 — Installation du VPS Kamatera (check-list)

> **À faire par toi**, connexion RDP (Bureau à distance) depuis ton PC.
> Machine : Windows Server 2025, 6 vCPU, 64 Go RAM, 200 Go SSD — essai 30 jours / 100 $.

## 1. Économie du crédit d'essai (règle n°1)

- Kamatera facture **à la minute** (~0,34 $/h pour cette config).
- **Éteindre le VPS (Power Off)** depuis le tableau de bord dès qu'on ne rend plus.
- Un serveur éteint ne coûte que le stockage (~10 $/mois).
- Calcul : 100 vidéos × ~5 min = ~8 h de serveur ≈ 2,7 $ → largement couvert par 100 $.

## 2. Outils à installer (dans l'ordre)

### a) Node.js (LTS)
- Télécharger le installateur officiel (nodejs.org), version **LTS**.
- Vérifier dans PowerShell : `node -v` et `npm -v`.

### b) Nexrender (open-source, github.com/inlife/nexrender)
```powershell
npm install -g @nexrender/cli
```
- Puis lancer le `nexrender-server` (écoute les jobs) et le `nexrender-worker`
  (exécute les rendus) — commandes exactes fournies en Phase 1 (cf. `03_JOB.md`).

### c) After Effects (version OFFICIELLE uniquement)
- Installer **Adobe Creative Cloud** sur le VPS, puis After Effects.
- **Jamais de version crackée** :
  - les pop-ups de crack sont invisibles en mode arrière-plan → `aerender` bloque
    jusqu'au timeout, tous les rendus échouent ;
  - risque de malware (serveur exposé 24 h/24 avec IP publique) ;
  - Kamatera peut bannir le compte pour activité suspecte.
- **Mode Render Only** : Adobe autorise les nœuds de rendu pilotés en ligne de commande
  sans interface. C'est ce mode qu'on utilise — c'est gratuit et prévu par Adobe.
  Tant qu'on n'ouvre pas l'interface graphique pour du montage, pas d'abonnement
  actif requis sur cette machine.

### d) Plugins du preset `cc2.ffx`
- D'après l'analyse du preset : **Magic Bullet Looks** et **S_Gradient (Sapphire)**.
- Installer les licences correspondantes sur le VPS (c'est LE grand avantage du
  self-hosted : sur Nexrender Cloud, les plugins tiers sont réservés aux nœuds dédiés).
- **Pas de plugins crackés** non plus : vérifications de licence qui popupent en
  arrière-plan, filigranes possibles sur les rendus, risque de bannissement.

## 3. Sécurité de base du VPS

- Mot de passe RDP fort.
- Ne pas laisser le VPS ouvert inutilement (crédit + exposition).
- Aucun fichier `.env`, token ou preset n'est stocké sur le VPS sans copie chiffrée.

## 4. Validation de la phase

- [ ] `node -v` / `npm -v` OK
- [ ] `nexrender` installé (version affichée)
- [ ] AE lançable en RDP, projet vide ouvrable
- [ ] `aerender` répond (test en ligne de commande, cf. `05_DEPANNAGE.md`)
- [ ] Magic Bullet Looks + Sapphire visibles dans AE
- [ ] Power Off / Power On du VPS maîtrisé depuis le tableau de bord

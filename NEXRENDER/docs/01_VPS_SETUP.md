# 01 — Installation du VPS Kamatera (check-list)

> **A faire par toi**, connexion RDP. Feuille complete : `ROADMAP_HUMAIN.md`.
> Machine : Windows Server 2025, 6 vCPU, 64 Go RAM — essai 30 jours / 100 $.

## 1. Credit

- Facturation a la minute (~0,34 $/h).
- **Power Off** des que tu ne rends plus. Eteint = stockage seulement.

## 2. Installer (ordre)

Node LTS, Python 3.12, FFmpeg (`ffprobe`), Git, puis :

```
npm install -g @nexrender/server @nexrender/worker @nexrender/action-copy @nexrender/action-encode
```

Secret (jamais Git) :

```
setx NEXRENDER_SECRET "ton-secret-local"
```

After Effects officiel + Magic Bullet Looks + Sapphire. Ouvrir AE une fois, fermer toutes les pop-ups.

aerender (adapter l'annee) :

```
& "C:\Program Files\Adobe\Adobe After Effects 2025\Support Files\aerender.exe" -help
```

## 3. Dossiers et process

Depuis le clone `dev6-E` :

```
powershell -ExecutionPolicy Bypass -File NEXRENDER\vps\bootstrap.ps1
powershell -ExecutionPolicy Bypass -File NEXRENDER\vps\start-nexrender.ps1
```

- server : `http://127.0.0.1:3000`
- API jobs : `POST /api/v1/jobs` header `nexrender-secret`
- worker : `aerender` + `C:\nexrender\work`

## 4. Validation

- [ ] `node -v` / `python --version` / `ffprobe -version`
- [ ] `nexrender-server` / `nexrender-worker` dans PATH
- [ ] AE + aerender + plugins visibles
- [ ] `C:\nexrender\scripts\apply_cc2.jsx` present
- [ ] Power Off / Power On maitrise

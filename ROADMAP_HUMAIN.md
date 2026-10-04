# Feuille de route — ta partie (VPS Kamatera)

Branche `dev6-E`. Le code est pret. Toi = machine + After Effects. Agent = scripts + jobs.

**Regle credit** : Power Off le VPS des que tu ne rends plus. Facturation a la minute.

---

## Etape 0 — Avant tout

- [ ] RDP vers le VPS (Windows Server).
- [ ] Mot de passe RDP fort.
- [ ] Tableau de bord Kamatera ouvert (Power Off / Power On).

---

## Etape 1 — Outils de base

Dans PowerShell **en Administrateur** :

```
winget install -e --id OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements
winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
winget install -e --id Gyan.FFmpeg --accept-package-agreements --accept-source-agreements
winget install -e --id Git.Git --accept-package-agreements --accept-source-agreements
```

Ferme et rouvre PowerShell, puis :

```
node -v
npm -v
python --version
ffprobe -version
git --version
```

Tout doit repondre. Si `winget` n'existe pas : installe depuis les sites officiels (nodejs.org LTS, python.org, ffmpeg, git-scm).

---

## Etape 2 — Nexrender

```
npm install -g @nexrender/server @nexrender/worker @nexrender/action-copy @nexrender/action-encode
```

Choisis un secret local (ne le mets **jamais** dans Git) :

```
setx NEXRENDER_SECRET "ton-secret-local"
```

Ferme / rouvre PowerShell pour que la variable existe.

---

## Etape 3 — After Effects officiel

1. Installe **Adobe Creative Cloud** puis **After Effects** (version officielle seulement).
2. Ouvre AE **une fois** en RDP, ferme toutes les pop-ups de bienvenue / licence / maj.
3. Verifie `aerender` :

```
& "C:\Program Files\Adobe\Adobe After Effects 2025\Support Files\aerender.exe" -help
```

Si le chemin est 2024 ou 2023, adapte. Le script `start-nexrender.ps1` teste 2025/2024/2023.

**Jamais de crack** : pop-up invisible = rendu bloque.

---

## Etape 4 — Plugins du preset `cc2.ffx`

Installe et licence sur le VPS :

- Magic Bullet Looks
- Sapphire (`S_Gradient`)

Ouvre AE, verifie qu'ils apparaissent dans Effets. Pas de watermark.

---

## Etape 5 — Clone du repo + dossiers

```
cd C:\
git clone --branch dev6-E --single-branch https://github.com/jfbjfojfonf/LACRIMAE.git
cd C:\LACRIMAE
powershell -ExecutionPolicy Bypass -File NEXRENDER\vps\bootstrap.ps1
```

Ca cree :

```
C:\nexrender\sources
C:\nexrender\inbox
C:\nexrender\outbox
C:\nexrender\queue
C:\nexrender\scripts
C:\nexrender\presets
C:\nexrender\templates
C:\nexrender\work
```

et copie `apply_cc2.jsx` dans `C:\nexrender\scripts\`.

---

## Etape 6 — Fichiers prives (hors Git)

A copier **a la main** (USB / scp / RDP glisser-deposer) :

| Fichier | Destination |
|---|---|
| `cc2.ffx` | `C:\nexrender\presets\cc2.ffx` |
| (plus tard) `template.aep` | `C:\nexrender\templates\template.aep` |

Verifier :

```
dir C:\nexrender\presets\cc2.ffx
dir C:\nexrender\scripts\apply_cc2.jsx
```

---

## Etape 7 — Template After Effects (sur le VPS, en RDP)

Ouvre AE. Cree **un** projet :

1. Composition nommee exactement `MAIN`
2. 1920 x 1080, fps = tes sources
3. Duree >= ta plus longue video
4. Importe une video placeholder, pose-la, **renomme le calque `SRC`**
5. N'applique **pas** `cc2.ffx` (le JSX le fera)
6. Render Queue : ajoute `MAIN`, Output Module **H.264** (AE 2023+ : obligatoire)
7. Fais **un rendu manuel** : doit produire un mp4
8. Enregistre : `C:\nexrender\templates\template.aep`

Check : calque = `SRC`, comp = `MAIN`, Output Module configure.

---

## Etape 8 — Demarrer Nexrender

```
cd C:\LACRIMAE
powershell -ExecutionPolicy Bypass -File NEXRENDER\vps\start-nexrender.ps1
```

Deux fenetres minimisées : server (port 3000) + worker. Laisse-les ouvertes.

Test :

```
curl http://127.0.0.1:3000/api/v1/jobs
```

---

## Etape 9 — Premier rendu (1 video)

1. Copie **une** video 1920x1080 mp4 dans `C:\nexrender\sources\`
2. Dry-run (pas d'AE) :

```
cd C:\LACRIMAE
python pipeline.py --dry-run
```

3. Rendu reel :

```
python pipeline.py
```

Sortie attendue : `C:\nexrender\outbox\<id>.mp4`

Si ca coince : `NEXRENDER\docs\05_DEPANNAGE.md` (pop-up, Output Module, plugin Missing, asset not found).

---

## Etape 10 — Couper le credit

Quand tu as le mp4 (ou que tu t'arretes) :

1. Ferme server / worker
2. **Power Off** le VPS dans Kamatera (pas juste RDP disconnect)

---

## Ce que tu n'as PAS a faire

- Ecrire du Python / JSON / JSX
- Toucher `dev6`, `dev6-D`, `f09-output`, `main`
- Committer `.ffx`, `.aep`, `.mp4`, tokens

## Quand revenir vers un agent

Envoie : capture d'erreur Nexrender / aerender, et dis si Etape 7 (template) est faite.
Le code attend Phase 4 (premier rendu reel).

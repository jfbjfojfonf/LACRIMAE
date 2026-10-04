# Intégration flottes sœurs — `dev-11`

`dev-11` n'ingère pas YouTube. L'appelant pousse des clips **déjà 9:16**.

---

## `dev10` PUR

Après FORMAT / F00-E, copies des stems retenus :

```
<flotte>/OUT/clips/<stem>.mp4  →  F01_OCULUS/IN/clips/<stem>.mp4
```

Puis `job_request.json` (`target: face` défaut). Interdit : importer PICTOR / VISIO ici.

Retour :

```
F03_CALIX/OUT/tracked/<stem>.mp4  →  IN Preview / Signum de la flotte appelante
```

Agrégation stricte : un stem HOLD OCULUS n'entre pas dans PUR zip.

---

## `dev9` ranking / `dev8` reveal

Même contrat fichiers. Ranking **après** Calix si le score dépend du visage collé. Reveal ne relance pas F01.

---

## Interdit

- Cloner le code PICTOR dans `dev-11`
- Lire `F0N_*/OUT` d'une autre branche depuis un moteur
- Decoder la campagne sur un runner GHA

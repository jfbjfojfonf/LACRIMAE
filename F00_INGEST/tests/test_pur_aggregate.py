# Tests pur_aggregate (unitaires, sans réseau, sans ffprobe requis)
# Run: pytest -q F00_INGEST/tests/test_pur_aggregate.py
import importlib.util
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "tools"))
import pur_aggregate  # noqa: E402


# ── Fix 2026-09-11 (run 34575463702) : identifiants déjà préfixés ──

def test_normalize_angle_retire_le_prefixe_pur():
    assert pur_aggregate.normalize_angle("pur_A01") == "A01"
    assert pur_aggregate.normalize_angle("PUR_A02") == "A02"
    assert pur_aggregate.normalize_angle("A01") == "A01"


def test_normalize_angle_cas_limites():
    assert pur_aggregate.normalize_angle("pur") == "pur"          # trop court : on ne touche pas
    assert pur_aggregate.normalize_angle("pur_") == "pur_"        # suffixe vide : on ne touche pas
    assert pur_aggregate.normalize_angle(None) == "?"             # entrée absente
    assert pur_aggregate.normalize_angle(7) == "7"                # rank numérique


def test_find_result_pur_A01_finale_est_trouve_avec_source_id_prefixe(tmp_path):
    # Scénario exact du run 34575463702 : fichier pur_A01_finale.mp4,
    # manifeste avec source_id 'pur_A01' → doit être trouvé après normalisation.
    mp4 = tmp_path / "pur_A01_finale.mp4"
    mp4.write_bytes(b"x" * 2048)
    found = pur_aggregate.find_result(tmp_path, pur_aggregate.normalize_angle("pur_A01"))
    assert found == mp4


def test_main_refuse_fichier_trop_petit(tmp_path, monkeypatch):
    # find_result ne filtre pas la taille : c'est main() qui refuse < 1024 octets
    # (copie interrompue → rendu vide, cf. bug du 2026-09-10 côté F00).
    monkeypatch.setattr(pur_aggregate, "probe", lambda p: {"codec": "h264"})
    code, report = _aggregate(
        tmp_path,
        [{"source_id": "pur_A01"}],
        {"pur_A01_finale.mp4": 100},
    )
    assert code == 1
    assert report["missing"] == ["A01"]
    assert report["results"][0]["status"] == "MISSING"


def test_find_result_dossier_absent(tmp_path):
    assert pur_aggregate.find_result(tmp_path / "inexistant", "A01") is None


def _aggregate(tmp_path, entries, files):
    """Lance main() avec un manifeste minimal ; retourne le code de sortie."""
    results = tmp_path / "results"
    results.mkdir(exist_ok=True)
    for name, size in files.items():
        (results / name).write_bytes(b"x" * size)
    manifest = tmp_path / "pur_manifest.json"
    manifest.write_text(json.dumps({"schema_version": "dev10.pur.v1", "entries": entries}), encoding="utf-8")
    out = tmp_path / "out"
    sys.argv = ["pur_aggregate.py", "--manifest", str(manifest),
                "--results", str(results), "--out", str(out)]
    code = pur_aggregate.main()
    report = json.loads((out / "pur_aggregate_report.json").read_text(encoding="utf-8"))
    return code, report


def test_main_bundle_complet_source_id_prefixe(tmp_path, monkeypatch):
    # Manifeste réel du run : source_id 'pur_A01' + fichier pur_A01_finale.mp4
    # ffprobe est mocké : l'agrégateur doit trouver le MP4 malgré le préfixe.
    monkeypatch.setattr(pur_aggregate, "probe",
                        lambda p: {"codec": "h264", "width": 1080, "height": 1920, "duration_seconds": 30.0})
    code, report = _aggregate(
        tmp_path,
        [{"source_id": "pur_A01", "duration_seconds": 30, "clip_file": "clips/pur_A01.mp4"}],
        {"pur_A01_finale.mp4": 2487479},
    )
    assert code == 0
    assert report["complete"] is True and report["missing"] == []
    assert report["rendered_count"] == 1
    assert report["results"][0]["angle_id"] == "A01"     # normalisé dans le rapport
    assert report["results"][0]["file"] == "pur_A01_finale.mp4"


def test_main_bundle_incomplet_refus(tmp_path, monkeypatch):
    # Doctrine préservée : un rendu manquant → code 1, RIEN n'est publié.
    monkeypatch.setattr(pur_aggregate, "probe",
                        lambda p: {"codec": "h264", "width": 1080, "height": 1920, "duration_seconds": 30.0})
    code, report = _aggregate(
        tmp_path,
        [{"source_id": "pur_A01"}, {"source_id": "pur_A02"}],
        {"pur_A01_finale.mp4": 2487479},
    )
    assert code == 1
    assert report["complete"] is False and report["missing"] == ["A02"]
    assert not (tmp_path / "out" / "pur_manifest.json").exists()   # pas de bundle publié

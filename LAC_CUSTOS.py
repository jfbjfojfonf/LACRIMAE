#!/usr/bin/env python3
"""Gardien LACRIMAE dev-11. Les portes sont dans TRACKING/DEV11_GATES.md."""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path
from typing import Any

ROOT_DEFAULT = Path(__file__).resolve().parent
STEM_RE = re.compile(r"^[a-zA-Z0-9._-]+$")
TARGETS = frozenset({"face", "nose", "eyes"})
FRIGATES = {
    "F01": "F01_OCULUS",
    "F01_OCULUS": "F01_OCULUS",
    "OCULUS": "F01_OCULUS",
    "F02": "F02_SANGUINOR",
    "F02_SANGUINOR": "F02_SANGUINOR",
    "SANGUINOR": "F02_SANGUINOR",
    "F03": "F03_CALIX",
    "F03_CALIX": "F03_CALIX",
    "CALIX": "F03_CALIX",
}
SISTER_OUT = {
    "F01_OCULUS": ("F02_SANGUINOR/OUT", "F03_CALIX/OUT"),
    "F02_SANGUINOR": ("F01_OCULUS/OUT", "F03_CALIX/OUT"),
    "F03_CALIX": ("F01_OCULUS/OUT", "F02_SANGUINOR/OUT"),
}


class Verdict:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.holds: list[str] = []
        self.held_stems: list[str] = []
        self.ambers: list[str] = []

    def rouge(self, gate: str, msg: str) -> None:
        self.errors.append(f"{gate}: {msg}")

    def hold(self, gate: str, msg: str, stem: str | None = None) -> None:
        self.holds.append(f"{gate}: {msg}")
        if stem and stem not in self.held_stems:
            self.held_stems.append(stem)

    def ambre(self, gate: str, msg: str) -> None:
        self.ambers.append(f"{gate}: {msg}")

    @property
    def refused(self) -> bool:
        return bool(self.errors)

    def dump(self, stream: Any) -> None:
        for line in self.errors:
            print(f"REFUS {line}", file=stream)
        for line in self.holds:
            print(f"HOLD  {line}", file=stream)
        for line in self.ambers:
            print(f"AMBRE {line}", file=stream)
        if self.refused:
            print("VERDICT REFUS", file=stream)
        elif self.holds:
            print("VERDICT PASS (HOLD stems)", file=stream)
        else:
            print("VERDICT PASS", file=stream)


def load_json(path: Path, v: Verdict, gate: str) -> Any | None:
    if not path.is_file():
        v.rouge(gate, f"absent: {path}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        v.rouge(gate, f"JSON invalide {path}: {exc}")
        return None


def load_config(root: Path) -> dict[str, Any]:
    path = root / "CONFIG" / "camera_defaults.json"
    if not path.is_file():
        return {
            "detected_ratio_min": 0.85,
            "gap_amber_frames": 12,
            "jitter_median_norm_max": 0.02,
            "deadzone_norm": 0.04,
            "zoom_min": 1.0,
        }
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_frigate(name: str) -> str:
    key = name.strip()
    if key not in FRIGATES:
        raise SystemExit(f"frigate inconnue: {name}")
    return FRIGATES[key]


def list_mp4(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return sorted(p for p in folder.iterdir() if p.suffix.lower() == ".mp4")


def list_json(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return sorted(p for p in folder.iterdir() if p.suffix.lower() == ".json")


def stem_of(path: Path) -> str:
    return path.stem


def check_stems(stems: list[str], v: Verdict, gate: str) -> None:
    seen: set[str] = set()
    for stem in stems:
        if not STEM_RE.match(stem):
            v.rouge(gate, f"stem charset illegal: {stem}")
        if stem in seen:
            v.rouge(gate, f"stem duplique: {stem}")
        seen.add(stem)


def is_norm(value: Any) -> bool:
    return isinstance(value, (int, float)) and 0.0 <= float(value) <= 1.0


def validate_job_request(data: Any, v: Verdict) -> None:
    if not isinstance(data, dict):
        v.rouge("P-OC-0", "job_request n'est pas un objet")
        return
    if data.get("schema") != "dev11.job_request.v1":
        v.rouge("P-OC-0", "schema doit etre dev11.job_request.v1")
    target = data.get("target")
    if target not in TARGETS:
        v.rouge("P-OC-1", f"target invalide: {target}")
    faces = data.get("max_num_faces", 1)
    if faces != 1:
        v.rouge("P-OC-1", "v1: max_num_faces doit etre 1")


def validate_landmarks(data: Any, v: Verdict, cfg: dict[str, Any], stem_expected: str | None = None) -> None:
    if not isinstance(data, dict):
        v.rouge("P-OC-11", "landmarks n'est pas un objet")
        return
    if data.get("schema") != "dev11.landmarks.v1":
        v.rouge("P-OC-11", "schema doit etre dev11.landmarks.v1")
        return
    stem = data.get("stem")
    if not isinstance(stem, str) or not STEM_RE.match(stem):
        v.rouge("P-OC-11", f"stem invalide: {stem}")
    if stem_expected and stem != stem_expected:
        v.rouge("P-OC-10", f"stem JSON {stem} != fichier {stem_expected}")
    if data.get("target") not in TARGETS:
        v.rouge("P-OC-11", f"target invalide: {data.get('target')}")
    fps = data.get("fps")
    if not isinstance(fps, (int, float)) or float(fps) <= 0:
        v.rouge("P-OC-12", f"fps invalide: {fps}")
    frames = data.get("frames")
    if not isinstance(frames, list):
        v.rouge("P-OC-12", "frames absent")
        return
    if data.get("frame_count") != len(frames):
        v.rouge("P-OC-12", f"frame_count {data.get('frame_count')} != len(frames) {len(frames)}")
    detected_n = 0
    gap = 0
    longest = 0
    for i, frame in enumerate(frames):
        if not isinstance(frame, dict):
            v.rouge("P-OC-13", f"frame {i} n'est pas un objet")
            continue
        if "t_s" not in frame:
            v.rouge("P-OC-13", f"frame {i} sans t_s")
        if not isinstance(frame.get("detected"), bool):
            v.rouge("P-OC-13", f"frame {i} detected non bool")
            continue
        if frame["detected"]:
            detected_n += 1
            gap = 0
            target = frame.get("target")
            if not isinstance(target, dict) or not is_norm(target.get("x")) or not is_norm(target.get("y")):
                v.rouge("P-OC-13", f"frame {i} target x,y hors [0,1]")
        else:
            gap += 1
            longest = max(longest, gap)
            if frame.get("target") not in (None, {}):
                v.rouge("P-OC-13", f"frame {i} detected=false mais target non null")
    ratio_min = float(cfg.get("detected_ratio_min", 0.85))
    if frames:
        ratio = detected_n / len(frames)
        if ratio < ratio_min:
            v.hold("P-OC-14", f"{stem}: detected_ratio {ratio:.3f} < {ratio_min}", stem=str(stem))
    gap_amber = int(cfg.get("gap_amber_frames", 12))
    if longest > gap_amber:
        v.ambre("P-OC-15", f"{stem}: gap {longest} frames > {gap_amber}")


def crop_in_bounds(crop: Any, width: int, height: int) -> bool:
    if not isinstance(crop, dict):
        return False
    try:
        x = int(crop["x"])
        y = int(crop["y"])
        w = int(crop["w"])
        h = int(crop["h"])
    except (KeyError, TypeError, ValueError):
        return False
    if w <= 0 or h <= 0:
        return False
    if x < 0 or y < 0:
        return False
    if x + w > width or y + h > height:
        return False
    return w * 16 == h * 9


def validate_camera_path(data: Any, v: Verdict, cfg: dict[str, Any], stem_expected: str | None = None) -> None:
    if not isinstance(data, dict):
        v.rouge("P-SG-2", "camera_path n'est pas un objet")
        return
    if data.get("schema") != "dev11.camera_path.v1":
        v.rouge("P-SG-2", "schema doit etre dev11.camera_path.v1")
        return
    stem = data.get("stem")
    if stem_expected and stem != stem_expected:
        v.rouge("P-SG-1", f"stem JSON {stem} != fichier {stem_expected}")
    width = data.get("width")
    height = data.get("height")
    if not isinstance(width, int) or not isinstance(height, int) or width <= 0 or height <= 0:
        v.rouge("P-SG-4", f"width/height invalides: {width}x{height}")
        return
    frames = data.get("frames")
    if not isinstance(frames, list):
        v.rouge("P-SG-3", "frames absent")
        return
    if data.get("frame_count") != len(frames):
        v.rouge("P-SG-2", f"frame_count {data.get('frame_count')} != {len(frames)}")
    zoom_min = float(cfg.get("zoom_min", 1.0))
    deltas: list[float] = []
    prev_cx = prev_cy = None
    for i, frame in enumerate(frames):
        if not isinstance(frame, dict):
            v.rouge("P-SG-3", f"frame {i} n'est pas un objet")
            continue
        for key in ("cx", "cy", "zoom"):
            if not isinstance(frame.get(key), (int, float)):
                v.rouge("P-SG-3", f"frame {i} manque {key}")
        zoom = frame.get("zoom")
        if isinstance(zoom, (int, float)) and float(zoom) < zoom_min:
            v.rouge("P-SG-3", f"frame {i} zoom {zoom} < {zoom_min}")
        if not crop_in_bounds(frame.get("crop"), width, height):
            v.rouge("P-SG-4", f"frame {i} crop hors cadre ou pas 9:16")
        cx, cy = frame.get("cx"), frame.get("cy")
        if isinstance(cx, (int, float)) and isinstance(cy, (int, float)):
            if prev_cx is not None and prev_cy is not None:
                deltas.append(((float(cx) - prev_cx) ** 2 + (float(cy) - prev_cy) ** 2) ** 0.5)
            prev_cx, prev_cy = float(cx), float(cy)
        if not isinstance(frame.get("held"), bool):
            v.rouge("P-SG-7", f"frame {i} held non bool")
    jitter_max = float(cfg.get("jitter_median_norm_max", 0.02))
    if deltas:
        median = statistics.median(deltas)
        if median > jitter_max:
            v.rouge("P-SG-5", f"{stem}: jitter median {median:.4f} > {jitter_max}")


def apply_hold_deadzone(
    path_data: dict[str, Any],
    land_data: dict[str, Any] | None,
    v: Verdict,
    cfg: dict[str, Any],
) -> None:
    if land_data is None:
        v.rouge("P-SG-7", "landmarks IN absents pour hold-last / deadzone")
        return
    p_frames = path_data.get("frames") or []
    l_frames = land_data.get("frames") or []
    if len(p_frames) != len(l_frames):
        v.rouge("P-SG-7", "camera_path et landmarks: frame_count divergent")
        return
    deadzone = float(cfg.get("deadzone_norm", 0.04))
    prev_cx = prev_cy = None
    for i, (pf, lf) in enumerate(zip(p_frames, l_frames)):
        if not isinstance(pf, dict) or not isinstance(lf, dict):
            continue
        cx, cy = pf.get("cx"), pf.get("cy")
        if not isinstance(cx, (int, float)) or not isinstance(cy, (int, float)):
            continue
        if lf.get("detected") is False:
            if pf.get("held") is not True:
                v.rouge("P-SG-7", f"frame {i} detected=false sans held")
            if prev_cx is not None and (cx != prev_cx or cy != prev_cy):
                v.rouge("P-SG-7", f"frame {i} hold-last a bouge le centre")
        elif lf.get("detected") is True and prev_cx is not None:
            tgt = lf.get("target") or {}
            tx, ty = tgt.get("x"), tgt.get("y")
            if isinstance(tx, (int, float)) and isinstance(ty, (int, float)):
                dist = ((float(tx) - prev_cx) ** 2 + (float(ty) - prev_cy) ** 2) ** 0.5
                if dist <= deadzone and (cx != prev_cx or cy != prev_cy):
                    v.rouge("P-SG-6", f"frame {i} deadzone violee")
        prev_cx, prev_cy = float(cx), float(cy)


def validate_calix_manifest(data: Any, v: Verdict, expected_stems: set[str]) -> None:
    if not isinstance(data, dict):
        v.rouge("P-CX-4", "manifeste n'est pas un objet")
        return
    if data.get("schema") != "dev11.calix_manifest.v1":
        v.rouge("P-CX-4", "schema doit etre dev11.calix_manifest.v1")
        return
    stems = data.get("stems")
    if not isinstance(stems, list) or not stems:
        v.rouge("P-CX-4", "stems vide")
        return
    listed: set[str] = set()
    for entry in stems:
        if not isinstance(entry, dict):
            v.rouge("P-CX-4", "entree stem non objet")
            continue
        stem = entry.get("stem")
        if not isinstance(stem, str):
            v.rouge("P-CX-4", "stem manquant")
            continue
        listed.add(stem)
        rel = entry.get("file")
        if not isinstance(rel, str) or not rel.startswith("tracked/"):
            v.rouge("P-CX-4", f"{stem}: file relatif tracked/ obligatoire")
        sha = entry.get("sha256")
        if not isinstance(sha, str) or len(sha) != 64:
            v.rouge("P-CX-4", f"{stem}: sha256 64 hex")
        audio = entry.get("audio")
        if audio not in {"copy", "none"}:
            v.rouge("P-CX-3", f"{stem}: audio doit etre copy|none")
    missing = expected_stems - listed
    extra = listed - expected_stems
    if missing:
        v.rouge("P-CX-6", f"stems manquants: {sorted(missing)}")
    if extra:
        v.rouge("P-CX-4", f"stems inconnus: {sorted(extra)}")


def check_isolation(root: Path, frigate: str, v: Verdict) -> None:
    codebase = root / frigate / "CODEBASE"
    if not codebase.is_dir():
        return
    forbidden = SISTER_OUT[frigate]
    for py in codebase.rglob("*.py"):
        text = py.read_text(encoding="utf-8")
        for needle in forbidden:
            if needle in text:
                v.rouge("P-ISO-1", f"{py.relative_to(root)} cite {needle}")


def check_in_f01(root: Path, v: Verdict) -> None:
    in_dir = root / "F01_OCULUS" / "IN"
    req = load_json(in_dir / "job_request.json", v, "P-OC-0")
    if req is not None:
        validate_job_request(req, v)
    clips = list_mp4(in_dir / "clips")
    if not clips:
        v.rouge("P-OC-2", "aucun IN/clips/*.mp4")
    check_stems([stem_of(p) for p in clips], v, "P-OC-5")
    v.ambre("P-OC-3", "probe H.264/duree differe (P-CI-1: pas de decode GHA)")
    v.ambre("P-OC-4", "resolution 1080x1920 recommandee, non probee en CI")


def check_out_f01(root: Path, v: Verdict, cfg: dict[str, Any]) -> None:
    in_dir = root / "F01_OCULUS" / "IN"
    out_dir = root / "F01_OCULUS" / "OUT"
    clips = list_mp4(in_dir / "clips")
    if not clips:
        v.rouge("P-OC-10", "aucun clip IN pour apparier landmarks")
        return
    for clip in clips:
        path = out_dir / "landmarks" / f"{clip.stem}.json"
        data = load_json(path, v, "P-OC-10")
        if data is not None:
            validate_landmarks(data, v, cfg, stem_expected=clip.stem)
    report = load_json(out_dir / "oculus_report.json", v, "P-OC-16")
    if report is not None and report.get("schema") != "dev11.oculus_report.v1":
        v.rouge("P-OC-16", "oculus_report schema")


def check_in_f02(root: Path, v: Verdict, cfg: dict[str, Any]) -> None:
    in_dir = root / "F02_SANGUINOR" / "IN"
    lands = list_json(in_dir / "landmarks")
    if not lands:
        v.rouge("P-SG-0", "aucun IN/landmarks/*.json")
        return
    clips = {p.stem for p in list_mp4(in_dir / "clips")}
    for land in lands:
        data = load_json(land, v, "P-SG-0")
        if data is not None:
            validate_landmarks(data, v, cfg, stem_expected=land.stem)
        if land.stem not in clips:
            v.rouge("P-SG-0", f"clip manquant pour {land.stem}")
    req_path = in_dir / "camera_request.json"
    if req_path.is_file():
        req = load_json(req_path, v, "P-SG-0")
        if req is not None and req.get("schema") != "dev11.camera_request.v1":
            v.rouge("P-SG-0", "camera_request schema")


def check_out_f02(root: Path, v: Verdict, cfg: dict[str, Any]) -> None:
    in_dir = root / "F02_SANGUINOR" / "IN"
    out_dir = root / "F02_SANGUINOR" / "OUT"
    lands = list_json(in_dir / "landmarks")
    if not lands:
        v.rouge("P-SG-1", "aucun landmarks IN")
        return
    for land in lands:
        path = out_dir / "camera_path" / f"{land.stem}.json"
        data = load_json(path, v, "P-SG-1")
        land_data = load_json(land, v, "P-SG-0")
        if data is not None:
            validate_camera_path(data, v, cfg, stem_expected=land.stem)
            if land_data is not None:
                apply_hold_deadzone(data, land_data, v, cfg)
    report = load_json(out_dir / "sanguinor_report.json", v, "P-SG-9")
    if report is not None and report.get("schema") != "dev11.sanguinor_report.v1":
        v.rouge("P-SG-9", "sanguinor_report schema")


def check_in_f03(root: Path, v: Verdict, cfg: dict[str, Any]) -> None:
    in_dir = root / "F03_CALIX" / "IN"
    paths = list_json(in_dir / "camera_path")
    if not paths:
        v.rouge("P-CX-0", "aucun IN/camera_path/*.json")
        return
    clips = {p.stem for p in list_mp4(in_dir / "clips")}
    for path in paths:
        data = load_json(path, v, "P-CX-0")
        if data is not None:
            validate_camera_path(data, v, cfg, stem_expected=path.stem)
        if path.stem not in clips:
            v.rouge("P-CX-0", f"clip manquant pour {path.stem}")


def check_out_f03(root: Path, v: Verdict) -> None:
    in_dir = root / "F03_CALIX" / "IN"
    out_dir = root / "F03_CALIX" / "OUT"
    expected = {p.stem for p in list_json(in_dir / "camera_path")}
    if not expected:
        v.rouge("P-CX-1", "aucun camera_path IN")
        return
    tracked = out_dir / "tracked"
    missing_files: list[str] = []
    for stem in sorted(expected):
        mp4 = tracked / f"{stem}.mp4"
        if not mp4.is_file():
            missing_files.append(stem)
            v.rouge("P-CX-1", f"tracked/{stem}.mp4 absent")
    manifest = load_json(out_dir / "calix_manifest.json", v, "P-CX-4")
    if manifest is not None:
        validate_calix_manifest(manifest, v, expected)
        if missing_files:
            v.rouge("P-CX-6", "artifact incomplet")
    report = load_json(out_dir / "calix_report.json", v, "P-CX-7")
    if report is not None and report.get("schema") != "dev11.calix_report.v1":
        v.rouge("P-CX-7", "calix_report schema")
    v.ambre("P-CX-2", "probe H.264/9:16/duree differe (P-CI-1)")
    v.ambre("P-CX-5", "faststart differe (P-CI-1)")


def run_custos(root: Path, frigate: str, mode: str) -> Verdict:
    v = Verdict()
    cfg = load_config(root)
    check_isolation(root, frigate, v)
    if frigate == "F01_OCULUS" and mode == "check-in":
        check_in_f01(root, v)
    elif frigate == "F01_OCULUS" and mode == "check-out":
        check_out_f01(root, v, cfg)
    elif frigate == "F02_SANGUINOR" and mode == "check-in":
        check_in_f02(root, v, cfg)
    elif frigate == "F02_SANGUINOR" and mode == "check-out":
        check_out_f02(root, v, cfg)
    elif frigate == "F03_CALIX" and mode == "check-in":
        check_in_f03(root, v, cfg)
    elif frigate == "F03_CALIX" and mode == "check-out":
        check_out_f03(root, v)
    else:
        v.rouge("P-ISO-1", f"mode inconnu {frigate} {mode}")
    return v


def main() -> int:
    parser = argparse.ArgumentParser(description="LAC_CUSTOS — portes dev-11")
    parser.add_argument("--frigate", required=True)
    parser.add_argument("--mode", required=True, choices=("check-in", "check-out"))
    parser.add_argument("--root", default=str(ROOT_DEFAULT))
    args = parser.parse_args()
    frigate = resolve_frigate(args.frigate)
    verdict = run_custos(Path(args.root), frigate, args.mode)
    verdict.dump(sys.stderr)
    return 1 if verdict.refused else 0


if __name__ == "__main__":
    raise SystemExit(main())

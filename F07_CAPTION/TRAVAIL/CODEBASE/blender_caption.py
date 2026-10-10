#!/usr/bin/env python3
"""H3/H4 — Blender headless : proof 1 mot OU calque alpha video entiere.

Usage:
  blender --background --python blender_caption.py -- --mode proof --style s.json --word HOE --out OUT
  blender --background --python blender_caption.py -- --mode render --style s.json --transcript t.json --out OUT
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from caption_schema import (  # noqa: E402
    CANVAS_SIZE,
    build_proof_request,
    hex_to_rgba,
    iter_couples,
    motion_windows,
    normalize_style,
    parse_transcript,
    resolve_font,
)


def _argv_after_dash() -> list[str]:
    if "--" in sys.argv:
        return sys.argv[sys.argv.index("--") + 1 :]
    return sys.argv[1:]


def parse_args(argv: list[str]) -> dict:
    out = {
        "mode": "proof",
        "style": None,
        "transcript": None,
        "word": "HOE",
        "out": None,
        "fps": 30,
        "duration": 1.0,
        "frames": 3,
        "fonts": str(HERE / "fonts"),
    }
    i = 0
    while i < len(argv):
        key = argv[i]
        if key == "--mode" and i + 1 < len(argv):
            out["mode"] = argv[i + 1]
            i += 2
            continue
        if key == "--style" and i + 1 < len(argv):
            out["style"] = argv[i + 1]
            i += 2
            continue
        if key == "--transcript" and i + 1 < len(argv):
            out["transcript"] = argv[i + 1]
            i += 2
            continue
        if key == "--word" and i + 1 < len(argv):
            out["word"] = argv[i + 1]
            i += 2
            continue
        if key == "--out" and i + 1 < len(argv):
            out["out"] = argv[i + 1]
            i += 2
            continue
        if key == "--fps" and i + 1 < len(argv):
            out["fps"] = int(argv[i + 1])
            i += 2
            continue
        if key == "--duration" and i + 1 < len(argv):
            out["duration"] = float(argv[i + 1])
            i += 2
            continue
        if key == "--frames" and i + 1 < len(argv):
            out["frames"] = int(argv[i + 1])
            i += 2
            continue
        if key == "--fonts" and i + 1 < len(argv):
            out["fonts"] = argv[i + 1]
            i += 2
            continue
        i += 1
    return out


def load_json(path: str | None) -> dict:
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def motion_scale(motion: str, elapsed_sec: float, speed: float = 1.0, word_dur: float | None = None) -> float:
    elapsed = max(0.0, float(elapsed_sec) if elapsed_sec == elapsed_sec else 0.0)
    if motion == "slide":
        return 1.0
    attack, settle = motion_windows(speed, word_dur)
    if motion == "bounce":
        t = min(1.0, elapsed / max(0.05, settle))
        return 0.35 + 0.65 * (1 - abs(math.sin((1 - t) * math.pi * 0.5)))
    if elapsed < attack:
        return 0.2 + 1.05 * (elapsed / max(1e-6, attack))
    if elapsed < settle:
        return 1.25 - 0.25 * ((elapsed - attack) / max(1e-6, settle - attack))
    return 1.0


def motion_offset_x(motion: str, local_t: float, width: float) -> float:
    if motion != "slide":
        return 0.0
    t = max(0.0, min(1.0, local_t))
    return (1.0 - t) * (-width * 0.15)


def setup_scene(style: dict, fps: int, frame_end: int):
    import bpy

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    width, height = CANVAS_SIZE[style["canvas"]]
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    scene.frame_start = 1
    scene.frame_end = max(1, frame_end)
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        scene.render.engine = engine
        if scene.render.engine == engine:
            break
    if hasattr(scene, "eevee"):
        scene.eevee.use_bloom = True
        scene.eevee.bloom_intensity = float(style["glow"]["intensity"])
        scene.eevee.bloom_threshold = 0.6
        scene.eevee.bloom_radius = 6.5
    cam_data = bpy.data.cameras.new("CaptionCam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 2.0
    cam = bpy.data.objects.new("CaptionCam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam.location = (0.0, 0.0, 6.0)
    cam.rotation_euler = (0.0, 0.0, 0.0)
    world = bpy.data.worlds.new("CaptionWorld")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0, 0, 0, 0)
        bg.inputs[1].default_value = 0.0
    return scene, width, height


def make_material(style: dict, name: str):
    import bpy

    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = hex_to_rgba(style["color"])
    emission.inputs["Strength"].default_value = 1.0 + float(style["glow"]["intensity"]) * 3.0
    links.new(emission.outputs["Emission"], out.inputs["Surface"])
    return mat


def add_text(scene, style: dict, word: str, font_path: Path, width: int, height: int, start_frame: int, end_frame: int, wait_start_frame: int | None = None, slot: str = "left", word_dur: float | None = None):
    import bpy

    curve = bpy.data.curves.new(name=f"txt_{word[:12]}", type="FONT")
    curve.body = word
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.extrude = 0.04
    curve.bevel_depth = 0.008
    if font_path.is_file():
        curve.font = bpy.data.fonts.load(str(font_path))
    obj = bpy.data.objects.new(curve.name, curve)
    scene.collection.objects.link(obj)
    obj.data.materials.append(make_material(style, f"mat_{obj.name}"))
    size_norm = style["size"] / 72.0 * 0.22
    obj.scale = (size_norm, size_norm, size_norm)
    x_center = (style["position"]["x_pct"] / 100.0 - 0.5) * 2.0
    y = (0.5 - style["position"]["y_pct"] / 100.0) * 2.0 * (height / width)
    gap = size_norm * 1.45
    x = x_center - gap / 2.0 if slot == "left" else x_center + gap / 2.0
    obj.location = (x, y, 0.0)
    motion = style["motion"]
    speed = float(style.get("motion_speed") or 1.0)
    fps = float(getattr(scene, "render", None).fps) if getattr(scene, "render", None) else 30.0
    if fps <= 0:
        fps = 30.0
    attack, settle = motion_windows(speed, word_dur)
    if wait_start_frame is not None and wait_start_frame < start_frame:
        obj.hide_render = True
        obj.keyframe_insert(data_path="hide_render", frame=wait_start_frame - 1)
        obj.hide_render = False
        obj.keyframe_insert(data_path="hide_render", frame=wait_start_frame)
        obj.scale = (size_norm, size_norm, size_norm)
        obj.location = (x, y, 0.0)
        obj.keyframe_insert(data_path="scale", frame=wait_start_frame)
        obj.keyframe_insert(data_path="location", frame=wait_start_frame)
        obj.keyframe_insert(data_path="scale", frame=start_frame - 1)
        obj.keyframe_insert(data_path="location", frame=start_frame - 1)
    else:
        obj.hide_render = True
        obj.keyframe_insert(data_path="hide_render", frame=start_frame - 1)
        obj.hide_render = False
        obj.keyframe_insert(data_path="hide_render", frame=start_frame)
    for frame in (
        start_frame,
        start_frame + max(1, int(round(attack * fps))),
        start_frame + max(1, int(round(settle * fps))),
        end_frame,
    ):
        elapsed = (frame - start_frame) / fps
        s = motion_scale(motion, elapsed, speed, word_dur) * size_norm
        obj.scale = (s, s, s)
        obj.location = (x + motion_offset_x(motion, elapsed, 2.0), y, 0.0)
        obj.keyframe_insert(data_path="scale", frame=frame)
        obj.keyframe_insert(data_path="location", frame=frame)
    obj.hide_render = True
    obj.keyframe_insert(data_path="hide_render", frame=end_frame + 1)
    return obj


def render_frames(scene, out_dir: Path, prefix: str) -> list[str]:
    written = []
    out_dir.mkdir(parents=True, exist_ok=True)
    for frame in range(scene.frame_start, scene.frame_end + 1):
        scene.frame_set(frame)
        dest = out_dir / f"{prefix}_{frame:04d}.png"
        scene.render.filepath = str(dest)
        import bpy

        bpy.ops.render.render(write_still=True)
        written.append(dest.name)
    return written


def run_proof(args: dict) -> dict:
    style = normalize_style(load_json(args["style"]))
    req = build_proof_request(style, args["word"], frames=args["frames"])
    font = resolve_font(style, Path(args["fonts"]))
    frames = max(1, min(3, int(req["frames"])))
    scene, width, height = setup_scene(style, fps=30, frame_end=frames)
    add_text(scene, style, req["word"], font, width, height, 1, frames, word_dur=frames / 30.0)
    out = Path(args["out"])
    names = render_frames(scene, out, "proof")
    report = {
        "schema_version": "dev11.caption.proof.v1",
        "word": req["word"],
        "style_id": style["id"],
        "frames": names,
        "qa_pass": bool(names),
    }
    (out / "proof_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def run_render(args: dict) -> dict:
    style = normalize_style(load_json(args["style"]))
    transcript = parse_transcript(load_json(args["transcript"]))
    if not transcript["words"]:
        raise SystemExit("C1: transcript vide")
    font = resolve_font(style, Path(args["fonts"]))
    last = max(w["end"] for w in transcript["words"])
    fps = int(args["fps"])
    frame_end = max(1, int(math.ceil(last * fps)))
    scene, width, height = setup_scene(style, fps=fps, frame_end=frame_end)
    for left, right, hide in iter_couples(transcript["words"]):
        hide_f = max(2, int(hide * fps) + 1)
        left_start = max(1, int(left["start"] * fps) + 1)
        left_end_t = right["start"] if right else hide
        add_text(
            scene, style, left["word"], font, width, height,
            left_start, hide_f, wait_start_frame=None, slot="left",
            word_dur=max(0.05, left_end_t - left["start"]),
        )
        if right:
            right_start = max(left_start + 1, int(right["start"] * fps) + 1)
            add_text(
                scene, style, right["word"], font, width, height,
                right_start, hide_f, wait_start_frame=left_start, slot="right",
                word_dur=max(0.05, hide - right["start"]),
            )
    out = Path(args["out"]) / "frames"
    names = render_frames(scene, out, "cap")
    report = {
        "schema_version": "dev11.caption.render.v1",
        "style_id": style["id"],
        "words": len(transcript["words"]),
        "frames": len(names),
        "frame_dir": str(out),
        "qa_pass": bool(names),
    }
    Path(args["out"]).mkdir(parents=True, exist_ok=True)
    (Path(args["out"]) / "render_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    args = parse_args(_argv_after_dash())
    if not args["out"]:
        print("blender_caption: --out requis", file=sys.stderr)
        return 1
    if args["mode"] == "proof":
        report = run_proof(args)
    elif args["mode"] == "render":
        report = run_render(args)
    else:
        print(f"mode inconnu: {args['mode']}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report.get("qa_pass") else 1


if __name__ == "__main__":
    try:
        import bpy  # noqa: F401
    except ImportError:
        print("blender_caption.py doit tourner via blender --background --python", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main())

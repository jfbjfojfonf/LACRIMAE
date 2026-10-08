import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "CODEBASE"))
import blender_caption  # noqa: E402


def test_parse_args_proof():
    args = blender_caption.parse_args(["--mode", "proof", "--word", "HOE", "--out", "/tmp/out", "--frames", "2"])
    assert args["mode"] == "proof"
    assert args["word"] == "HOE"
    assert args["frames"] == 2


def test_motion_scale_pop_in_overshoot():
    assert blender_caption.motion_scale("pop-in", 0.0) == 0.2
    mid = blender_caption.motion_scale("pop-in", 0.22)
    rest = blender_caption.motion_scale("pop-in", 1.0)
    assert mid > rest
    assert rest == 1.0


def test_motion_scale_speed_faster():
    slow = blender_caption.motion_scale("pop-in", 0.05, 0.5)
    fast = blender_caption.motion_scale("pop-in", 0.05, 3.0)
    assert fast > slow


def test_motion_slide_offset():
    assert blender_caption.motion_offset_x("pop-in", 0.0, 2.0) == 0.0
    assert blender_caption.motion_offset_x("slide", 0.0, 2.0) < 0

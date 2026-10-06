import json
import subprocess
import sys
import unittest
from pathlib import Path

CODE = Path(__file__).resolve().parent.parent / "CODEBASE"
sys.path.insert(0, str(CODE))

from lut import build_ffmpeg_cmd, find_lut, lut3d_filter, render_lut  # noqa: E402


class LutTests(unittest.TestCase):
    def test_lut3d_filter_escapes_colon(self):
        filt = lut3d_filter(Path("C:/SHARED/IN/look.cube"))
        self.assertIn("lut3d=file=", filt)
        self.assertIn("look.cube", filt)

    def test_build_ffmpeg_cmd_has_lut3d(self):
        cmd = build_ffmpeg_cmd(Path("in.mp4"), Path("out.mp4"), Path("look.cube"))
        self.assertEqual(cmd[0], "ffmpeg")
        self.assertIn("lut3d=file=", cmd[cmd.index("-vf") + 1])
        self.assertIn("libx264", cmd)

    def test_find_lut_missing(self):
        tmp = Path("/tmp/lacrimae_f_no_lut")
        tmp.mkdir(parents=True, exist_ok=True)
        with self.assertRaises(FileNotFoundError):
            find_lut(None, tmp)

    def test_find_lut_explicit(self):
        tmp = Path("/tmp/lacrimae_f_lut")
        tmp.mkdir(parents=True, exist_ok=True)
        cube = tmp / "pack.cube"
        cube.write_text("TITLE Identity\n", encoding="utf-8")
        found = find_lut(cube, tmp)
        self.assertEqual(found, cube.resolve())

    def test_dry_run(self):
        tmp = Path("/tmp/lacrimae_f_lut_dry")
        queue = tmp / "queue"
        outbox = tmp / "outbox"
        queue.mkdir(parents=True, exist_ok=True)
        cube = tmp / "look.cube"
        cube.write_text("TITLE Identity\n", encoding="utf-8")
        manifest = {
            "generated_at": "2026-10-06T00:00:00Z",
            "items": [
                {
                    "id": "clip-aaaa1111",
                    "video_path": str(tmp / "clip-aaaa1111.mp4"),
                }
            ],
        }
        manifest_path = queue / "manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        summary = render_lut(manifest_path, cube, outbox, dry_run=True)
        self.assertEqual(summary["results"][0]["status"], "dry_run")
        self.assertEqual(summary["results"][0]["cmd"][0], "ffmpeg")
        report = json.loads((outbox / "lut_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["results"][0]["id"], "clip-aaaa1111")

    def test_render_success_mocked_ffmpeg(self):
        tmp = Path("/tmp/lacrimae_f_lut_run")
        queue = tmp / "queue"
        outbox = tmp / "outbox"
        queue.mkdir(parents=True, exist_ok=True)
        src = tmp / "clip-bbbb2222.mp4"
        src.write_bytes(b"fake")
        cube = tmp / "look.cube"
        cube.write_text("TITLE Identity\n", encoding="utf-8")
        manifest_path = queue / "manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "items": [
                        {"id": "clip-bbbb2222", "video_path": str(src)}
                    ]
                }
            ),
            encoding="utf-8",
        )

        def fake_run(cmd):
            dest = Path(cmd[-1])
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(b"colored")
            return subprocess.CompletedProcess(cmd, 0, "", "")

        summary = render_lut(manifest_path, cube, outbox, run_fn=fake_run)
        self.assertEqual(summary["results"][0]["status"], "success")
        self.assertTrue((outbox / "clip-bbbb2222.mp4").exists())


if __name__ == "__main__":
    unittest.main()

import json
import sys
import unittest
from pathlib import Path

CODE = Path(__file__).resolve().parent.parent / "CODEBASE"
sys.path.insert(0, str(CODE))

from ingest import ingest, make_id, validate_metadata  # noqa: E402


def fake_probe_ok(_path: Path) -> dict:
    return {
        "width": 1920,
        "height": 1080,
        "fps": 30.0,
        "duration_sec": 8.0,
        "has_audio": False,
        "size_bytes": 1234,
    }


def fake_probe_bad_res(_path: Path) -> dict:
    return {
        "width": 1280,
        "height": 720,
        "fps": 30.0,
        "duration_sec": 8.0,
        "has_audio": False,
        "size_bytes": 1234,
    }


class IngestTests(unittest.TestCase):
    def test_validate_ok(self):
        self.assertEqual(validate_metadata(fake_probe_ok(Path("x")), 1920, 1080), [])

    def test_validate_bad_res(self):
        errs = validate_metadata(fake_probe_bad_res(Path("x")), 1920, 1080)
        self.assertTrue(errs)

    def test_ingest_copies_and_manifest(self):
        tmp = Path("/tmp/lacrimae_f_ingest_test")
        source = tmp / "sources"
        inbox = tmp / "inbox"
        queue = tmp / "queue"
        source.mkdir(parents=True, exist_ok=True)
        video = source / "clip_one.mp4"
        video.write_bytes(b"fake-mp4")
        manifest = ingest(source, inbox, queue, probe_fn=fake_probe_ok)
        self.assertEqual(len(manifest["items"]), 1)
        item = manifest["items"][0]
        self.assertTrue(item["id"].startswith("clip_one-"))
        self.assertEqual(item["source_name"], "clip_one.mp4")
        dest = Path(item["video_path"])
        self.assertTrue(dest.exists())
        self.assertEqual(dest.read_bytes(), b"fake-mp4")
        written = json.loads((queue / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(written["items"][0]["id"], item["id"])
        self.assertEqual(make_id(video), item["id"])

    def test_ingest_skips_bad_resolution(self):
        tmp = Path("/tmp/lacrimae_f_ingest_skip")
        source = tmp / "sources"
        inbox = tmp / "inbox"
        queue = tmp / "queue"
        source.mkdir(parents=True, exist_ok=True)
        (source / "bad.mp4").write_bytes(b"x")
        manifest = ingest(source, inbox, queue, probe_fn=fake_probe_bad_res)
        self.assertEqual(manifest["items"], [])
        skipped = json.loads((queue / "skipped.json").read_text(encoding="utf-8"))
        self.assertEqual(skipped[0]["source_name"], "bad.mp4")


if __name__ == "__main__":
    unittest.main()

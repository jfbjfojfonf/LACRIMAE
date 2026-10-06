import sys
import unittest
from pathlib import Path

CODE = Path(__file__).resolve().parent.parent / "CODEBASE"
sys.path.insert(0, str(CODE))

from modal_app import APP_NAME, LUT_REMOTE, VOLUME_MOUNT, VOLUME_NAME, plan_jobs  # noqa: E402


class ModalAppTests(unittest.TestCase):
    def test_names(self):
        self.assertEqual(APP_NAME, "lacrimae-dev6f-lut")
        self.assertEqual(VOLUME_NAME, "lacrimae-dev6f")
        self.assertTrue(LUT_REMOTE.startswith(VOLUME_MOUNT))
        self.assertTrue(LUT_REMOTE.endswith(".cube"))

    def test_plan_jobs(self):
        tmp = Path("/tmp/lacrimae_f_modal_plan")
        inbox = tmp / "inbox"
        outbox = tmp / "outbox"
        inbox.mkdir(parents=True, exist_ok=True)
        (inbox / "clip-aaaa1111.mp4").write_bytes(b"x")
        (inbox / "notes.txt").write_text("no", encoding="utf-8")
        cube = tmp / "Cinematic.cube"
        jobs = plan_jobs(inbox, outbox, cube)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["id"], "clip-aaaa1111")
        self.assertEqual(jobs[0]["output"], str(outbox / "clip-aaaa1111.mp4"))
        self.assertEqual(jobs[0]["lut"], str(cube))


if __name__ == "__main__":
    unittest.main()

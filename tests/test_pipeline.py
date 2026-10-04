import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "F01_INGEST"))
sys.path.insert(0, str(ROOT / "F02_RENDER"))

import pipeline  # noqa: E402


def fake_probe(_path: Path) -> dict:
    return {
        "width": 1920,
        "height": 1080,
        "fps": 30.0,
        "duration_sec": 4.0,
        "has_audio": False,
        "size_bytes": 10,
    }


class PipelineTests(unittest.TestCase):
    def test_pipeline_dry_run(self):
        tmp = Path("/tmp/lacrimae_pipeline")
        source = tmp / "sources"
        inbox = tmp / "inbox"
        queue = tmp / "queue"
        outbox = tmp / "outbox"
        source.mkdir(parents=True, exist_ok=True)
        (source / "ok.mp4").write_bytes(b"data")
        paths = {
            "vps": {
                "sources_dir": str(source),
                "inbox_dir": str(inbox),
                "queue_dir": str(queue),
                "outbox_dir": str(outbox),
                "nexrender_server": "http://127.0.0.1:3000",
                "nexrender_secret_env": "NEXRENDER_SECRET",
            },
            "conventions": {"expected_width": 1920, "expected_height": 1080},
        }
        paths_file = tmp / "paths.json"
        paths_file.write_text(json.dumps(paths), encoding="utf-8")
        with patch("pipeline.ingest") as ingest_mock, patch("pipeline.render") as render_mock:
            ingest_mock.return_value = {"items": [{"id": "ok-1"}]}
            render_mock.return_value = {"results": [{"status": "dry_run"}]}
            rc = pipeline.main(["--paths", str(paths_file), "--dry-run"])
            self.assertEqual(rc, 0)
            ingest_mock.assert_called_once()
            render_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()

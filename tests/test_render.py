import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "F02_RENDER"))

from render import build_job, jobs_url, render, to_file_url  # noqa: E402


class RenderTests(unittest.TestCase):
    def test_to_file_url_windows(self):
        self.assertEqual(
            to_file_url(r"C:\nexrender\inbox\a.mp4"),
            "file:///C:/nexrender/inbox/a.mp4",
        )

    def test_build_job_substitutes_paths(self):
        template = json.loads(
            (ROOT / "NEXRENDER" / "jobs" / "job.reference.json").read_text(encoding="utf-8")
        )
        item = {
            "id": "clip-abcd1234",
            "video_path": r"C:\nexrender\inbox\clip-abcd1234.mp4",
        }
        job = build_job(item, template, r"C:\nexrender\outbox")
        video = next(a for a in job["assets"] if a["type"] == "video")
        self.assertEqual(video["src"], "file:///C:/nexrender/inbox/clip-abcd1234.mp4")
        self.assertEqual(video["layerName"], "SRC")
        copy_action = next(
            a for a in job["actions"]["postrender"] if a["module"] == "@nexrender/action-copy"
        )
        self.assertTrue(copy_action["output"].endswith("clip-abcd1234.mp4"))

    def test_dry_run_writes_jobs(self):
        tmp = Path("/tmp/lacrimae_render_test")
        queue = tmp / "queue"
        jobs_dir = queue / "jobs"
        outbox = tmp / "outbox"
        queue.mkdir(parents=True, exist_ok=True)
        manifest = {
            "generated_at": "2026-10-04T11:00:00Z",
            "items": [
                {
                    "id": "clip-aaaa1111",
                    "video_path": r"C:\nexrender\inbox\clip-aaaa1111.mp4",
                    "source_name": "clip.mp4",
                }
            ],
        }
        manifest_path = queue / "manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        summary = render(
            manifest_path=manifest_path,
            job_template_path=ROOT / "NEXRENDER" / "jobs" / "job.reference.json",
            outbox_dir=outbox,
            jobs_dir=jobs_dir,
            server="http://127.0.0.1:3000",
            dry_run=True,
        )
        self.assertEqual(summary["results"][0]["status"], "dry_run")
        job_file = jobs_dir / "clip-aaaa1111.json"
        self.assertTrue(job_file.exists())
        job = json.loads(job_file.read_text(encoding="utf-8"))
        self.assertEqual(job["template"]["composition"], "MAIN")

    def test_submit_and_poll_success(self):
        tmp = Path("/tmp/lacrimae_render_poll")
        queue = tmp / "queue"
        jobs_dir = queue / "jobs"
        outbox = tmp / "outbox"
        queue.mkdir(parents=True, exist_ok=True)
        manifest = {
            "items": [
                {
                    "id": "clip-bbbb2222",
                    "video_path": r"C:\nexrender\inbox\clip-bbbb2222.mp4",
                }
            ]
        }
        manifest_path = queue / "manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        def post(_method, url, payload=None):
            self.assertTrue(url.endswith("/api/v1/jobs"))
            self.assertEqual(payload["assets"][0]["layerName"], "SRC")
            return {"uid": "job-1"}

        def get(_method, url, payload=None):
            self.assertTrue(url.endswith("/api/v1/jobs/job-1"))
            return {"state": "finished"}

        summary = render(
            manifest_path=manifest_path,
            job_template_path=ROOT / "NEXRENDER" / "jobs" / "job.reference.json",
            outbox_dir=outbox,
            jobs_dir=jobs_dir,
            server="http://127.0.0.1:3000",
            post_fn=post,
            get_fn=get,
        )
        self.assertEqual(summary["results"][0]["status"], "success")
        self.assertEqual(summary["results"][0]["nexrender_uid"], "job-1")

    def test_jobs_url(self):
        self.assertEqual(jobs_url("http://127.0.0.1:3000"), "http://127.0.0.1:3000/api/v1/jobs")
        self.assertEqual(
            jobs_url("http://127.0.0.1:3000/", "abc"),
            "http://127.0.0.1:3000/api/v1/jobs/abc",
        )


if __name__ == "__main__":
    unittest.main()

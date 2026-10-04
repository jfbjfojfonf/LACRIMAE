#!/usr/bin/env python3
"""Enchaine F01_INGEST puis F02_RENDER."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "F01_INGEST"))
sys.path.insert(0, str(REPO_ROOT / "F02_RENDER"))

from ingest import ingest, load_paths  # noqa: E402
from render import render  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="F01 puis F02")
    parser.add_argument("--paths", type=Path, default=REPO_ROOT / "NEXRENDER" / "paths.json")
    parser.add_argument("--source", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--secret", default=None)
    args = parser.parse_args(argv)

    cfg = load_paths(args.paths)
    vps = cfg["vps"]
    conv = cfg["conventions"]
    source = args.source or Path(vps["sources_dir"])
    inbox = Path(vps["inbox_dir"])
    queue = Path(vps["queue_dir"])
    outbox = Path(vps["outbox_dir"])
    jobs_dir = queue / "jobs"

    manifest = ingest(
        source_dir=source,
        inbox_dir=inbox,
        queue_dir=queue,
        expected_width=int(conv["expected_width"]),
        expected_height=int(conv["expected_height"]),
    )
    print(json.dumps({"ingest_items": len(manifest["items"])}))
    if not manifest["items"]:
        print("aucun item valide, stop", file=sys.stderr)
        return 1

    secret = args.secret or os.environ.get(vps.get("nexrender_secret_env", "NEXRENDER_SECRET"))
    summary = render(
        manifest_path=queue / "manifest.json",
        job_template_path=REPO_ROOT / "NEXRENDER" / "jobs" / "job.reference.json",
        outbox_dir=outbox,
        jobs_dir=jobs_dir,
        server=vps["nexrender_server"],
        dry_run=args.dry_run,
        secret=secret,
    )
    failed = [r for r in summary["results"] if r.get("status") == "failed"]
    print(json.dumps({"jobs": len(summary["results"]), "failed": len(failed)}))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

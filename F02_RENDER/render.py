#!/usr/bin/env python3
"""F02_RENDER: manifeste F01 → jobs Nexrender → suivi → outbox."""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PATHS = REPO_ROOT / "NEXRENDER" / "paths.json"
DEFAULT_JOB = REPO_ROOT / "NEXRENDER" / "jobs" / "job.reference.json"


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def to_file_url(path: str) -> str:
    p = path.replace("\\", "/")
    if p.startswith("file://"):
        return p
    if len(p) >= 2 and p[1] == ":":
        return "file:///" + p
    if not p.startswith("/"):
        p = "/" + p
    return "file://" + p


def build_job(item: dict, template: dict, outbox_dir: str) -> dict:
    job = copy.deepcopy(template)
    ident = item["id"]
    video_path = item["video_path"]
    video_url = to_file_url(video_path)
    for asset in job.get("assets", []):
        if asset.get("type") == "video":
            asset["src"] = video_url
            asset["layerName"] = asset.get("layerName") or "SRC"
    dest = str(Path(outbox_dir) / f"{ident}.mp4").replace("\\", "/")
    for action in job.get("actions", {}).get("postrender", []):
        if action.get("module") == "@nexrender/action-copy":
            action["output"] = dest
    return job


def jobs_url(server: str, job_id: str | None = None) -> str:
    base = server.rstrip("/") + "/api/v1/jobs"
    return base + "/" + job_id if job_id else base


def http_json(
    method: str,
    url: str,
    payload: dict | None = None,
    timeout: int = 30,
    secret: str | None = None,
) -> dict:
    data = None
    headers = {"Accept": "application/json"}
    if secret:
        headers["nexrender-secret"] = secret
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} {url}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"nexrender-server injoignable ({url}): {exc.reason}") from exc


def submit_job(
    server: str,
    job: dict,
    post_fn: Callable[..., dict] | None = None,
    secret: str | None = None,
) -> str:
    post = post_fn or (
        lambda method, url, payload=None: http_json(method, url, payload, secret=secret)
    )
    result = post("POST", jobs_url(server), job)
    job_id = result.get("uid") or result.get("id") or result.get("jobId")
    if not job_id:
        raise RuntimeError(f"reponse submit sans id: {result}")
    return str(job_id)


def poll_job(
    server: str,
    job_id: str,
    get_fn: Callable[..., dict] | None = None,
    timeout_sec: int = 3600,
    interval_sec: float = 5.0,
    secret: str | None = None,
) -> dict:
    get = get_fn or (
        lambda method, url, payload=None: http_json(method, url, payload, secret=secret)
    )
    url = jobs_url(server, job_id)
    deadline = time.time() + timeout_sec
    last = {}
    while time.time() < deadline:
        last = get("GET", url)
        state = str(last.get("state") or last.get("status") or "").lower()
        if state in {"finished", "done", "completed", "success"}:
            return last
        if state in {"error", "failed", "failure"}:
            raise RuntimeError(f"job {job_id} failed: {last}")
        time.sleep(interval_sec)
    raise TimeoutError(f"job {job_id} timeout after {timeout_sec}s (last={last})")


def render(
    manifest_path: Path,
    job_template_path: Path,
    outbox_dir: Path,
    jobs_dir: Path,
    server: str,
    dry_run: bool = False,
    post_fn: Callable[..., dict] | None = None,
    get_fn: Callable[..., dict] | None = None,
    poll: bool = True,
    timeout_sec: int = 3600,
    secret: str | None = None,
) -> dict:
    manifest = load_json(manifest_path)
    template = load_json(job_template_path)
    outbox_dir.mkdir(parents=True, exist_ok=True)
    jobs_dir.mkdir(parents=True, exist_ok=True)
    results = []
    started = time.time()
    for item in manifest.get("items", []):
        ident = item["id"]
        job = build_job(item, template, str(outbox_dir))
        job_path = jobs_dir / f"{ident}.json"
        with job_path.open("w", encoding="utf-8") as fh:
            json.dump(job, fh, indent=2)
            fh.write("\n")
        entry = {
            "id": ident,
            "job_path": str(job_path),
            "output": str(outbox_dir / f"{ident}.mp4"),
            "status": "dry_run" if dry_run else "submitted",
        }
        if dry_run:
            results.append(entry)
            continue
        t0 = time.time()
        try:
            job_id = submit_job(server, job, post_fn=post_fn, secret=secret)
            entry["nexrender_uid"] = job_id
            if poll:
                poll_job(
                    server, job_id, get_fn=get_fn, timeout_sec=timeout_sec, secret=secret
                )
                entry["status"] = "success"
            else:
                entry["status"] = "queued"
        except Exception as exc:
            entry["status"] = "failed"
            entry["reason"] = str(exc)
        entry["duration_sec"] = round(time.time() - t0, 2)
        results.append(entry)
    summary = {
        "generated_at_elapsed_sec": round(time.time() - started, 2),
        "dry_run": dry_run,
        "results": results,
    }
    results_path = jobs_dir.parent / "results.json"
    with results_path.open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
        fh.write("\n")
    summary["results_path"] = str(results_path)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="F02_RENDER — jobs Nexrender")
    parser.add_argument("--paths", type=Path, default=DEFAULT_PATHS)
    parser.add_argument("--job-template", type=Path, default=DEFAULT_JOB)
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--outbox", type=Path, default=None)
    parser.add_argument("--jobs-dir", type=Path, default=None)
    parser.add_argument("--server", default=None)
    parser.add_argument("--secret", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-poll", action="store_true")
    parser.add_argument("--timeout", type=int, default=3600)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cfg = load_json(args.paths)
    vps = cfg["vps"]
    queue = Path(vps["queue_dir"])
    manifest = args.manifest or (queue / "manifest.json")
    outbox = args.outbox or Path(vps["outbox_dir"])
    jobs_dir = args.jobs_dir or (queue / "jobs")
    server = args.server or vps["nexrender_server"]
    secret = args.secret or os.environ.get(vps.get("nexrender_secret_env", "NEXRENDER_SECRET"))
    summary = render(
        manifest_path=manifest,
        job_template_path=args.job_template,
        outbox_dir=outbox,
        jobs_dir=jobs_dir,
        server=server,
        dry_run=args.dry_run,
        poll=not args.no_poll,
        timeout_sec=args.timeout,
        secret=secret,
    )
    failed = [r for r in summary["results"] if r.get("status") == "failed"]
    print(json.dumps({"jobs": len(summary["results"]), "failed": len(failed), "results": summary.get("results_path")}))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

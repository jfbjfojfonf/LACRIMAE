#!/usr/bin/env python3
"""Probe / decode / encode via FFmpeg. Pas de sœur OUT. Isolation OK."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Iterator


class FFmpegMissing(RuntimeError):
    pass


def require_ffmpeg() -> str:
    path = shutil.which("ffmpeg")
    if not path:
        raise FFmpegMissing("ffmpeg absent du PATH")
    return path


def require_ffprobe() -> str:
    path = shutil.which("ffprobe")
    if not path:
        raise FFmpegMissing("ffprobe absent du PATH")
    return path


def probe(path: Path) -> dict[str, Any]:
    ffprobe = require_ffprobe()
    cmd = [
        ffprobe,
        "-v",
        "error",
        "-show_format",
        "-show_streams",
        "-of",
        "json",
        str(path),
    ]
    raw = subprocess.check_output(cmd, timeout=30)
    data = json.loads(raw)
    video = None
    audio = None
    for stream in data.get("streams") or []:
        if stream.get("codec_type") == "video" and video is None:
            video = stream
        elif stream.get("codec_type") == "audio" and audio is None:
            audio = stream
    if video is None:
        raise RuntimeError(f"pas de flux video: {path}")
    width = int(video["width"])
    height = int(video["height"])
    fps = _parse_fps(video.get("avg_frame_rate") or video.get("r_frame_rate") or "0/1")
    duration = float(data.get("format", {}).get("duration") or video.get("duration") or 0.0)
    nb = video.get("nb_frames")
    frame_count = int(nb) if nb and str(nb).isdigit() else None
    codec = video.get("codec_name")
    return {
        "width": width,
        "height": height,
        "fps": fps,
        "duration_s": duration,
        "frame_count": frame_count,
        "video_codec": codec,
        "has_audio": audio is not None,
        "audio_codec": None if audio is None else audio.get("codec_name"),
    }


def _parse_fps(rate: str) -> float:
    if "/" in str(rate):
        a, b = str(rate).split("/", 1)
        den = float(b)
        if den == 0:
            return 0.0
        return float(a) / den
    return float(rate)


def iter_rgb_frames(path: Path, width: int, height: int) -> Iterator[bytes]:
    ffmpeg = require_ffmpeg()
    frame_size = width * height * 3
    cmd = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(path),
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "pipe:1",
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.stdout is not None
    try:
        while True:
            buf = proc.stdout.read(frame_size)
            if not buf:
                break
            if len(buf) != frame_size:
                break
            yield buf
    finally:
        proc.stdout.close()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


def encode_rgb_stream(
    out_path: Path,
    frames: Iterator[bytes],
    width: int,
    height: int,
    fps: float,
    audio_src: Path | None,
    has_audio: bool,
) -> None:
    ffmpeg = require_ffmpeg()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{width}x{height}",
        "-r",
        str(fps),
        "-i",
        "pipe:0",
    ]
    if has_audio and audio_src is not None:
        cmd.extend(["-i", str(audio_src), "-map", "0:v:0", "-map", "1:a:0", "-c:a", "copy", "-shortest"])
    else:
        cmd.extend(["-an"])
    cmd.extend(
        [
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(out_path),
        ]
    )
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.stdin is not None
    try:
        for frame in frames:
            proc.stdin.write(frame)
        proc.stdin.close()
        err = proc.stderr.read() if proc.stderr else b""
        code = proc.wait(timeout=120)
        if code != 0:
            raise RuntimeError(f"ffmpeg encode exit {code}: {err.decode('utf-8', 'replace')}")
    except Exception:
        proc.kill()
        raise

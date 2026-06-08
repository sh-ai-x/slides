#!/usr/bin/env python3
"""Speed up an MP4 while keeping audio/video synchronized."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import imageio_ffmpeg


def atempo_chain(speed: float) -> str:
    values: list[float] = []
    remaining = speed
    while remaining > 2.0:
        values.append(2.0)
        remaining /= 2.0
    while remaining < 0.5:
        values.append(0.5)
        remaining /= 0.5
    values.append(remaining)
    return ",".join(f"atempo={value:.6f}" for value in values)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", "-o", type=Path, required=True)
    parser.add_argument("--speed", type=float, default=1.3)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--crf", type=int, default=23)
    args = parser.parse_args()

    if args.speed <= 0:
        raise SystemExit("--speed must be positive")

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(args.input),
            "-filter_complex",
            f"[0:v]setpts=PTS/{args.speed},fps={args.fps}[v];[0:a]{atempo_chain(args.speed)}[a]",
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            str(args.crf),
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-movflags",
            "+faststart",
            str(args.output),
        ],
        check=True,
    )
    print(f"Wrote {args.output} at {args.speed}x")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

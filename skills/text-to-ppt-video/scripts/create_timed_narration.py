#!/usr/bin/env python3
"""Create narration audio aligned to timing JSON using TTS and ffmpeg."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import imageio_ffmpeg
from gtts import gTTS


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def duration_seconds(ffmpeg: str, media: Path) -> float:
    probe = subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-i",
            str(media),
            "-f",
            "null",
            "-",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    # imageio-ffmpeg does not bundle ffprobe. Parse ffmpeg's input duration line.
    for line in probe.stderr.splitlines():
        if "Duration:" not in line:
            continue
        value = line.split("Duration:", 1)[1].split(",", 1)[0].strip()
        hh, mm, ss = value.split(":")
        return int(hh) * 3600 + int(mm) * 60 + float(ss)
    raise RuntimeError(f"Could not parse duration for {media}")


def atempo_chain(ratio: float) -> str:
    values: list[float] = []
    remaining = ratio
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
    parser.add_argument("timing_json", type=Path)
    parser.add_argument("--output", "-o", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--engine", choices=["gtts", "say"], default="gtts")
    parser.add_argument("--voice", default="Yuna")
    parser.add_argument("--rate", default="205")
    parser.add_argument("--pace", type=float, default=1.08, help="Narration speed multiplier before padding to the target timing")
    args = parser.parse_args()

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    timing_doc = json.loads(args.timing_json.read_text(encoding="utf-8"))
    rows = timing_doc.get("timing", [])
    if not rows:
        raise SystemExit("No timing rows found")

    args.work_dir.mkdir(parents=True, exist_ok=True)
    segment_paths: list[Path] = []

    for index, row in enumerate(rows, start=1):
        script = str(row.get("script") or row.get("title") or "").strip()
        target = max(0.5, int(row["durationMs"]) / 1000.0)
        raw = args.work_dir / f"narration-{index:02d}.aiff"
        mp3 = args.work_dir / f"narration-{index:02d}.mp3"
        wav = args.work_dir / f"narration-{index:02d}.wav"
        fixed = args.work_dir / f"narration-{index:02d}-timed.wav"

        if args.engine == "gtts":
            gTTS(script, lang="ko").save(str(mp3))
            run([ffmpeg, "-y", "-i", str(mp3), "-ac", "1", "-ar", "44100", str(wav)])
        else:
            run(["say", "-v", args.voice, "-r", args.rate, "-o", str(raw), script])
            run([ffmpeg, "-y", "-i", str(raw), "-ac", "1", "-ar", "44100", str(wav)])

        source_duration = max(0.1, duration_seconds(ffmpeg, wav))
        ratio = (source_duration / target) * max(0.5, args.pace)
        filter_chain = f"{atempo_chain(ratio)},apad,atrim=0:{target:.3f}"
        run([ffmpeg, "-y", "-i", str(wav), "-af", filter_chain, "-ac", "1", "-ar", "44100", str(fixed)])
        segment_paths.append(fixed)

    concat_file = args.work_dir / "concat.txt"
    concat_file.write_text("".join(f"file '{path.resolve()}'\n" for path in segment_paths), encoding="utf-8")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c:a", "pcm_s16le", str(args.output)])
    print(f"Wrote timed narration {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

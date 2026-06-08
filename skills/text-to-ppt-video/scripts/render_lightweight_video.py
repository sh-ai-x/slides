#!/usr/bin/env python3
"""Render a lightweight motion-slide GIF from scene JSON."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


FORMATS = {
    "wide": (1280, 720),
    "square": (1080, 1080),
    "card": (1080, 1350),
}


def ease_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size, index=0)
            except Exception:
                continue
    return ImageFont.load_default()


def split_metric(metric: str) -> tuple[float, str, str, int]:
    text = str(metric).strip()
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)", text)
    if not match:
        return 0.0, text, "", 0
    value = float(match.group(1))
    decimals = len(match.group(1).split(".")[1]) if "." in match.group(1) else 0
    return value, text[: match.start(1)], text[match.end(1) :], decimals


def metric_label(value: float, prefix: str, suffix: str, decimals: int) -> str:
    body = f"{value:.{decimals}f}" if decimals else str(int(round(value)))
    return f"{prefix}{body}{suffix}"


def has_numeric_metric(scene: dict[str, Any]) -> bool:
    return bool(re.search(r"\d", str(scene.get("metric", ""))))


def should_render_chart(scene: dict[str, Any]) -> bool:
    if scene.get("chart") is False or scene.get("showChart") is False:
        return False
    if scene.get("chart") is True or scene.get("showChart") is True:
        return True
    return has_numeric_metric(scene)


def wrap(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.ImageFont, max_width: int, max_lines: int) -> list[str]:
    korean = bool(re.search(r"[\u3131-\ud7a3]", text))
    units = list(text) if korean else text.split()
    sep = "" if korean else " "
    lines: list[str] = []
    current = ""
    for unit in units:
        trial = f"{current}{sep if current else ''}{unit}"
        if draw.textlength(trial, font=face) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = unit
    if current:
        lines.append(current)
    return lines[:max_lines]


def draw_lines(draw: ImageDraw.ImageDraw, xy: tuple[int, int], lines: list[str], face: ImageFont.ImageFont, fill: str, gap: int) -> int:
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=face, fill=fill)
        box = draw.textbbox((x, y), line, font=face)
        y += box[3] - box[1] + gap
    return y


def estimate_speech_duration_ms(text: str, speed: str, min_scene_ms: int, max_scene_ms: int) -> int:
    clean = re.sub(r"\s+", " ", text.strip())
    if not clean:
        return min_scene_ms

    # Korean narration is more stable by character count than whitespace count.
    hangul_chars = len(re.findall(r"[\u3131-\ud7a3]", clean))
    latin_words = len(re.findall(r"[A-Za-z0-9]+", clean))
    punctuation_pauses = len(re.findall(r"[.!?。！？,，.]", clean))

    chars_per_second = {
        "slow": 5.8,
        "normal": 7.9,
        "fast": 9.6,
    }[speed]
    words_per_second = {
        "slow": 1.7,
        "normal": 2.45,
        "fast": 3.05,
    }[speed]

    seconds = 0.0
    if hangul_chars:
        seconds += hangul_chars / chars_per_second
    if latin_words:
        seconds += latin_words / words_per_second
    seconds += punctuation_pauses * 0.18
    seconds += 0.65  # visual settle time
    return int(max(min_scene_ms, min(max_scene_ms, seconds * 1000)))


def scene_duration(scene: dict[str, Any], speed: str, min_scene_ms: int, max_scene_ms: int) -> int:
    if "durationMs" in scene and scene.get("durationMs") not in (None, "", 0):
        return int(scene["durationMs"])
    if "duration" in scene and scene.get("duration") not in (None, "", 0):
        return int(scene["duration"])
    narration = str(scene.get("script") or scene.get("notes") or "")
    fallback = " ".join(str(scene.get(key, "")) for key in ("title", "body"))
    return estimate_speech_duration_ms(narration or fallback, speed, min_scene_ms, max_scene_ms)


def render_frame(scene: dict[str, Any], progress: float, size: tuple[int, int]) -> Image.Image:
    w, h = size
    image = Image.new("RGB", size, "#F7F8FA")
    draw = ImageDraw.Draw(image)

    ink = "#111827"
    muted = "#5F6673"
    accent = "#C0392B"
    track = "#E5E8EE"
    px = int(w * 0.075)
    py = int(h * 0.105)

    title_font = font(max(30, int(w * 0.043)))
    eyebrow_font = font(max(15, int(w * 0.016)))
    metric_font = font(max(68, int(w * 0.13)))
    body_font = font(max(19, int(w * 0.026)))
    footer_font = font(max(12, int(w * 0.014)))

    wipe = ease_out_cubic(min(progress / 0.28, 1))
    draw.rectangle((px, int(py * 0.68), px + int(w * 0.07 * wipe), int(py * 0.68) + max(4, int(h * 0.008))), fill=accent)

    entrance = ease_out_cubic(min(progress / 0.42, 1))
    offset = int((1 - entrance) * 30)
    draw.text((px, py + offset), str(scene.get("eyebrow", "")).upper(), font=eyebrow_font, fill=accent)

    title_lines = wrap(draw, str(scene.get("title", "")), title_font, int(w * 0.8), 2)
    y = draw_lines(draw, (px, int(py * 1.38) + offset), title_lines, title_font, ink, int(h * 0.018))

    metric_text = str(scene.get("metric", "")).strip()
    metric_y = y + int(h * 0.05)
    if metric_text and has_numeric_metric(scene):
        target, prefix, suffix, decimals = split_metric(metric_text)
        count = target * ease_out_cubic(min(progress / 0.82, 1))
        draw.text((px, metric_y), metric_label(count, prefix, suffix, decimals), font=metric_font, fill=accent)
        body_y = metric_y + int(h * 0.22)
    else:
        body_y = metric_y + int(h * 0.02)

    body_lines = wrap(draw, str(scene.get("body", "")), body_font, int(w * 0.72), 2)
    draw_lines(draw, (px, body_y), body_lines, body_font, muted, int(h * 0.014))

    value = float(scene.get("bar", 0) or 0)
    if value and should_render_chart(scene):
        bx = px
        by = int(h * 0.79)
        bw = int(w * 0.72)
        bh = max(10, int(h * 0.024))
        fill_w = int(bw * (value / 100.0) * ease_out_cubic(min(progress / 0.86, 1)))
        draw.text((bx, by - int(h * 0.047)), f"{int(value)}%", font=footer_font, fill=ink)
        draw.rectangle((bx, by, bx + bw, by + bh), fill=track)
        draw.rectangle((bx, by, bx + fill_w, by + bh), fill=accent)

    draw.text((px, h - int(h * 0.07)), "text-to-ppt-video / lightweight motion file", font=footer_font, fill=muted)
    page = scene.get("page")
    if page is not None:
        draw.text((w - int(w * 0.14), h - int(h * 0.07)), f"Slide {page}", font=footer_font, fill=muted)
    return image


def build_timing(deck: dict[str, Any], speed: str, min_scene_ms: int, max_scene_ms: int) -> list[dict[str, Any]]:
    timing: list[dict[str, Any]] = []
    cursor = 0
    for index, scene in enumerate(deck.get("scenes", []), start=1):
        duration = scene_duration(scene, speed, min_scene_ms, max_scene_ms)
        page = scene.get("page", index)
        timing.append(
            {
                "page": page,
                "startMs": cursor,
                "endMs": cursor + duration,
                "durationMs": duration,
                "title": scene.get("title", ""),
                "script": scene.get("script") or scene.get("notes") or "",
            }
        )
        cursor += duration
    return timing


def render(
    deck: dict[str, Any],
    output: Path,
    fmt: str,
    fps: int,
    speed: str,
    min_scene_ms: int,
    max_scene_ms: int,
    timing_output: Path | None = None,
) -> None:
    size = FORMATS[fmt]
    frame_ms = int(1000 / fps)
    frames: list[Image.Image] = []
    durations: list[int] = []
    timing = build_timing(deck, speed, min_scene_ms, max_scene_ms)

    for scene, timing_row in zip(deck.get("scenes", []), timing):
        duration = int(timing_row["durationMs"])
        count = max(8, math.ceil(duration / frame_ms))
        for i in range(count):
            frames.append(render_frame(scene, i / max(1, count - 1), size))
            durations.append(frame_ms)
        for _ in range(max(4, fps // 2)):
            frames.append(render_frame(scene, 1.0, size))
            durations.append(frame_ms)

    if not frames:
        raise SystemExit("No scenes found")

    output.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(output, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=True)
    print(f"Wrote {output} with {len(frames)} frames at {size[0]}x{size[1]}")
    if timing_output:
        timing_output.parent.mkdir(parents=True, exist_ok=True)
        timing_output.write_text(json.dumps({"title": deck.get("title", ""), "timing": timing}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote timing JSON {timing_output}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", "-o", type=Path, default=Path("lightweight-video.gif"))
    parser.add_argument("--format", choices=FORMATS.keys(), default="wide")
    parser.add_argument("--fps", type=int, default=10)
    parser.add_argument("--speech-speed", choices=["slow", "normal", "fast"], default="fast")
    parser.add_argument("--min-scene-ms", type=int, default=2400)
    parser.add_argument("--max-scene-ms", type=int, default=12000)
    parser.add_argument("--timing-output", type=Path, default=None, help="Write page/script timing JSON")
    args = parser.parse_args()

    deck = json.loads(args.input.read_text(encoding="utf-8"))
    min_scene_ms = max(1000, args.min_scene_ms)
    max_scene_ms = max(min_scene_ms, args.max_scene_ms)
    render(
        deck,
        args.output,
        args.format,
        max(4, min(20, args.fps)),
        args.speech_speed,
        min_scene_ms,
        max_scene_ms,
        args.timing_output,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

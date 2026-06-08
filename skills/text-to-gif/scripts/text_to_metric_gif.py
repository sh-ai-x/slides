#!/usr/bin/env python3
"""Render a metric-led animated GIF from scene JSON."""

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


def find_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size, index=0)
            except Exception:
                continue
    try:
        return ImageFont.truetype("Arial.ttf", size=size)
    except Exception:
        return ImageFont.load_default()


def split_metric(metric: str) -> tuple[float, str, str, int]:
    text = str(metric).strip()
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)", text)
    if not match:
        return 0.0, text, "", 0
    number = float(match.group(1))
    prefix = text[: match.start(1)]
    suffix = text[match.end(1) :]
    decimals = len(match.group(1).split(".")[1]) if "." in match.group(1) else 0
    return number, prefix, suffix, decimals


def format_metric(value: float, prefix: str, suffix: str, decimals: int) -> str:
    if decimals:
        body = f"{value:.{decimals}f}"
    else:
        body = f"{int(round(value))}"
    return f"{prefix}{body}{suffix}"


def has_numeric_metric(scene: dict[str, Any]) -> bool:
    return bool(re.search(r"\d", str(scene.get("metric", ""))))


def should_render_chart(scene: dict[str, Any]) -> bool:
    if scene.get("chart") is False or scene.get("showChart") is False:
        return False
    if scene.get("chart") is True or scene.get("showChart") is True:
        return True
    return has_numeric_metric(scene)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = list(text) if re.search(r"[\u3131-\ud7a3]", text) else text.split()
    lines: list[str] = []
    current = ""
    separator = "" if words and len(words[0]) == 1 else " "
    for word in words:
        trial = f"{current}{separator if current else ''}{word}"
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines[:3]


def draw_text_lines(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    lines: list[str],
    font: ImageFont.ImageFont,
    fill: str,
    line_gap: int,
) -> int:
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        bbox = draw.textbbox((x, y), line, font=font)
        y += (bbox[3] - bbox[1]) + line_gap
    return y


def render_scene_frame(
    scene: dict[str, Any],
    progress: float,
    size: tuple[int, int],
    palette: dict[str, str],
) -> Image.Image:
    width, height = size
    img = Image.new("RGB", size, palette["bg"])
    draw = ImageDraw.Draw(img)

    pad_x = int(width * 0.075)
    pad_y = int(height * 0.105)
    accent_h = max(4, int(height * 0.008))
    accent_w = int(width * 0.07 * ease_out_cubic(progress))

    title_font = find_font(max(28, int(width * 0.045)), bold=True)
    eyebrow_font = find_font(max(14, int(width * 0.016)), bold=True)
    metric_font = find_font(max(62, int(width * 0.13)), bold=True)
    body_font = find_font(max(18, int(width * 0.026)))
    footer_font = find_font(max(12, int(width * 0.014)))

    draw.rectangle((pad_x, int(pad_y * 0.7), pad_x + accent_w, int(pad_y * 0.7) + accent_h), fill=palette["accent"])

    fade = ease_out_cubic(min(progress / 0.45, 1.0))
    text_fill = palette["ink"] if fade > 0.2 else palette["muted"]

    draw.text((pad_x, pad_y), str(scene.get("eyebrow", "")).upper(), font=eyebrow_font, fill=palette["accent"])

    title_lines = wrap_text(draw, str(scene.get("title", "")), title_font, int(width * 0.78))
    y = draw_text_lines(draw, (pad_x, int(pad_y * 1.38)), title_lines, title_font, text_fill, int(height * 0.018))

    metric_y = y + int(height * 0.045)
    if has_numeric_metric(scene):
        metric_target, prefix, suffix, decimals = split_metric(str(scene.get("metric", "")))
        count_progress = ease_out_cubic(min(progress / 0.68, 1.0))
        metric_text = format_metric(metric_target * count_progress, prefix, suffix, decimals)
        draw.text((pad_x, metric_y), metric_text, font=metric_font, fill=palette["accent"])
        body_y = metric_y + int(height * 0.21)
    else:
        body_y = metric_y + int(height * 0.02)

    body_lines = wrap_text(draw, str(scene.get("body", "")), body_font, int(width * 0.72))
    draw_text_lines(draw, (pad_x, body_y), body_lines, body_font, palette["muted"], int(height * 0.014))

    bar_value = float(scene.get("bar", 0) or 0)
    if bar_value and should_render_chart(scene):
        track_x = pad_x
        track_y = int(height * 0.78)
        track_w = int(width * 0.72)
        track_h = max(10, int(height * 0.024))
        fill_w = int(track_w * (bar_value / 100.0) * ease_out_cubic(min(progress / 0.72, 1.0)))
        draw.rectangle((track_x, track_y, track_x + track_w, track_y + track_h), fill=palette["track"])
        draw.rectangle((track_x, track_y, track_x + fill_w, track_y + track_h), fill=palette["accent"])
        draw.text((track_x, track_y - int(height * 0.045)), f"{int(bar_value)}%", font=footer_font, fill=palette["ink"])

    footer = str(scene.get("footer", "Text to GIF / metric motion"))
    draw.text((pad_x, height - int(height * 0.07)), footer, font=footer_font, fill=palette["muted"])
    return img


def render_gif(deck: dict[str, Any], output: Path, fmt: str, fps: int) -> None:
    size = FORMATS[fmt]
    palette = {
        "bg": "#F7F8FA",
        "ink": "#111827",
        "muted": "#5F6673",
        "accent": "#C0392B",
        "track": "#E5E8EE",
        "sweep": "#FFFFFF",
    }

    frames: list[Image.Image] = []
    durations: list[int] = []
    frame_duration = int(1000 / fps)
    for scene in deck.get("scenes", []):
        scene_duration = int(scene.get("duration", 900))
        frame_count = max(4, math.ceil(scene_duration / frame_duration))
        for frame in range(frame_count):
            progress = frame / max(1, frame_count - 1)
            frames.append(render_scene_frame(scene, progress, size, palette))
            durations.append(frame_duration)
        for _ in range(max(1, fps // 3)):
            frames.append(render_scene_frame(scene, 1.0, size, palette))
            durations.append(frame_duration)

    if not frames:
        raise SystemExit("No scenes found in input JSON")

    output.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )
    print(f"Wrote {output} with {len(frames)} frames at {size[0]}x{size[1]}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Scene JSON")
    parser.add_argument("--output", "-o", type=Path, default=Path("text-to-gif.gif"))
    parser.add_argument("--format", choices=FORMATS.keys(), default="wide")
    parser.add_argument("--fps", type=int, default=12)
    args = parser.parse_args()

    deck = json.loads(args.input.read_text(encoding="utf-8"))
    render_gif(deck, args.output, args.format, max(4, min(args.fps, 20)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

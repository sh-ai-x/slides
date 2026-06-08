#!/usr/bin/env python3
"""Render a text-to-slides motion preview GIF from scene JSON."""

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
    number = float(match.group(1))
    prefix = text[: match.start(1)]
    suffix = text[match.end(1) :]
    decimals = len(match.group(1).split(".")[1]) if "." in match.group(1) else 0
    return number, prefix, suffix, decimals


def metric_text(value: float, prefix: str, suffix: str, decimals: int) -> str:
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


def is_dark_neon(scene: dict[str, Any]) -> bool:
    style = str(scene.get("style") or scene.get("theme") or "").lower().replace("-", "_")
    return style in {"dark_neon", "neon_dark", "creator_dark", "youtube_neon"}


def draw_neon_hub(draw: ImageDraw.ImageDraw, w: int, h: int, progress: float) -> None:
    cx = int(w * 0.73)
    cy = int(h * 0.44)
    growth = ease_out_cubic(min(progress / 0.72, 1))
    radius = int(min(w, h) * 0.17 * growth)
    for i in range(20):
        angle = math.tau * i / 20 + 0.2
        inner = int(radius * 0.18)
        outer = radius + int((i % 4) * radius * 0.22)
        x1 = cx + int(math.cos(angle) * inner)
        y1 = cy + int(math.sin(angle) * inner)
        x2 = cx + int(math.cos(angle) * outer)
        y2 = cy + int(math.sin(angle) * outer)
        fill = "#27F59B" if i % 2 else "#FF744F"
        draw.line((x1, y1, x2, y2), fill=fill, width=max(2, int(w * 0.003)))
    r = max(16, int(radius * 0.24))
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill="#FF744F", outline="#27F59B", width=max(2, int(w * 0.003)))
    icon_font = font(max(12, int(w * 0.014)))
    for ox, oy, label in [(-0.16, -0.15, "AI"), (0.17, -0.08, "{}"), (-0.10, 0.21, "API")]:
        alpha = ease_out_cubic(max(0, min((progress - 0.28) / 0.5, 1)))
        bx = cx + int(w * ox * alpha)
        by = cy + int(h * oy * alpha)
        bw = int(w * 0.07)
        bh = int(h * 0.06)
        draw.rounded_rectangle((bx, by, bx + bw, by + bh), radius=10, fill="#111719", outline="#24E89A", width=1)
        draw.text((bx + int(bw * 0.22), by + int(bh * 0.22)), label, font=icon_font, fill="#E9FFF6")


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


def render_frame(scene: dict[str, Any], progress: float, size: tuple[int, int]) -> Image.Image:
    w, h = size
    dark = is_dark_neon(scene)
    bg = "#030504" if dark else "#F7F8FA"
    ink = "#F8FAFC" if dark else "#111827"
    muted = "#A8B3BD" if dark else "#5F6673"
    accent = "#27F59B" if dark else "#C0392B"
    track = "#253036" if dark else "#E5E8EE"

    image = Image.new("RGB", size, bg)
    draw = ImageDraw.Draw(image)

    px = int(w * 0.075)
    py = int(h * 0.105)
    title_font = font(max(30, int(w * 0.043)))
    eyebrow_font = font(max(15, int(w * 0.016)))
    metric_font = font(max(68, int(w * 0.13)))
    body_font = font(max(19, int(w * 0.026)))
    footer_font = font(max(12, int(w * 0.014)))

    if dark:
        draw_neon_hub(draw, w, h, progress)

    wipe = ease_out_cubic(min(progress / 0.25, 1))
    draw.rectangle((px, int(py * 0.68), px + int(w * 0.07 * wipe), int(py * 0.68) + max(4, int(h * 0.008))), fill=accent)

    entrance = ease_out_cubic(min(progress / 0.42, 1))
    offset = int((1 - entrance) * 30)
    draw.text((px, py + offset), str(scene.get("eyebrow", "")).upper(), font=eyebrow_font, fill=accent)

    title_lines = wrap(draw, str(scene.get("title", "")), title_font, int(w * (0.56 if dark else 0.8)), 2)
    y = draw_lines(draw, (px, int(py * 1.38) + offset), title_lines, title_font, ink, int(h * 0.018))

    metric_y = y + int(h * 0.05)
    if has_numeric_metric(scene):
        target, prefix, suffix, decimals = split_metric(str(scene.get("metric", "")))
        count = target * ease_out_cubic(min(progress / 0.82, 1))
        draw.text((px, metric_y), metric_text(count, prefix, suffix, decimals), font=metric_font, fill=accent)
        body_y = metric_y + int(h * 0.22)
    else:
        body_y = metric_y + int(h * 0.02)

    body_lines = wrap(draw, str(scene.get("body", "")), body_font, int(w * (0.55 if dark else 0.72)), 2)
    draw_lines(draw, (px, body_y), body_lines, body_font, muted, int(h * 0.014))

    value = float(scene.get("bar", 0) or 0)
    if value and should_render_chart(scene):
        bx = px
        by = int(h * 0.79)
        bw = int(w * 0.72)
        bh = max(10, int(h * 0.024))
        fill_w = int(bw * (value / 100) * ease_out_cubic(min(progress / 0.86, 1)))
        draw.text((bx, by - int(h * 0.047)), f"{int(value)}%", font=footer_font, fill=ink)
        draw.rectangle((bx, by, bx + bw, by + bh), fill=track)
        draw.rectangle((bx, by, bx + fill_w, by + bh), fill=accent)

    footer = "dark-neon explainer / motion preview" if dark else "text-to-slides-video / motion preview"
    draw.text((px, h - int(h * 0.07)), footer, font=footer_font, fill=muted)
    return image


def render(deck: dict[str, Any], output: Path, fmt: str, fps: int) -> None:
    size = FORMATS[fmt]
    frame_ms = int(1000 / fps)
    frames: list[Image.Image] = []
    durations: list[int] = []

    for scene in deck.get("scenes", []):
        scene = {**({"style": deck.get("style")} if deck.get("style") else {}), **scene}
        duration = int(scene.get("duration", 2400))
        count = max(6, math.ceil(duration / frame_ms))
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", "-o", type=Path, default=Path("motion-preview.gif"))
    parser.add_argument("--format", choices=FORMATS.keys(), default="wide")
    parser.add_argument("--fps", type=int, default=10)
    args = parser.parse_args()

    deck = json.loads(args.input.read_text(encoding="utf-8"))
    render(deck, args.output, args.format, max(4, min(20, args.fps)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

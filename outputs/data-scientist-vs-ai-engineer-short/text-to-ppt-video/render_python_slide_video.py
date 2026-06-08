#!/usr/bin/env python3
"""Render a clean 16:9 slide video using only Python, Pillow, MoviePy, and ffmpeg."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

import numpy as np
from moviepy import AudioFileClip, VideoClip
from PIL import Image, ImageDraw, ImageFont


WIDTH = 1280
HEIGHT = 720
FPS = 30

BG = "#030504"
INK = "#F8FAFC"
MUTED = "#AAB4BE"
DIM = "#6F7A83"
NEON = "#27F59B"
ORANGE = "#FF744F"
PANEL = "#0B1113"
LINE = "#253239"


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


def ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


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


def text_block(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    lines: list[str],
    face: ImageFont.ImageFont,
    fill: str,
    gap: int,
) -> int:
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=face, fill=fill)
        box = draw.textbbox((x, y), line, font=face)
        y += box[3] - box[1] + gap
    return y


def blend_hex(a: str, b: str, t: float) -> str:
    t = max(0.0, min(1.0, t))
    av = tuple(int(a[i : i + 2], 16) for i in (1, 3, 5))
    bv = tuple(int(b[i : i + 2], 16) for i in (1, 3, 5))
    cv = tuple(round(av[i] + (bv[i] - av[i]) * t) for i in range(3))
    return f"#{cv[0]:02x}{cv[1]:02x}{cv[2]:02x}"


def draw_top_bar(draw: ImageDraw.ImageDraw, p: float) -> None:
    draw.rounded_rectangle((70, 46, 70 + int(120 * ease(p)), 53), radius=8, fill=NEON)
    draw.line((70, 656, 1210, 656), fill="#132124", width=3)
    draw.line((70, 656, 70 + int(1140 * p), 656), fill=NEON, width=3)


def draw_footer(draw: ImageDraw.ImageDraw, index: int, total: int) -> None:
    foot = font(17)
    draw.text((70, 675), "python slide video", font=foot, fill=DIM)
    draw.text((1160, 675), f"{index + 1} / {total}", font=foot, fill=DIM)


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], outline: str = LINE) -> None:
    draw.rounded_rectangle(box, radius=10, fill=PANEL, outline=outline, width=1)


def draw_comparison(draw: ImageDraw.ImageDraw, progress: float, left_title: str, right_title: str) -> None:
    x1, x2 = 120, 670
    y = 360
    w, h = 490, 170
    reveal = ease((progress - 0.18) / 0.42)
    panel(draw, (x1, y, x1 + w, y + h), NEON)
    panel(draw, (x2, y, x2 + w, y + h), ORANGE)
    title_font = font(34)
    body_font = font(25)
    draw.text((x1 + 30, y + 28), left_title, font=title_font, fill=NEON)
    draw.text((x2 + 30, y + 28), right_title, font=title_font, fill=ORANGE)
    draw.text((x1 + 30, y + 88), "분석과 예측", font=body_font, fill=INK)
    draw.text((x2 + 30, y + 88), "제품과 시스템 구현", font=body_font, fill=INK)
    draw.line((x1 + 30, y + 135, x1 + 30 + int((w - 60) * reveal), y + 135), fill=NEON, width=5)
    draw.line((x2 + 30, y + 135, x2 + 30 + int((w - 60) * reveal), y + 135), fill=ORANGE, width=5)


def draw_chip_row(draw: ImageDraw.ImageDraw, chips: list[str], y: int, progress: float) -> None:
    chip_font = font(24)
    x = 95
    for i, chip in enumerate(chips):
        shown = ease((progress - 0.22 - i * 0.08) / 0.34)
        if shown <= 0:
            continue
        w = int(draw.textlength(chip, font=chip_font)) + 46
        yy = y + int((1 - shown) * 18)
        draw.rounded_rectangle((x, yy, x + w, yy + 48), radius=24, fill=PANEL, outline=NEON, width=1)
        draw.text((x + 23, yy + 11), chip, font=chip_font, fill=INK)
        x += w + 16


def draw_role_table(draw: ImageDraw.ImageDraw, scene: dict[str, Any], progress: float) -> None:
    rows = (
        [
            ("데이터", "정형 데이터"),
            ("도구", "Excel, SQL"),
            ("결과", "인사이트, 예측 모델"),
        ]
        if scene["page"] == 3
        else [
            ("데이터", "텍스트, 이미지"),
            ("도구", "LLM, API"),
            ("결과", "챗봇, AI 에이전트"),
        ]
    )
    label_font = font(22)
    value_font = font(28)
    x, y, w = 95, 385, 620
    for i, (label, value) in enumerate(rows):
        shown = ease((progress - 0.18 - i * 0.1) / 0.35)
        yy = y + i * 68 + int((1 - shown) * 14)
        if shown <= 0:
            continue
        draw.rounded_rectangle((x, yy, x + w, yy + 52), radius=8, fill=PANEL, outline=LINE, width=1)
        draw.text((x + 22, yy + 15), label, font=label_font, fill=NEON if scene["page"] == 3 else ORANGE)
        draw.text((x + 150, yy + 10), value, font=value_font, fill=INK)


def draw_decision(draw: ImageDraw.ImageDraw, progress: float) -> None:
    items = [
        ("데이터에서 패턴을 찾고 싶은가?", "데이터 과학자", NEON),
        ("사람들이 쓰는 서비스를 만들고 싶은가?", "AI 엔지니어", ORANGE),
    ]
    title_font = font(25)
    role_font = font(38)
    for i, (q, role, color) in enumerate(items):
        shown = ease((progress - 0.18 - i * 0.12) / 0.42)
        x = 115 + i * 540
        y = 360 + int((1 - shown) * 24)
        panel(draw, (x, y, x + 475, y + 150), color)
        draw.text((x + 28, y + 28), q, font=title_font, fill=MUTED)
        draw.text((x + 28, y + 82), role, font=role_font, fill=color)
    shown = ease((progress - 0.55) / 0.35)
    if shown > 0:
        draw.text((354, 560 + int((1 - shown) * 18)), "두 역할은 상호보완적입니다", font=font(33), fill=INK)


def draw_scene(scene: dict[str, Any], progress: float, index: int, total: int) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    draw_top_bar(draw, progress)

    enter = ease(progress / 0.28)
    x = 90
    y = 96 + int((1 - enter) * 24)
    eyebrow_font = font(22)
    title_font = font(58 if scene["page"] != 1 else 68)
    body_font = font(30)

    draw.text((x, y), str(scene.get("eyebrow", "")).upper(), font=eyebrow_font, fill=NEON)
    if scene["page"] == 1:
        title_lines = ["데이터 과학자 vs", "AI 엔지니어"]
    else:
        title_lines = wrap(draw, str(scene.get("title", "")), title_font, 920, 2)
    y = text_block(draw, (x, y + 48), title_lines, title_font, INK, 10)
    body_lines = wrap(draw, str(scene.get("body", "")), body_font, 850, 2)
    text_block(draw, (x, y + 30), body_lines, body_font, MUTED, 8)

    page = int(scene["page"])
    if page in (1, 2):
        draw_comparison(draw, progress, "Data Scientist", "AI Engineer")
    elif page in (3, 4):
        draw_role_table(draw, scene, progress)
        draw_chip_row(draw, list(scene.get("chips", [])), 600, progress)
    elif page == 5:
        draw_decision(draw, progress)

    if page == 2:
        axis_font = font(26)
        p = ease((progress - 0.32) / 0.38)
        draw.line((170, 585, 1110, 585), fill=blend_hex(LINE, NEON, p), width=5)
        draw.ellipse((160, 575, 180, 595), fill=NEON)
        draw.ellipse((1100, 575, 1120, 595), fill=ORANGE)
        draw.text((155, 612), "분석", font=axis_font, fill=NEON)
        draw.text((1038, 612), "구현", font=axis_font, fill=ORANGE)

    draw_footer(draw, index, total)
    return image


def load_inputs(base: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    scenes_doc = json.loads((base / "scenes.json").read_text(encoding="utf-8"))
    timing_doc = json.loads((base / "timing.json").read_text(encoding="utf-8"))
    scenes = scenes_doc.get("scenes", [])
    timing = timing_doc.get("timing", [])
    if len(scenes) != len(timing):
        raise SystemExit(f"Scene/timing mismatch: {len(scenes)} vs {len(timing)}")
    return scenes, timing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audio", type=Path, required=True)
    parser.add_argument("--fps", type=int, default=FPS)
    args = parser.parse_args()

    scenes, timing = load_inputs(args.base)
    fps = max(8, min(30, args.fps))
    duration = max(float(row["endMs"]) for row in timing) / 1000.0

    def make_frame(t: float) -> np.ndarray:
        ms = t * 1000
        scene_index = 0
        for i, row in enumerate(timing):
            if float(row["startMs"]) <= ms < float(row["endMs"]):
                scene_index = i
                break
        row = timing[scene_index]
        local = (ms - float(row["startMs"])) / max(1.0, float(row["durationMs"]))
        image = draw_scene(scenes[scene_index], local, scene_index, len(scenes))
        return np.asarray(image)

    audio = AudioFileClip(str(args.audio))
    clip = VideoClip(make_frame, duration=min(duration, audio.duration)).with_audio(audio)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    clip.write_videofile(
        str(args.output),
        codec="libx264",
        audio_codec="aac",
        fps=fps,
        bitrate="1800k",
        audio_bitrate="128k",
        preset="medium",
        ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart"],
        logger=None,
    )
    clip.close()
    audio.close()
    print(f"Wrote {args.output} at {WIDTH}x{HEIGHT}, {fps}fps, {duration:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

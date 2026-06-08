---
name: text-to-gif
description: Turn text, scripts, outlines, Korean drafts, metric narratives, or slide/card-news plans into animated GIFs. Use when Codex needs to summarize text into a short looping GIF, create KPI or chart motion from text, make a lightweight social preview, export a motion proof without full video rendering, or test text-to-motion concepts with Python/Pillow when ffmpeg or Remotion is unavailable.
---

# Text to GIF

## Overview

Create a short animated GIF from text. Use metric-led motion only when the source includes useful numbers, ROI claims, charts, comparisons, or KPI tables.

## Workflow

1. Summarize the input into 3-5 GIF scenes.
2. Choose output format:
   - `wide`: 1280x720, default for presentation/video previews.
   - `square`: 1080x1080 for social feeds.
   - `card`: 1080x1350 for card-news style.
3. Build compact scene JSON with title, body, optional metric/bar only when numerically useful, and duration.
4. Render with `scripts/text_to_metric_gif.py` using Python/Pillow.
5. Verify the GIF exists, is non-empty, opens as an animated image, and has multiple frames.

## Default Motion

Read `references/gif-motion.md` whenever numbers or charts exist. Default effects:

- count-up for numeric metrics
- left-to-right bar fill for percentages
- panel fade/slide entrance
- subtle progress line or footer marker
- looping final hold so the GIF is readable

Keep final text values visible in later frames; the GIF must still make sense if viewed as a thumbnail.

Do not add count-up text, gauges, or bar motion to conceptual scenes with no useful number. If a scene has no numeric metric, render title/body entrance motion only.

## Token Optimization Rules

- Reuse the same compact scenes JSON used for PPT, slides, or video variants.
- Save the GIF and source JSON as files; report paths and frame/dimension metadata instead of pasting large JSON.
- Keep preview FPS low (`8-12`) unless the user asks for smoother motion.

## Tool Choice

Use Python/Pillow as the default because it is deterministic and works without ffmpeg. Use Remotion plus ffmpeg only when the project already has that toolchain or the user asks for higher-fidelity motion/video.

If `ffmpeg` is unavailable, say so and use the Pillow path instead of blocking.

## Relationship To Other Skills

- Pair with `text-to-slides` when the user also wants responsive HTML or Remotion-ready slides.
- Pair with `text-to-ppt` when the user also wants an editable deck.
- Use one shared story spine when producing PPTX, HTML slides, and GIF from the same text.

## Quick Start

```bash
python scripts/text_to_metric_gif.py scenes.json --output output.gif --format wide
```

`scenes.json` can contain:

```json
{
  "title": "LLM Wiki ROI",
  "scenes": [
    {
      "eyebrow": "Opening Metric",
      "title": "LLM Wiki lowers knowledge-management cost",
      "metric": "95%",
      "body": "Token usage reduction versus raw document loading",
      "bar": 95,
      "duration": 900
    }
  ]
}
```

## Verification Checklist

- GIF file exists and is non-empty.
- GIF has at least 8 frames.
- Key text and final metric values are readable.
- Dimensions match the selected format.
- No single frame relies on decorative motion to explain the message.

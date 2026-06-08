---
name: text-to-slides-video
description: Turn text, scripts, outlines, Korean drafts, metric narratives, or slide plans into Remotion motion-slide video assets. Use when Codex needs to summarize text into a video-ready slide spine, create Remotion scenes, add chart motion only when metrics need it, produce a GIF motion preview for proof, or prepare a path from text-to-slides HTML into MP4/WebM/GIF.
---

# Text to Slides Video

## Overview

Create video-ready motion slides from text. Inherit the content and layout discipline of `text-to-slides`: shared story spine, Remotion metadata, and chart motion only for meaningful metrics.

## Workflow

1. Summarize the input into a concise story spine.
2. Create 3-7 video scenes from the spine.
3. Use `remotion-video` as the final route when motion is requested.
   - `gif-preview`: deterministic animated GIF proof only.
   - `html-motion`: responsive HTML handoff only, not the final motion renderer.
4. Apply chart motion only to metrics, bars, KPI tables, and comparisons that are important to the message.
5. Verify the output by checking dimensions, frame count or duration, readability, and final metric values.

## Required Text-to-Slides Carryover

When building a video scene deck, reuse the same rules from `../text-to-slides`:

- Use one shared story spine for PPT, HTML, GIF, and video variants.
- Preserve Remotion metadata such as `data-duration`, `data-remotion-width`, `data-remotion-height`, and `data-fps`.
- Keep one logical source slide as one Remotion scene. Do not create extra slide pages to simulate animation states.
- Use responsive web layout for HTML previews; do not hardcode fixed `1920px` browser layouts.
- Add chart motion only when numbers or charts need visual emphasis.
- Keep final values readable without animation.

Read these references as needed:

- `../text-to-slides/references/responsive-html.md`
- `../text-to-slides/references/chart-motion.md`
- `references/video-pipeline.md`

## Default Motion

Use the same visual grammar for all routes:

- metric count-up only when `metric` contains a meaningful number
- slow bar fill only when `bar` represents a useful numeric value
- panel fade/slide entrance
- row or claim stagger
- final hold on each scene
- `prefers-reduced-motion` for HTML previews

Do not invent gauges, bars, or count-up metrics for conceptual slides. If `metric` is empty and `chart/showChart` is not explicitly true, use text entrance motion only.

Motion belongs inside the scene timeline: use Remotion `<Sequence>`, `interpolate()`, `spring()`, opacity, transform, and `scaleX`. Do not solve motion by generating multiple slides for the same source page.

## Token Optimization Rules

- Create one compact scenes JSON and reuse it for HTML, GIF preview, Remotion props, and MP4/WebM rendering.
- Save scene JSON, timing JSON, captions, and render props as files; summarize paths and metadata in chat.
- Prefer GIF for visual proof images. PNG is allowed only for internal frame sequences used to encode video.
- Keep FPS low for previews (`8-12`) and raise it only for final Remotion/MP4 output when requested.

## Tool Choice

Default to Remotion for real motion output. Use `gif-preview` only for testing, quick proof, or when Remotion is unavailable.

If Remotion or ffmpeg is missing, do not pretend the final video exists. Produce the GIF preview only as proof, state what is missing, and leave the scene JSON/Remotion props ready for rendering.

## Quick Start

```bash
python scripts/render_motion_preview.py scenes.json --output preview.gif --format wide --fps 10
```

Scene JSON:

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
      "duration": 2400
    }
  ]
}
```

## Verification Checklist

- scene JSON is valid
- one logical slide maps to one scene; duplicate pages are not used for animation
- output GIF/video exists and is non-empty
- preview has multiple frames or video has non-zero duration
- dimensions match selected format
- key text and final metric values are readable
- chart motion appears only for useful numeric scenes
- if browser/ffmpeg/Remotion verification is blocked, report the limitation

---
name: text-to-ppt-video
description: "Turn text, markdown, presentation scripts, Korean drafts, slide outlines, or narration into synchronized Remotion motion-slide video files using ffmpeg + Whisper + Remotion. Use when Codex must create MP4/WebM video from text with page-to-script timing JSON, captions, narrated slide timing, chart motion, or token-efficient local media processing."
---

# Text to PPT Video

## Overview

Create a synchronized video-style file from text. Despite the historical name, this skill outputs a video asset first, with `ffmpeg + Whisper` as the timing layer and Remotion as the motion renderer.

Use `text-to-ppt` for editable PPTX. Use this skill when the user asks for a video file, motion preview, MP4, WebM, GIF, animated slides, or text-to-video.

## Required Toolchain

1. `ffmpeg` capability: use system `ffmpeg` when available, otherwise Python `imageio-ffmpeg`.
2. `Whisper`: use CLI `whisper` when available, otherwise Python `openai-whisper`.
3. Remotion: render motion slides from scene JSON and timing JSON.
4. `moviepy` / `imageio-ffmpeg`: fallback encoder only when Remotion is unavailable or for quick local diagnostics.

If any required tool is missing, run `scripts/check_toolchain.sh`, report the missing item, and stop before pretending the final MP4/WebM exists. GIF is only a quick proof artifact, not the final output for this skill.

## Workflow

1. Convert source text into compact `scenes.json`; preserve one object per slide/page.
2. Put each page's full narration in `script`; keep slide text short.
3. Generate or ingest narration audio.
4. Normalize narration with ffmpeg.
5. Transcribe normalized audio with Whisper.
6. Build `timing.json` from Whisper segments and `scenes.json` using `scripts/build_video_timing.py`.
7. Render motion slides in Remotion using the timing JSON:
   - one source page equals one Remotion scene/sequence
   - do not duplicate logical slides to fake animation
   - motion happens inside a scene with frame interpolation, springs, opacity, transforms, and scale
   - `startMs`, `endMs`, and `durationMs` come from timing JSON
   - captions come from Whisper segments when requested
8. Encode final MP4/WebM with Remotion/ffmpeg and verify metadata.
9. Unless the user asks for slower narration, create the delivery MP4 at `1.3x` playback speed with `scripts/speed_up_video.py`; keep the original Remotion render as an intermediate/source master.
10. Use chart motion only when the script has metrics or ROI claims that should be visible on the slide:
   - metric count-up
   - slow bar fill
   - no separate white sweep overlay on gauges
   - panel/text entrance
   - final hold for readability
11. If there is no useful number for a slide, do not create a metric, gauge, or animated bar. Use text entrance motion only.

For exact commands and branch choices, read `references/pipeline.md`.

## Relationship To Other Skills

- `text-to-ppt`: editable PPTX and Google Slides upload.
- `text-to-slides`: responsive HTML slides and Remotion-ready web scenes.
- `text-to-slides-video`: video scene planning and motion-slide previews.
- `text-to-gif`: compact GIFs for metric highlights.

Use one shared story spine when the user asks for multiple formats.

## Scene Schema

Preferred schema is page-to-script 1:1:

```json
{
  "page": 1,
  "title": "Slide title",
  "metric": "95%",
  "body": "On-slide summary",
  "script": "Full narration for this page"
}
```

Timing JSON shape:

```json
{
  "page": 1,
  "startMs": 0,
  "endMs": 6200,
  "durationMs": 6200,
  "title": "Slide title",
  "script": "Full narration for this page"
}
```

## Token Optimization Rules

- Create one compact `scenes.json` and reuse it for GIF preview, timing, frame rendering, Remotion props, and final video.
- Keep visible slide text short; store full narration only in `script` fields.
- Do not paste full Whisper transcripts into the chat unless the user asks.
- Save transcripts, scene plans, captions, timing JSON, and render props as files.
- Use local scripts to transform large JSON artifacts.
- Use Whisper `tiny` for timing verification unless the user asks for high-accuracy captions.
- Use low FPS (`8-12`) and moderate bitrate for lightweight files; raise quality only when the user asks.
- Default delivery pace is `1.3x`; use ffmpeg `setpts=PTS/1.3` plus `atempo=1.3` after Remotion render so audio and scene timing stay synchronized.
- For visual proof images, save GIF by default. PNG frame sequences are allowed only as internal video-encoding intermediates.
- Load only the relevant reference file for the selected renderer:
  - Remotion: read Remotion best-practices and `references/pipeline.md`.
- Summarize verification outputs instead of pasting full ffprobe or transcript JSON.

## Verification Checklist

- output file exists and is non-empty
- ffprobe reports non-zero duration
- dimensions match requested format
- each source slide/page has a corresponding scene unless the user asks for a compressed teaser
- no extra duplicate pages exist solely to simulate motion
- each timing row has `page`, `startMs`, `endMs`, `durationMs`, and `script`
- scene transitions follow Whisper-derived timing
- chart motion is visible only when the slide contains useful metrics
- gauges use one filling bar only, no separate moving white overlay
- representative frame is visually readable

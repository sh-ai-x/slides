# Lightweight Preview Output

This reference is only for quick GIF previews. The final output for `text-to-ppt-video` must use `ffmpeg + Whisper + Remotion`.

## Formats

- `wide`: 1280x720
- `square`: 1080x1080
- `card`: 1080x1350

## Timing Defaults

- 10 fps for GIF preview
- auto duration from each scene's `script` or `notes` only when Whisper timing is not available
- fallback 2400ms minimum per scene
- 500ms+ final hold
- bar fill through 85% of the scene only when a useful metric/bar exists
- no separate white sweep overlay on gauges

## Speech Speed

Use:

```bash
python scripts/render_lightweight_video.py scenes.json --output preview.gif --speech-speed fast --min-scene-ms 2200 --max-scene-ms 10000
```

Supported speeds:

- `slow`: slower presenter or dense technical narration
- `normal`: careful Korean/English presentation pace
- `fast`: default faster presentation pace

If a scene includes explicit `durationMs`, that value overrides automatic speech timing. Legacy `duration` is also accepted.
Use `--max-scene-ms` to prevent long scripts from being clipped too aggressively, or `--min-scene-ms` to keep short slides readable.

## Page-To-Script JSON

Use one scene object per source slide/page:

```json
{
  "page": 1,
  "title": "Slide title",
  "metric": "95%",
  "body": "On-slide summary",
  "script": "Full narration for this page",
  "durationMs": 5200
}
```

Render with timing export:

```bash
python scripts/render_lightweight_video.py scenes.json --output preview.gif --speech-speed fast --min-scene-ms 2200 --max-scene-ms 10000 --timing-output timing.json
```

The preview timing JSON includes `page`, `startMs`, `endMs`, `durationMs`, `title`, and `script`. For final MP4/WebM, prefer Whisper-derived timing from `scripts/build_video_timing.py`.

Only include `metric` and `bar` when the number should appear on-screen. Conceptual scenes should omit both and use text entrance motion only.

## Scene Coverage

If the source script already labels slides or pages, preserve that count by default. For example, a 7-slide script should become 7 scenes unless the user asks for a shorter teaser.

## File Size

GIF is convenient but can grow quickly. Keep GIF previews short and use 1280x720 unless the user requests a larger file. Do not use GIF as the final delivery for this skill unless the user explicitly asks for GIF.

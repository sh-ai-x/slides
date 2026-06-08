# Text to Slides Video Pipeline

## Routes

### remotion-video

Use this route for real motion output:

1. Convert each logical slide to one React scene component.
2. Use `<Sequence>` per logical scene, not per animation state.
3. Map `duration` milliseconds to frames.
4. Animate text with opacity/transform, not duplicate pages.
5. Map counters to `interpolate(frame, ...)` only when `metric` is meaningful.
6. Map bars to `scaleX(...)` only when `bar` is meaningful.
7. Render MP4/WebM through Remotion.

### gif-preview

Use this route for deterministic testing without ffmpeg:

```bash
python scripts/render_motion_preview.py scenes.json --output preview.gif --format wide --fps 10
```

This route produces an animated GIF proof of motion and story timing. It is not a final high-fidelity video master.

### html-motion

Use `text-to-slides` rules to build responsive HTML:

- one `.slide` per scene
- `data-duration` per scene
- `data-count-to`, `data-prefix`, `data-suffix` for counters
- `--value` for bars
- responsive CSS plus Remotion metadata

## Shared Scene Schema

```json
{
  "title": "Deck/video title",
  "source": "user-provided script",
  "scenes": [
    {
      "eyebrow": "Short section label",
      "title": "One message",
      "metric": "95%",
      "body": "Readable support sentence",
      "bar": 95,
      "duration": 2400
    }
  ]
}
```

## Motion Timing

- 0-25%: eyebrow and title enter
- 20-85%: metric count-up and bar fill only when those fields are meaningful
- 85-100%: final hold
- add 500-700ms hold between scenes when exporting GIF
- Do not add a separate white sweep rectangle over the gauge; it reads as a second moving chart. Animate only the main filled bar unless the user explicitly asks for a shine effect.
- Do not duplicate slides/pages to create animation. Motion is always inside the Remotion scene timeline.

## Fallback Policy

- If ffmpeg is unavailable: produce GIF preview only.
- If Remotion is unavailable: produce responsive HTML or GIF preview only and state that final motion video is blocked.
- If browser rendering is blocked: validate scene JSON and generated file metadata.

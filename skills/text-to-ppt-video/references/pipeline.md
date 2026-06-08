# Text to PPT Video Pipeline

Use this pipeline when the final deliverable is MP4/WebM. The required stack is:

- ffmpeg capability through system `ffmpeg` or Python `imageio-ffmpeg`
- Whisper through CLI `whisper` or Python `openai-whisper`
- Remotion for the default motion renderer and MP4/WebM render path
- Python `moviepy` only for fallback muxing/diagnostics when Remotion is unavailable

GIF output is only a quick visual proof. Do not treat GIF as the final result for this skill.

Motion must be authored inside Remotion scenes. Do not create extra slide pages or duplicate logical scenes to simulate animation states.

## Token-Efficient File Contract

Keep large artifacts on disk and pass file paths between tools:

- `scenes.json`: compact page-to-script scene plan
- `audio.wav`: ffmpeg-normalized narration
- `whisper.json`: Whisper segments
- `timing.json`: one row per page with `startMs`, `endMs`, `durationMs`, `script`
- `render-props.json`: renderer input combining scenes and timing
- `render-master.mp4`: normal-speed Remotion source master
- `final.mp4` or `final.webm`: delivery video, default `1.3x`

Codex should inspect summaries, row counts, durations, and representative snippets, not paste entire transcripts.

## 1. Tool Check

```bash
scripts/check_toolchain.sh
```

Require Remotion and ffmpeg for final video rendering. Python packages `moviepy`, `imageio-ffmpeg`, `openai-whisper`, and `gTTS` support narration, Whisper timing, and fallback diagnostics.

## 2. Scene Plan

Create one scene per slide/page. A scene is a logical slide, not a frame of animation:

```json
{
  "title": "Deck title",
  "scenes": [
    {
      "page": 1,
      "title": "Slide title",
      "metric": "95%",
      "body": "Short on-slide message",
      "bar": 95,
      "script": "Full narration for page 1."
    }
  ]
}
```

Do not put long narration in visible slide text. Keep it in `script`.
Only include `metric` and `bar` when the number should appear on-screen. Conceptual scenes should omit both and use text entrance motion only.

## 3. Audio Normalize With ffmpeg

For supplied narration:

```bash
python scripts/create_timed_narration.py out/timing.json --output out/audio.wav --work-dir out/narration-work --engine gtts --pace 1.08
```

For supplied narration, normalize with system ffmpeg or `imageio-ffmpeg`.

Inspect duration:

```bash
python -c 'from moviepy import AudioFileClip; c=AudioFileClip("out/audio.wav"); print(c.duration); c.close()'
```

## 4. Whisper Timing

```bash
python -m whisper out/audio.wav --model tiny --language ko --output_format json --output_dir out
```

Use `tiny` for token- and runtime-efficient timing verification. Use a larger model only when accurate captions are requested.

## 5. Build Page Timing JSON

If source narration already exists, run Whisper first and then build timing:

```bash
python scripts/build_video_timing.py scenes.json out/audio.json --output out/timing.json --hold-ms 350 --min-scene-ms 1200
```

If a timing JSON already exists, use it as the source of truth and do not regenerate it unless the audio changed.

The script maps Whisper segment timing to the 1:1 page/script scene plan. It outputs:

```json
{
  "page": 1,
  "startMs": 0,
  "endMs": 6200,
  "durationMs": 6200,
  "title": "Slide title",
  "script": "Full narration for page 1.",
  "segmentStart": 0,
  "segmentEnd": 3
}
```

## 6A. Remotion Route

Use Remotion for final motion output:

- one logical scene per `<Sequence>`
- `durationInFrames = Math.ceil(durationMs / 1000 * fps)`
- `from` frame comes from cumulative timing
- metric count-up uses `interpolate()` only when `metric` is present
- gauge uses one `scaleX` bar fill only when `bar` is present
- text/panel entrances use opacity and transform
- narration audio is one global audio track
- captions use Whisper segment timings

Recommended render command:

```bash
npx remotion render src/index.ts TextToPptVideo out/render-master.mp4 --props=out/render-props.json
python scripts/speed_up_video.py out/render-master.mp4 --output out/final.mp4 --speed 1.3 --fps 30
```

Use the `1.3x` file as the final delivery unless the user asks for a slower lecture-style version. This preserves Remotion-authored scene motion while shortening the overall runtime.

## 6B. Python Diagnostic Route

Use this route only when Remotion is unavailable and the user accepts a local fallback or diagnostic MP4:

```bash
python scripts/render_video_frames.py scenes.json out/timing.json --output-dir out/frames --format wide --fps 10
python scripts/png_frames_to_mp4.py out/frames --output out/video.mp4 --fps 10
python scripts/mux_audio_to_mp4.py out/video.mp4 out/audio.wav --output out/final.mp4 --fps 10
```

This route uses PNG frame sequences internally only for encoding. Do not deliver those PNGs as final image artifacts.

## 7. Encode And Verify

Verify:

```bash
python -c 'from moviepy import VideoFileClip; c=VideoFileClip("out/final.mp4"); print(c.duration, c.fps, c.size, c.audio is not None); c.close()'
```

Expected default delivery pace is about `original duration / 1.3`.

## Fallback

If Remotion is not installed, stop after producing `scenes.json`, `timing.json`, and optional GIF preview unless the user explicitly approves the Python diagnostic route. Use `scripts/render_lightweight_video.py` only as a local preview, not as the skill's final video path.

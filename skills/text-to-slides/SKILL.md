---
name: text-to-slides
description: Turn text, scripts, outlines, Korean drafts, or article excerpts into responsive HTML-based slides or card-news frames that can be animated in Remotion. Use when Codex needs to summarize text into slide/card structure, output a self-contained web-responsive HTML file, add CSS/JS motion cues only when charts or metrics are useful, prepare 16:9 slides or 4:5 card-news layouts, create Remotion-friendly scene data, or produce web slides instead of a PPTX.
---

# Text to Slides

## Overview

Create HTML slide or card-news outputs from text. Prefer this over PPTX when the user mentions HTML, Remotion, animation, video effects, card news, social posts, or motion-ready slides.

## Workflow

1. Summarize the source into a slide spine.
2. Choose format:
   - `slides`: 1920x1080, 16:9 presentation/video.
   - `card-news`: 1080x1350, vertical social carousel.
3. Build one self-contained HTML file with inline CSS and minimal JS.
4. Put scene data in `const slides = [...]` or HTML `data-*` attributes so it can be ported to Remotion.
5. Add motion cues with CSS classes only when they carry meaning: `fade-up`, `count-up`, `bar-fill`, `stagger`, `row-reveal`, `wipe`.
6. Make the HTML responsive for web viewing while preserving Remotion dimensions in `data-remotion-width` and `data-remotion-height`.
7. Verify the HTML renders without overflow at desktop and mobile viewports.

If the user also needs editable PPT or Google Slides upload, pair this with the project `text-to-ppt` skill. Use one shared story spine, then export both PPTX and HTML from the same content plan.

## Output Routing

- Use `text-to-ppt` for editable `.pptx`, PowerPoint, Google Slides upload, or manual slide editing.
- Use `text-to-slides` for HTML slides, Remotion animation, video production, card news, or web previews.
- If the user asks for both, create the summarized slide plan once and produce both outputs.

## Style Defaults

- Use consulting-style hierarchy for business scripts.
- Lead with numbers and quantified claims when available.
- Use one accent color, default red `#c0392b`.
- Avoid emoji, gradients, decorative cards, and ornamental icons unless the user asks for a social style.
- Keep every slide readable at thumbnail size.
- Include speaker notes in `data-notes` or hidden `<aside>` blocks when useful.

## Default Chart Motion

Read `references/chart-motion.md` only when the output includes metrics, charts, KPI tables, bars, comparisons, or numeric claims that should be visually emphasized. Do not invent chart bars or gauges for conceptual slides with no meaningful number. Default behavior:

- Animate large metrics with count-up when the slide enters the viewport.
- Animate bar charts with left-to-right fill only; do not add a separate sweep highlight unless the user asks.
- Animate comparison panels from left/right when they appear as opposing options.
- Animate summary table rows with a staggered reveal.
- Include `prefers-reduced-motion: reduce` so motion can be disabled.
- Keep the motion decorative; final values must remain readable without JavaScript.
- Preserve data in attributes such as `data-count-to`, `data-suffix`, and CSS variables such as `--value` for Remotion mapping.

## Token Optimization Rules

- Build one compact story-spine JSON first and reuse it for HTML, PPTX, GIF, and video variants.
- Keep slide text short; put full narration in `data-notes` or external JSON instead of duplicating it in visible HTML.
- Use local scripts and references instead of pasting generated HTML, transcripts, or long scene arrays back into chat.
- When exporting a visual proof image, save GIF by default. PNG is allowed only for internal render frames or when the user explicitly asks for a still image.

## Responsive HTML Requirements

Read `references/responsive-html.md` when producing HTML. The defaults are:

- Do not hardcode `.deck { width: 1920px }` or `.slide { width: 1920px; height: 1080px }` for web output.
- Use `width: min(100%, 1920px)` on the deck and `aspect-ratio: 16 / 9` on slide mode.
- Use `clamp()` for typography, padding, gaps, bars, and table spacing.
- Add a mobile breakpoint around `760px`; stack grids into one column and let slides become `min-height: 100svh`.
- Keep Remotion export metadata as attributes, e.g. `data-remotion-width="1920" data-remotion-height="1080"`.
- Avoid horizontal overflow and avoid text that only fits at the 1920px design size.

## Remotion Handoff

HTML outputs should be easy to convert into Remotion:

- Keep each slide as a `.slide` section.
- Store timing in `data-duration`.
- Use CSS custom properties for chart values, e.g. `--value: 95`.
- Use `data-count-to`, `data-prefix`, and `data-suffix` for count-up values.
- Avoid runtime-only browser APIs that Remotion cannot reproduce.
- Prefer transform and opacity animations.
- Use deterministic layout dimensions.

For Remotion implementation, translate each `.slide` into a React component, replace CSS keyframes with `interpolate()`, `spring()`, and `<Sequence>`, map `data-duration` to frames, map `.bar` `--value` to animated width/scale, and map `.counter` `data-count-to` to frame-based number interpolation.

## Output Checklist

- HTML file exists and opens standalone.
- Slide/card count matches the source plan.
- No visible text overflow at desktop and mobile viewport sizes.
- No fixed 1920px deck/slide CSS remains unless the user explicitly asks for a fixed render-only frame.
- Numeric claims are prominent only when the source makes them important.
- Chart and metric motion cues are present only when charts or numbers are useful to the message.
- `prefers-reduced-motion` fallback exists.
- Speaker notes or narration hints are preserved.
- Browser verification was attempted; if blocked by sandbox or browser permissions, state that clearly.

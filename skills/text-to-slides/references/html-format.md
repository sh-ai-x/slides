# HTML Slide Format

Use this structure for each output:

```html
<main class="deck" data-format="slides">
  <section class="slide" data-duration="7" data-notes="Narration text">
    <p class="eyebrow">SECTION</p>
    <h1>Insight title</h1>
    <div class="metric">95%</div>
  </section>
</main>
```

Animation classes:

- `reveal`: fade and rise on entry.
- `stagger`: sequential child reveal.
- `bar-fill`: animate a horizontal metric bar.
- `bar-fill`: animate a meaningful numeric bar with one filled element. Do not add a separate sweep overlay unless the user explicitly asks.
- `counter`: numeric emphasis for Remotion count-up conversion.
- `counter-inline`: count-up inside table or paragraph text.
- `row-reveal`: staggered table/list row reveal.
- `wipe`: section transition line.

Sizing:

- Slides: use `data-remotion-width="1920"` and `data-remotion-height="1080"` for Remotion metadata, but use responsive CSS for browser layout.
- Card news: use `data-remotion-width="1080"` and `data-remotion-height="1350"` for Remotion metadata, but use responsive CSS for browser layout.

Do not make the web-facing deck depend on fixed pixel dimensions. For browser viewing, use `width: min(100%, targetWidth)` and `aspect-ratio`.

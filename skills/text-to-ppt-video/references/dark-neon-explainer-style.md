# Dark Neon Explainer Style

Use this style for AI, developer-tool, automation, or technical explainer videos when the user asks to adopt a YouTube-style tutorial look or when the topic benefits from a strong hook. Reference observed: <https://www.youtube.com/watch?v=2oOXHWGn_Cw>.

## Visual System

- Background: near-black stage (`#030504`, `#070807`) with subtle vignette. Avoid purple/blue gradient fields.
- Typography: oversized bold Korean hook text, white, left-heavy, max 2-3 lines. Use tight but non-overlapping line height.
- Accent: neon green (`#27f59b`) for the key turn or conclusion; warm orange/coral (`#ff744f`) for a central spark, pointer, or warning state.
- Composition: big hook or claim on the left; one symbolic system visual on the right or center-right.
- Labels: small context label such as tool, chapter, or source near the top edge.
- Supporting text: one short sentence or 2-3 compact chips. Do not fill the frame with paragraphs.

## Motifs

- Central hub: glowing starburst, radial rays, node graph, orbiting tool icons, or simple topology map.
- Progress/KPI scenes: one clean circular progress ring or one bar only when a real metric exists.
- Process scenes: thin timeline with 3-4 nodes, checklist rows, or layered context blocks.
- Tool scenes: icons may float near the hub with glow; keep them secondary to the headline.

## Remotion Motion

- Animate inside a single scene with `<Sequence>`, `interpolate()`, `spring()`, opacity, transform, scale, and SVG stroke/radial line drawing.
- Do not create multiple slide pages to simulate one animation.
- Open with a punchy hook: title scale/slide-in over 12-18 frames, then accent subtitle reveal.
- Draw the hub with radial line growth, glow pulse, or icon orbit/fade. Keep the movement slow enough to read.
- For metrics, use count-up and a single progress fill. Do not add a separate white sweep overlay.
- End each scene with a short hold so the final state is readable.

## When Not To Use

- Do not use this style for formal consulting decks unless the user asks for a YouTube or creator-style version.
- Do not force charts, gauges, or large numbers when the source is conceptual and has no meaningful metric.
- Do not stack cards inside cards or use decorative blobs/orbs as background filler.

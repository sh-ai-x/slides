---
name: text-to-one-slide
description: Create exactly one presentation slide from text, markdown, Korean drafts, article excerpts, meeting notes, scripts, or dense ideas. Use when Codex needs a single-slide summary, executive one-pager, title slide, KPI/metric slide, concept card, poster-like 16:9 slide, or one-page visual brief instead of a multi-slide deck.
---

# Text to One Slide

## Overview

Turn source text into exactly one slide. Do not create a deck, carousel, or multi-page outline unless the user changes the request.

Default output is a 16:9 GIF plus a compact JSON plan. If the user asks for editable PPTX, pair with `text-to-ppt` but still create a single-slide deck only.

## Workflow

1. Extract one core message from the source.
2. Choose the slide type:
   - `executive-summary`: headline, 3-4 compact points, takeaway.
   - `metric`: one large number, context, supporting bars or chips.
   - `concept`: definition, why it matters, simple structure.
   - `comparison`: two sides and one conclusion.
   - `title`: strong title, subtitle, source/date.
3. Build a single JSON object with short visible text.
4. Render with `scripts/render_one_slide.py` when a visual proof is useful.
5. Verify the output is one slide only and text is readable.

## Rules

- Exactly one slide.
- One main headline; make it say the insight.
- Keep visible body text under 70 Korean characters or 45 English words when possible.
- Put long source detail into `notes`, not on the slide.
- Use one accent color, default red `#c0392b`.
- Prefer dense but readable consulting-style composition over decorative cards.
- If metrics are central to the message, show the most important metric prominently. Do not add a large number just because the source mentions a list count.
- Use compact JSON and local rendering scripts; do not duplicate long source text in chat or visible slide text.

## Quick Start

```bash
python scripts/render_one_slide.py one-slide.json --output one-slide.gif --format wide
```

JSON shape:

```json
{
  "title": "LLM Wiki cuts token waste by structuring knowledge first",
  "eyebrow": "Executive one-slide",
  "metric": "95%",
  "body": "A managed wiki layer turns raw documents into reusable AI-readable knowledge.",
  "points": [
    "Lower token cost",
    "Faster retrieval",
    "Cleaner team onboarding"
  ],
  "footer": "Source: user-provided script",
  "notes": "Longer speaker notes can live here."
}
```

## Resources

- `scripts/render_one_slide.py`: render one slide GIF from JSON.
- `references/one-slide-schema.md`: schema and slide-type guidance.

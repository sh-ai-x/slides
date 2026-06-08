# One Slide Schema

Use this schema when creating a single-slide GIF or a one-slide PPTX handoff.

```json
{
  "title": "Insight headline",
  "eyebrow": "Optional section label",
  "metric": "Optional large metric",
  "body": "One concise explanatory sentence.",
  "points": ["Point one", "Point two", "Point three"],
  "footer": "Source or date",
  "notes": "Speaker notes or source detail."
}
```

## Slide Types

- `executive-summary`: title, body, three points, footer.
- `metric`: eyebrow, metric, title, short body, optional points.
- `concept`: title, body, points as definition / mechanism / impact.
- `comparison`: title, two or three points showing contrast, conclusion in body.
- `title`: title, subtitle in body, footer.

## Text Limits

- Title: one line preferred, two lines max.
- Body: one sentence.
- Points: 2-4 items, each short.
- Notes: unlimited, not visible by default.

## Visual Defaults

- 16:9 `wide`: 1280x720.
- `square`: 1080x1080 for social one-card.
- `card`: 1080x1350 for vertical one-card.
- Accent: `#c0392b`.
- Background: `#f7f8fa`.

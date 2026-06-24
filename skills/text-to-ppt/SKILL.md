---
name: text-to-ppt
description: Create editable PowerPoint decks OR interactive HTML slide decks from plain text, markdown, outlines, notes, pasted articles, Korean drafts, or speaker scripts. Supports PPTX (via pptxgenjs) and self-contained HTML with arrow-key navigation and Remotion-style spring transitions. Use when Codex needs to turn text-only input into a structured presentation with slide titles, bullets, speaker notes, source lines, consulting-style charts or card-like slides, and a professional 16:9 layout.
---

# Text to PPT

## Overview

Convert user-provided text into a presentation deck. Two output formats are supported from the **same deck JSON**:

| Format | Command | Use when |
|--------|---------|----------|
| **PPTX** | `build_pptx.cjs` | Editable file for PowerPoint / Keynote |
| **HTML** | `build_html.cjs` | Browser presentation with arrow-key nav + Remotion spring transitions |

Use a disciplined sequence: clarify only what is necessary → plan → normalize to deck JSON → build output → verify.

## Workflow

### 1. Ask Only Required Questions

For a simple request like "이 텍스트로 PPT 만들어줘", proceed with defaults:

- audience: general business
- slide count: 6-10 slides for ordinary text, 10-15 for long articles or lectures
- format: PPTX unless the user says "HTML", "브라우저", "웹", "화살표 키", or "Remotion"
- style: dark consulting-style deck
- language: preserve the input language

Ask only when the answer materially changes the deck:

- exact slide count
- audience or purpose
- required brand color / accent
- PPTX vs HTML output
- whether slides need custom layouts (metrics cards, bar charts, timelines)

### 2. Plan Before Building

```text
=== PPT 기획안 ===
장수: 6
출력: HTML (화살표 키 + Remotion 스프링 트랜지션)
스타일: dark consulting

1. [cover]  제목 커버
2. [content] 핵심 역량 소개
3. [content] Project 1 — ...
...
=== 기획안 끝 ===
```

### 3. Normalize to Deck JSON

**Option A — Auto (text/markdown input):**
```bash
python3 scripts/text_to_ppt_plan.py input.md --output deck.json --title "Deck Title"
```
Then manually edit the JSON — the auto-converter produces one slide per heading, which is often too many.

**Option B — Manual (recommended for custom layouts):**
Write `deck.json` directly. For custom slide bodies (metrics cards, bar charts, timelines) use the `html` field on individual slides. See `references/deck-json.md` for schema.

### 4a. Build PPTX

```bash
NODE_PATH=/Users/sanghee/.claude/skills/text-to-ppt/node_modules \
  node scripts/build_pptx.cjs deck.json --output deck.pptx
```

### 4b. Build HTML (arrow-key nav + Remotion spring)

```bash
node scripts/build_html.cjs deck.json --output deck.html
```

No extra dependencies — pure Node.js, zero npm installs required.

**HTML features:**
- `←` `→` arrow keys (also `Space`, `↑`, `↓`, `Home`, `End`)
- `N` key to toggle speaker notes overlay
- Dot indicators + prev/next buttons
- Touch swipe support
- Remotion-style spring physics (`springValue()` with stiffness/damping/mass)
- `requestAnimationFrame` 60 fps frame loop
- Auto-scales to any viewport (1280×720 logical canvas)
- Self-contained single `.html` file — no server needed

**For custom slide layouts** write inline HTML in the `html` field of a slide and open the generated file in a browser. Iterate directly in the HTML — the deck JSON is the source of truth for standard slides.

### 5. Verify Quality

PPTX:
- File exists and is non-empty
- Slide count matches plan
- No slide has more than 5 bullets (dense content → notes)

HTML:
- Open in browser, navigate with arrow keys
- Check all slides render without overflow
- Confirm spring animation is smooth (not instant, not sluggish)
- Check notes appear/disappear with `N`

## Style Rules

Default to a dark consulting style:

- Background: `#0d0d0d`, accent: `#c0392b` (red), text: `#f0f0f0`
- No emoji, decorative icons, gradients, or shadows on standard slides
- Slide titles pass the "So what?" test — state the insight, not the topic
- Quantify claims when numbers exist in the source
- One message per slide
- Sub-bullets use indented `"  text"` in the bullets array

For stricter guidance, read `references/consulting-style.md`.

## Resources

- `scripts/text_to_ppt_plan.py`: Auto-convert plain text/markdown to deck JSON.
- `scripts/build_pptx.cjs`: Build editable PPTX from deck JSON (requires pptxgenjs).
- `scripts/build_html.cjs`: Build self-contained HTML presentation from deck JSON (no deps).
- `scripts/check_text_to_ppt_toolchain.sh`: Check toolchain (Node, pptxgenjs).
- `references/deck-json.md`: Deck JSON schema — includes `layout` and `html` fields.
- `references/consulting-style.md`: Consulting-style writing, layout, and validation rules.

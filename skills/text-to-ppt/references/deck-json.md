# Deck JSON

Shared source format for both `build_pptx.cjs` (PPTX) and `build_html.cjs` (HTML).

## Top-level fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `title` | string | required | Deck title — used on auto-generated cover |
| `subtitle` | string | `""` | Cover subtitle |
| `theme` | `"dark"` \| `"light"` | `"dark"` | Color scheme |
| `accent` | hex | `"#c0392b"` | Accent color |
| `slides` | Slide[] | required | Array of slide objects |

## Slide fields (all layouts)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `layout` | string | `"content"` | Layout type — see below |
| `section` | string | `""` | Small label above title (e.g. `"01 / PROJECT 1"`) |
| `title` | string | required | Slide title |
| `notes` | string | `""` | Speaker notes (PPTX notes pane; HTML `N` key overlay) |

---

## Layout types

### `"cover"` — Title page

```json
{
  "layout": "cover",
  "section": "AI Engineering Portfolio",
  "title": "발표 제목",
  "subtitle": "부제목",
  "meta": ["항목1", "항목2", "2026.06.24"]
}
```

Fields: `section` → tag label, `title` → large title, `subtitle` → below line, `meta[]` → small footer items.

---

### `"content"` — Bullet list (default)

```json
{
  "layout": "content",
  "section": "01 / OVERVIEW",
  "title": "핵심 메시지를 제목에 담을 것",
  "bullets": [
    "첫 번째 포인트",
    "  서브 불릿 (2칸 들여쓰기)",
    "",
    "빈 줄은 시각적 구분선"
  ]
}
```

`bullets` rules: 2-5 items ideal. Sub-bullets use 2-space indent. Empty string inserts a spacer row.

---

### `"metrics"` — Metric cards + pipeline + agent table

```json
{
  "layout": "metrics",
  "section": "02 / PROJECT 1",
  "title": "LangGraph 멀티에이전트 고객 이탈 예측",
  "metrics": [
    { "value": "0.9257", "label": "AUC-ROC" },
    { "value": "85%",    "label": "정확도" },
    { "value": "76%",    "label": "이탈 재현율" },
    { "value": "6,589",  "label": "분석 대상 (명)" }
  ],
  "pipeline": ["load_data", "eda", "feature_engineering", "model_training", "evaluation", "report"],
  "agents": [
    { "name": "load_data", "role": "CSV 로드, 타깃 분포 확인" },
    { "name": "eda",       "role": "기술통계, 그룹 비교, LLM 인사이트" }
  ],
  "bullets": [
    "회사 적용 포인트 1",
    "회사 적용 포인트 2"
  ]
}
```

- `metrics[]`: up to 4 cards with big numbers in a row
- `pipeline[]`: node names rendered as connected boxes (last 3 highlighted)
- `agents[]`: numbered step list on left column (shown when both `agents` and `bullets` present)
- `bullets[]`: applied to right column as company-application list

---

### `"bar-chart"` — Horizontal bar chart + stats + insights

```json
{
  "layout": "bar-chart",
  "section": "03 / PROJECT 2",
  "title": "RAG vs LLM Wiki 검색 품질 비교",
  "chart_label": "Precision@5 비교",
  "bars": [
    { "label": "RAG (원본쿼리)",    "value": 0.5208, "max": 0.60, "display": "0.5208", "best": false },
    { "label": "Hybrid α=0.50",    "value": 0.5500, "max": 0.60, "display": "0.5500 — 최고", "best": true }
  ],
  "stats": [
    { "value": "$0.03",  "label": "API 총비용" },
    { "value": "0.0000", "label": "재실행 차이" }
  ],
  "insights": [
    "LLM Wiki 단독 < RAG — 정보 압축으로 어휘 손실",
    "Hybrid 앙상블이 최고 — 두 방법이 상호 보완"
  ],
  "bullets": [
    "사내 문서 치환 시 LLM Wiki 즉시 구축 가능"
  ]
}
```

- `bars[].value`: numeric (used for bar width calculation)
- `bars[].max`: scale maximum (optional; defaults to max value × 1.1)
- `bars[].display`: text shown inside the bar
- `bars[].best`: highlights bar in accent color
- `stats[]`: small stat cards below the chart
- `insights[]`: numbered insight items on right column
- `bullets[]`: company-application list below insights

---

### `"steps"` — Stat cards + numbered pipeline steps

```json
{
  "layout": "steps",
  "section": "04 / PROJECT 3",
  "title": "Harness Engineering 기반 분석 자동화",
  "stats": [
    { "value": "50",   "label": "매장 수",  "unit": "stores" },
    { "value": "156K", "label": "데이터 행", "unit": "rows" },
    { "value": "14",   "label": "외부 피처", "unit": "컬럼" },
    { "value": "RMSE", "label": "성공 지표", "unit": "LightGBM + Prophet" }
  ],
  "steps": [
    { "name": "Ralph Loop",      "role": "분석 목표 명확화" },
    { "name": "define-analysis", "role": "분석 정의 문서 생성 & 승인" },
    { "name": "kaggle-discover", "role": "데이터셋 검색·선정" }
  ],
  "bullets": [
    "Ralph 루프로 목표 먼저 수렴 → AI 실행 품질을 프로세스로 보장",
    "스킬 1줄 호출로 Kaggle 검색부터 리포트까지 재실행 가능"
  ]
}
```

- `stats[]`: up to 4 stat cards at top
- `steps[]`: left column — `name` (accent color, fixed width) + `role` description
- `bullets[]`: right column — key difference bullets

---

### `"timeline"` — N-column timeline + before/after transform

```json
{
  "layout": "timeline",
  "section": "05 / ROADMAP",
  "title": "AI 활용을 팀 인프라로",
  "columns": [
    {
      "period": "단기", "range": "1 — 3개월",
      "items": [
        { "task": "팀 내 반복 분석 1개 자동화", "tech": "Harness 파이프라인 + Python" },
        { "task": "사내 LLM Wiki 프로토타입",   "tech": "RAG + LLM Wiki Hybrid" }
      ]
    },
    {
      "period": "중기", "range": "3 — 6개월",
      "items": [
        { "task": "멀티에이전트 파이프라인 운영", "tech": "LangGraph + Hermes Agent" }
      ]
    },
    {
      "period": "장기", "range": "6개월 ~",
      "items": [
        { "task": "Harness 플랫폼 전사 확산", "tech": "도메인별 에이전트 팀" }
      ]
    }
  ],
  "transform": {
    "before": "사람이 데이터 보고 → 분석 → 리포트 → 의사결정",
    "after": "Ralph 수렴 → Harness 실행 → LLM Wiki 맥락 → 의사결정에만 집중"
  }
}
```

- `columns[]`: 1–3 columns (grid adapts); each has `period`, `range`, `items[{task, tech}]`
- `transform`: optional before/after bar at the bottom

---

### `"two-col"` — Generic two-column layout

```json
{
  "layout": "two-col",
  "title": "슬라이드 제목",
  "left": {
    "heading": "왼쪽 제목",
    "items": [
      { "key": "항목명", "value": "설명" },
      "또는 문자열 불릿"
    ]
  },
  "right": {
    "heading": "오른쪽 제목",
    "items": ["불릿1", "  서브불릿", "불릿2"]
  }
}
```

- `items[]`: if strings → bullet list; if `{key, value}` objects → key/value table
- Mix not supported within one column

---

## Rules

- Titles under 90 characters; pass the "so what?" test
- `metrics` layout: 4 cards max
- `bar-chart`: 3–6 bars for readability
- `steps`: 5–8 steps
- `timeline`: 2–3 columns, 2–4 items each
- Put narration in `notes`, not bullets
- `build_pptx.cjs` uses `bullets[]` as fallback for all layouts except `content` and `cover`

#!/usr/bin/env bash
set -u

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# ── Node ──────────────────────────────────────────────────────────────────
if command -v node >/dev/null 2>&1; then
  printf 'ok: node -> %s\n' "$(command -v node)"
else
  echo 'missing: node  (install via nvm or https://nodejs.org)'
fi

# ── python3 ───────────────────────────────────────────────────────────────
if command -v python3 >/dev/null 2>&1; then
  printf 'ok: python3 -> %s\n' "$(command -v python3)"
else
  echo 'missing: python3  (required for text_to_ppt_plan.py)'
fi

# ── pptxgenjs (PPTX output only) ──────────────────────────────────────────
NODE_PATH="${NODE_PATH:-$SKILL_DIR/node_modules}" node - <<'JS'
const path = require("path");
function tryLoad(p) {
  try { require(p ? path.join(p, "pptxgenjs") : "pptxgenjs"); return true; } catch(_) { return false; }
}
if (tryLoad("") || tryLoad(process.env.NODE_PATH)) {
  console.log("ok: pptxgenjs  (PPTX output available)");
} else {
  console.log("missing: pptxgenjs  (run: cd " + process.env.NODE_PATH?.replace(/\/node_modules$/, "") + " && npm install pptxgenjs)");
}
JS

# ── build_html.cjs (HTML output — no deps) ────────────────────────────────
if [ -f "$SKILL_DIR/scripts/build_html.cjs" ]; then
  echo "ok: build_html.cjs  (HTML output available — no extra deps required)"
else
  echo "missing: build_html.cjs  (expected at scripts/build_html.cjs)"
fi

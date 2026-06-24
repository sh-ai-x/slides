#!/usr/bin/env node
"use strict";

const fs   = require("fs");
const path = require("path");

// ── CLI ───────────────────────────────────────────────────────────────────
function parseArgs(argv) {
  const args = { deckJson: null, output: "deck.html" };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--output" || a === "-o") args.output = argv[++i];
    else if (!args.deckJson) args.deckJson = a;
    else throw new Error(`Unknown argument: ${a}`);
  }
  if (!args.deckJson) throw new Error("Usage: build_html.cjs deck.json --output deck.html");
  return args;
}

// ── Helpers ───────────────────────────────────────────────────────────────
function esc(s) {
  return String(s ?? "")
    .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

// ── Layout renderers ──────────────────────────────────────────────────────

/** layout: "cover" */
function renderCover(slide) {
  return `<div class="slide-cover">
  <div class="cv-tag">${esc(slide.section || "Presentation")}</div>
  <div class="cv-title">${esc(slide.title || "")}</div>
  <div class="cv-line"></div>
  ${slide.subtitle ? `<div class="cv-sub">${esc(slide.subtitle)}</div>` : ""}
  ${slide.meta ? slide.meta.map(m => `<span class="cv-meta-item">${esc(m)}</span>`).join("") : ""}
</div>`;
}

/** layout: "content" (default) — bullets */
function renderContent(slide) {
  const bullets = slide.bullets || [];
  if (!bullets.length) return "";
  const items = bullets.map(b => {
    const s = String(b);
    if (!s.trim()) return `<li class="sp"></li>`;
    const sub = s.startsWith("  ") || s.startsWith("\t");
    return `<li class="${sub ? "sub" : ""}">${esc(s.trim())}</li>`;
  }).join("\n");
  return `<ul class="bullets">${items}</ul>`;
}

/** layout: "metrics" — metric cards + optional pipeline + bullets */
function renderMetrics(slide) {
  const cards = (slide.metrics || []).map(m => `
  <div class="met-card">
    <div class="met-val">${esc(m.value)}</div>
    <div class="met-label">${esc(m.label)}</div>
  </div>`).join("");

  const pipe = slide.pipeline ? `
  <div class="sub-label">에이전트 파이프라인</div>
  <div class="pipeline">${slide.pipeline.map((n,i,a) =>
    `<div class="pipe-node${i >= a.length - 3 ? " hi" : ""}">${esc(n)}</div>${i < a.length-1 ? '<div class="pipe-arr">→</div>' : ""}`
  ).join("")}</div>` : "";

  const twoCol = slide.agents && slide.bullets ? `
  <div class="two-col" style="flex:1">
    <div class="step-list">${(slide.agents || []).map((a,i) =>
      `<div class="step-item"><div class="step-num">${i+1}</div><div class="step-name">${esc(a.name)}</div><div class="step-role">${esc(a.role)}</div></div>`
    ).join("")}</div>
    <div style="display:flex;flex-direction:column;justify-content:center">
      <div class="sub-label">회사 적용</div>
      <ul class="bullets">${(slide.bullets||[]).map(b=>`<li>${esc(b)}</li>`).join("")}</ul>
    </div>
  </div>` : (slide.bullets ? `<ul class="bullets mt">${(slide.bullets||[]).map(b=>`<li>${esc(b)}</li>`).join("")}</ul>` : "");

  return `<div class="met-row">${cards}</div>${pipe}${twoCol}`;
}

/** layout: "bar-chart" — horizontal bars + stats + insights + bullets */
function renderBarChart(slide) {
  const bars = slide.bars || [];
  const maxVal = Math.max(...bars.map(b => b.value), 0.01);

  const barsHtml = bars.map(b => {
    const pct = Math.round((b.value / (b.max || maxVal * 1.1)) * 100);
    return `
    <div class="bar-row">
      <div class="bar-name${b.best ? " best-name" : ""}">${esc(b.label)}</div>
      <div class="bar-track">
        <div class="bar-fill${b.best ? " best" : ""}" data-width="${pct}%" style="width:0%">${b.display || b.value}</div>
      </div>
    </div>`;
  }).join("");

  const statsHtml = (slide.stats || []).map(s => `
  <div class="stat-mini">
    <div class="stat-mini-val">${esc(s.value)}</div>
    <div class="stat-mini-label">${esc(s.label)}</div>
  </div>`).join("");

  const insightsHtml = (slide.insights || []).map((ins, i) => `
  <div class="insight">
    <div class="ins-num">${i+1}</div>
    <div class="ins-text">${esc(ins)}</div>
  </div>`).join("");

  const bulletsHtml = (slide.bullets || []).map(b => `<li>${esc(b)}</li>`).join("");

  return `
  <div class="two-col" style="flex:1">
    <div>
      <div class="sub-label">${esc(slide.chart_label || "비교")}</div>
      <div class="bar-chart">${barsHtml}</div>
      ${statsHtml ? `<div class="stat-mini-row">${statsHtml}</div>` : ""}
    </div>
    <div style="display:flex;flex-direction:column;justify-content:space-between">
      ${insightsHtml ? `<div><div class="sub-label">핵심 인사이트</div>${insightsHtml}</div>` : ""}
      ${bulletsHtml ? `<div><div class="sub-label">회사 적용</div><ul class="bullets">${bulletsHtml}</ul></div>` : ""}
    </div>
  </div>`;
}

/** layout: "steps" — stat cards + step list + bullets */
function renderSteps(slide) {
  const statsHtml = (slide.stats || []).map(s => `
  <div class="stat-card">
    <div class="stat-label">${esc(s.label)}</div>
    <div class="stat-val">${esc(s.value)}</div>
    <div class="stat-unit">${esc(s.unit || "")}</div>
  </div>`).join("");

  const stepsHtml = (slide.steps || []).map(s => `
  <div class="h-step">
    <div class="h-skill">${esc(s.name)}</div>
    <div class="h-arr">→</div>
    <div class="h-role">${esc(s.role)}</div>
  </div>`).join("");

  const bulletsHtml = (slide.bullets || []).map(b => `<li>${esc(b)}</li>`).join("");

  return `
  <div class="stat-row">${statsHtml}</div>
  <div class="two-col" style="flex:1">
    <div>
      <div class="sub-label">파이프라인</div>
      <div class="h-steps">${stepsHtml}</div>
    </div>
    ${bulletsHtml ? `
    <div style="display:flex;flex-direction:column;justify-content:center">
      <div class="sub-label">핵심 차이</div>
      <ul class="bullets">${bulletsHtml}</ul>
    </div>` : ""}
  </div>`;
}

/** layout: "timeline" — N-column timeline + optional transform */
function renderTimeline(slide) {
  const cols = (slide.columns || []).map(col => `
  <div class="tl-col">
    <div class="tl-period">${esc(col.period)}</div>
    <div class="tl-range">${esc(col.range)}</div>
    ${(col.items || []).map(it => `
    <div class="tl-item">
      <div class="tl-dot"></div>
      <div>
        <div class="tl-task">${esc(it.task)}</div>
        ${it.tech ? `<div class="tl-tech">${esc(it.tech)}</div>` : ""}
      </div>
    </div>`).join("")}
  </div>`).join("");

  const tf = slide.transform ? `
  <div class="tf-box">
    <div class="sub-label" style="margin-bottom:8px">내가 만들 수 있는 변화</div>
    <div class="tf-row">
      <span class="tf-tag before">지금</span>
      <span class="tf-text">${esc(slide.transform.before)}</span>
    </div>
    <div class="tf-row">
      <span class="tf-tag after">목표</span>
      <span class="tf-text after">${esc(slide.transform.after)}</span>
    </div>
  </div>` : "";

  return `<div class="tl-grid" style="flex:1">${cols}</div>${tf}`;
}

/** layout: "two-col" — generic two-column */
function renderTwoCol(slide) {
  function renderCol(col) {
    if (!col) return "";
    const head = col.heading ? `<div class="sub-label">${esc(col.heading)}</div>` : "";
    const items = (col.items || []).map(it => {
      if (typeof it === "string") return `<li>${esc(it)}</li>`;
      return `<div class="tc-item"><div class="tc-key">${esc(it.key)}</div><div class="tc-val">${esc(it.value)}</div></div>`;
    });
    const isLi = col.items && col.items.length && typeof col.items[0] === "string";
    return `${head}${isLi ? `<ul class="bullets">${items.join("")}</ul>` : items.join("")}`;
  }
  return `<div class="two-col" style="flex:1"><div>${renderCol(slide.left)}</div><div>${renderCol(slide.right)}</div></div>`;
}

// ── Slide assembler ────────────────────────────────────────────────────────
function renderSlide(slide, idx) {
  const layout  = slide.layout || "content";
  const section = esc(slide.section || "");
  const title   = esc(slide.title   || "");
  const notes   = esc(slide.notes   || "");

  if (layout === "cover") {
    return `<div class="slide" data-index="${idx}" data-notes="${notes}">${renderCover(slide)}</div>`;
  }

  let body;
  switch (layout) {
    case "metrics":   body = renderMetrics(slide);   break;
    case "bar-chart": body = renderBarChart(slide);  break;
    case "steps":     body = renderSteps(slide);     break;
    case "timeline":  body = renderTimeline(slide);  break;
    case "two-col":   body = renderTwoCol(slide);    break;
    default:          body = renderContent(slide);   break;
  }

  return `<div class="slide" data-index="${idx}" data-notes="${notes}">
  <div class="slide-hd">
    ${section ? `<div class="sec-label">${section}</div>` : ""}
    <div class="sl-title">${title}</div>
    <div class="sl-rule"></div>
  </div>
  <div class="slide-bd">${body}</div>
  <div class="sl-num">${String(idx).padStart(2,"0")}</div>
</div>`;
}

// ── CSS ───────────────────────────────────────────────────────────────────
const CSS = `
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --red:#c0392b;--dark:#0d0d0d;--card:#252525;--border:#333;
  --text:#f0f0f0;--muted:#888;--sub:#aaa;
}
html,body{width:100%;height:100%;overflow:hidden;background:#000;
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Apple SD Gothic Neo','Noto Sans KR',sans-serif;
  -webkit-font-smoothing:antialiased}

/* Stage / Deck */
#stage{position:fixed;inset:0;display:flex;align-items:center;justify-content:center}
#deck{position:relative;width:1280px;height:720px;overflow:hidden;transform-origin:center center}

/* Progress */
#pbar{position:absolute;top:0;left:0;height:3px;background:var(--red);z-index:100;
  transition:width .4s cubic-bezier(.34,1.56,.64,1)}

/* Slide base */
.slide{position:absolute;inset:0;background:var(--dark);color:var(--text);
  display:flex;flex-direction:column;will-change:transform,opacity;opacity:0;pointer-events:none}
.slide.active{opacity:1;pointer-events:auto}

/* Cover */
.slide-cover{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;
  text-align:center;padding:60px 80px}
.cv-tag{font-size:11px;font-weight:600;letter-spacing:4px;text-transform:uppercase;
  color:var(--red);margin-bottom:24px}
.cv-title{font-size:52px;font-weight:800;color:#fff;line-height:1.15;margin-bottom:20px}
.cv-line{width:60px;height:3px;background:var(--red);margin:0 auto 20px}
.cv-sub{font-size:18px;color:var(--muted);margin-bottom:20px}
.cv-meta-item{font-size:12px;color:#444;letter-spacing:1px;display:inline-block;margin:0 16px}

/* Slide header */
.slide-hd{padding:44px 68px 0;flex-shrink:0}
.sec-label{font-size:11px;font-weight:600;letter-spacing:3px;text-transform:uppercase;
  color:var(--red);margin-bottom:8px}
.sl-title{font-size:32px;font-weight:700;color:#fff;line-height:1.2;margin-bottom:14px}
.sl-rule{height:1px;background:var(--border)}
.slide-bd{flex:1;padding:20px 68px 42px;overflow:hidden;display:flex;flex-direction:column}
.sl-num{position:absolute;right:22px;bottom:16px;font-size:10px;color:#2a2a2a;letter-spacing:1px}

/* Sub-label */
.sub-label{font-size:10px;font-weight:600;letter-spacing:2px;text-transform:uppercase;
  color:var(--muted);margin-bottom:10px}

/* Bullets */
.bullets{list-style:none;margin-top:8px}
.bullets li{position:relative;padding:7px 0 7px 20px;border-bottom:1px solid #1e1e1e;
  font-size:16px;color:var(--sub);line-height:1.55}
.bullets li::before{content:'';position:absolute;left:0;top:16px;
  width:7px;height:7px;background:var(--red);border-radius:50%}
.bullets li.sub{padding-left:34px;font-size:13px;color:#555;border-bottom:none}
.bullets li.sub::before{left:14px;top:13px;width:5px;height:5px;background:#3a3a3a}
.bullets li.sp{border:none;padding:3px 0}
.bullets li.sp::before{display:none}
.bullets li strong{color:#fff}
.bullets.mt{margin-top:12px}

/* Two-col grid */
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:28px}

/* Metric cards */
.met-row{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:18px;flex-shrink:0}
.met-card{background:var(--card);border:1px solid var(--border);border-radius:5px;
  padding:14px 16px;text-align:center}
.met-val{font-size:34px;font-weight:800;color:var(--red);line-height:1}
.met-label{font-size:11px;color:var(--muted);margin-top:5px}

/* Pipeline */
.pipeline{display:flex;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:0}
.pipe-node{background:var(--card);border:1px solid var(--border);border-radius:3px;
  padding:6px 10px;font-size:11px;font-weight:600;color:#bbb;white-space:nowrap}
.pipe-node.hi{border-color:var(--red);color:var(--red)}
.pipe-arr{color:var(--muted);font-size:13px;padding:0 5px}

/* Step list */
.step-list{display:flex;flex-direction:column;gap:5px}
.step-item{display:flex;align-items:center;gap:10px;background:var(--card);
  border:1px solid var(--border);border-radius:4px;padding:7px 12px;font-size:12px}
.step-num{flex-shrink:0;width:20px;height:20px;background:var(--red);border-radius:50%;
  display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:800;color:#fff}
.step-name{font-weight:700;color:#fff;width:150px;flex-shrink:0}
.step-role{color:var(--sub);font-size:11px}

/* Stat cards */
.stat-row{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:16px;flex-shrink:0}
.stat-card{background:var(--card);border:1px solid var(--border);border-radius:5px;
  padding:12px 16px;text-align:center}
.stat-label{font-size:10px;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted)}
.stat-val{font-size:30px;font-weight:800;color:var(--red);margin-top:2px}
.stat-unit{font-size:11px;color:#555;margin-top:2px}

/* Harness steps */
.h-steps{display:flex;flex-direction:column}
.h-step{display:flex;align-items:center;gap:10px;padding:7px 0;border-bottom:1px solid #1e1e1e}
.h-skill{width:160px;flex-shrink:0;font-size:12px;font-weight:700;color:var(--red)}
.h-arr{color:#3a3a3a;font-size:12px}
.h-role{font-size:12px;color:var(--sub)}

/* Bar chart */
.bar-chart{display:flex;flex-direction:column;gap:9px;margin-bottom:14px}
.bar-row{display:flex;align-items:center;gap:10px}
.bar-name{width:190px;font-size:12px;color:#aaa;flex-shrink:0;text-align:right}
.bar-name.best-name{color:var(--red);font-weight:700}
.bar-track{flex:1;height:22px;background:#1a1a1a;border-radius:3px;overflow:hidden}
.bar-fill{height:100%;border-radius:3px;background:#444;display:flex;align-items:center;
  padding-left:8px;font-size:11px;font-weight:700;color:#ccc;
  transition:width .8s cubic-bezier(.34,1.2,.64,1)}
.bar-fill.best{background:var(--red);color:#fff}
.stat-mini-row{display:flex;gap:10px;margin-top:4px}
.stat-mini{flex:1;background:var(--card);border:1px solid var(--border);border-radius:4px;padding:8px 12px}
.stat-mini-val{font-size:20px;font-weight:800;color:var(--red)}
.stat-mini-label{font-size:10px;color:var(--muted);margin-top:2px}

/* Insights */
.insight{display:flex;gap:10px;margin-bottom:12px;align-items:flex-start}
.ins-num{flex-shrink:0;width:22px;height:22px;background:var(--red);border-radius:50%;
  display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:800;color:#fff}
.ins-text{font-size:13px;color:var(--sub);line-height:1.6}
.ins-text strong{color:#fff}

/* Timeline */
.tl-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:14px}
.tl-col{background:var(--card);border:1px solid var(--border);border-radius:5px;padding:18px 16px}
.tl-period{font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--red);font-weight:700}
.tl-range{font-size:17px;font-weight:800;color:#fff;margin:3px 0 14px;
  padding-bottom:12px;border-bottom:1px solid var(--border)}
.tl-item{display:flex;gap:10px;align-items:flex-start;margin-bottom:10px}
.tl-dot{flex-shrink:0;margin-top:5px;width:7px;height:7px;border-radius:50%;background:var(--red)}
.tl-task{font-size:12px;color:#ccc;line-height:1.5}
.tl-tech{font-size:11px;color:var(--red);margin-top:2px}
.tf-box{background:var(--card);border:1px solid var(--border);border-radius:5px;padding:14px 18px;flex-shrink:0}
.tf-row{display:flex;align-items:baseline;gap:12px;font-size:12px;margin-bottom:5px}
.tf-tag{font-size:10px;letter-spacing:1.5px;text-transform:uppercase;font-weight:700;width:40px;flex-shrink:0}
.tf-tag.before{color:var(--muted)}
.tf-tag.after{color:var(--red)}
.tf-text{color:#888}
.tf-text.after{color:#fff;font-weight:600}

/* Two-col generic */
.tc-item{display:flex;gap:12px;padding:7px 0;border-bottom:1px solid #1e1e1e;font-size:13px}
.tc-key{width:160px;flex-shrink:0;color:var(--red);font-weight:700}
.tc-val{color:var(--sub)}

/* Navigation */
#nav{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);
  display:flex;align-items:center;gap:14px;
  background:rgba(12,12,12,.93);border:1px solid #2a2a2a;border-radius:30px;
  padding:8px 20px;z-index:999;backdrop-filter:blur(12px);user-select:none}
.nbtn{background:none;border:none;cursor:pointer;color:#555;font-size:16px;
  padding:2px 6px;transition:color .15s}
.nbtn:hover{color:var(--red)}
.nbtn:disabled{color:#222;cursor:default}
#ncnt{font-size:12px;color:#444;min-width:38px;text-align:center}
.dots{display:flex;gap:6px}
.dot{width:6px;height:6px;border-radius:50%;background:#2a2a2a;cursor:pointer;
  transition:background .25s,transform .25s}
.dot.active{background:var(--red);transform:scale(1.4)}

/* Notes overlay */
#nbar{position:fixed;bottom:66px;left:50%;transform:translateX(-50%);
  max-width:860px;width:90%;background:rgba(8,8,8,.96);
  border:1px solid #1e1e1e;border-radius:6px;padding:10px 16px;
  font-size:12px;color:#555;line-height:1.6;display:none;z-index:998}
#nbar.on{display:block}
`;

// ── JS runtime ────────────────────────────────────────────────────────────
function jsRuntime(slideCount) {
  return `
function spring(t,cfg){
  cfg=cfg||{};var s=cfg.stiffness||120,d=cfg.damping||14,m=cfg.mass||1;
  if(t<=0)return 0;
  var w=Math.sqrt(s/m),z=d/(2*Math.sqrt(s*m));
  if(z<1){var wd=w*Math.sqrt(1-z*z);return 1-Math.exp(-z*w*t)*(Math.cos(wd*t)+(z*w/wd)*Math.sin(wd*t));}
  return 1-Math.exp(-w*t)*(1+w*t);
}
function clamp(v,a,b){return Math.max(a,Math.min(b,v))}
function lerp(a,b,t){return a+(b-a)*clamp(t,0,1)}

var TOTAL=${slideCount},cur=0,anim=false;
var slides=Array.from(document.querySelectorAll('.slide'));
var dotsEl=document.getElementById('dots');
var ncnt=document.getElementById('ncnt');
var pbar=document.getElementById('pbar');
var bp=document.getElementById('bp'),bn=document.getElementById('bn');
var nbar=document.getElementById('nbar');

for(var i=0;i<TOTAL;i++){(function(ix){
  var d=document.createElement('div');
  d.className='dot'+(ix===0?' active':'');
  d.onclick=function(){goTo(ix)};
  dotsEl.appendChild(d);
})(i)}

var deck=document.getElementById('deck');
function scale(){
  var s=Math.min(window.innerWidth/1280,window.innerHeight/720);
  deck.style.transform='scale('+s+')';
}
scale();window.addEventListener('resize',scale);

slides[0].classList.add('active');
slides[0].style.transform='translateX(0)';
ui();

function goTo(nx){
  if(anim||nx===cur||nx<0||nx>=TOTAL)return;
  anim=true;
  var pv=cur,dir=nx>pv?1:-1,DUR=400;
  var os=slides[pv],ns=slides[nx];
  ns.style.transform='translateX('+(dir*72)+'px)';
  ns.style.opacity='0';
  ns.classList.add('active');
  var t0=performance.now();
  function tick(now){
    var p=clamp((now-t0)/DUR,0,1),sp=clamp(spring(p*.30),0,1);
    os.style.transform='translateX('+(lerp(0,-dir*72,sp))+'px)';
    os.style.opacity=lerp(1,0,clamp(sp/.35,0,1));
    ns.style.transform='translateX('+(lerp(dir*72,0,sp))+'px)';
    ns.style.opacity=clamp((sp-.1)/.4,0,1);
    if(p<1){requestAnimationFrame(tick)}
    else{
      os.classList.remove('active');os.style.cssText='';
      ns.style.transform='translateX(0)';ns.style.opacity='1';
      cur=nx;anim=false;ui();enter(cur);
    }
  }
  requestAnimationFrame(tick);
}

function ui(){
  ncnt.textContent=(cur+1)+' / '+TOTAL;
  pbar.style.width=((cur+1)/TOTAL*100)+'%';
  bp.disabled=cur===0;bn.disabled=cur===TOTAL-1;
  document.querySelectorAll('.dot').forEach(function(d,i){d.classList.toggle('active',i===cur)});
  var note=slides[cur]&&slides[cur].dataset.notes;
  if(note){nbar.textContent=note;nbar.classList.add('on')}else{nbar.classList.remove('on')}
}

function enter(idx){
  slides[idx].querySelectorAll('.bar-fill[data-width]').forEach(function(f){
    f.style.width='0%';
    requestAnimationFrame(function(){setTimeout(function(){f.style.width=f.dataset.width},80)});
  });
}
enter(0);

document.addEventListener('keydown',function(e){
  if(e.key==='ArrowRight'||e.key==='ArrowDown'||e.key===' '){e.preventDefault();goTo(cur+1)}
  else if(e.key==='ArrowLeft'||e.key==='ArrowUp'){e.preventDefault();goTo(cur-1)}
  else if(e.key==='Home'){goTo(0)}
  else if(e.key==='End'){goTo(TOTAL-1)}
  else if(e.key==='n'||e.key==='N'){nbar.classList.toggle('on')}
});
bp.onclick=function(){goTo(cur-1)};
bn.onclick=function(){goTo(cur+1)};
var tx=0;
document.addEventListener('touchstart',function(e){tx=e.touches[0].clientX},{passive:true});
document.addEventListener('touchend',function(e){
  var dx=e.changedTouches[0].clientX-tx;
  if(Math.abs(dx)>50)goTo(cur+(dx<0?1:-1));
},{passive:true});
`;
}

// ── HTML assembler ────────────────────────────────────────────────────────
function generateHtml(deck) {
  const accent = deck.accent || "#c0392b";
  const slides = deck.slides || [];

  // Inject cover from deck metadata if first slide isn't already a cover
  const hasExplicitCover = slides[0] && slides[0].layout === "cover";
  const allSlides = hasExplicitCover
    ? slides.map((s, i) => renderSlide(s, i))
    : [
        renderSlide({ layout: "cover", section: "Presentation", title: deck.title, subtitle: deck.subtitle }, 0),
        ...slides.map((s, i) => renderSlide(s, i + 1)),
      ];
  const total = allSlides.length;

  return `<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>${esc(deck.title || "Deck")}</title>
<style>
${CSS.replace(/--red:#c0392b/, `--red:${accent}`)}
</style>
</head>
<body>
<div id="stage">
  <div id="deck">
    <div id="pbar"></div>
${allSlides.join("\n")}
  </div>
</div>
<div id="nav">
  <button class="nbtn" id="bp">&#8592;</button>
  <div class="dots" id="dots"></div>
  <span id="ncnt">1 / ${total}</span>
  <button class="nbtn" id="bn">&#8594;</button>
</div>
<div id="nbar"></div>
<script>${jsRuntime(total)}</script>
</body>
</html>`;
}

// ── Main ──────────────────────────────────────────────────────────────────
function main() {
  const args = parseArgs(process.argv);
  const deck = JSON.parse(fs.readFileSync(path.resolve(args.deckJson), "utf8"));
  const html = generateHtml(deck);
  fs.mkdirSync(path.dirname(path.resolve(args.output)), { recursive: true });
  fs.writeFileSync(path.resolve(args.output), html, "utf8");
  const cnt = (deck.slides || []).length + 1;
  console.log(`Wrote ${args.output} with ${cnt} slides`);
}

main();

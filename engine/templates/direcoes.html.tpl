<!DOCTYPE html>
%%PROVENIENCIA%%
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>temcomo · Relatório de direções — %%PERGUNTA_TITULO%%</title>
<style>
/* ===== QualiApps Design System — tokens (fonte: skills/brand/qualiapps-design-system/tokens.css, via base aprovada 001-revisao-design-doc.html) ===== */
%%FONTS%%
%%TOKENS%%
*, *::before, *::after { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; scroll-behavior: smooth; scrollbar-gutter: stable; }
body {
  margin: 0; background: var(--bg-soft); color: var(--ink);
  font-family: var(--font-body); font-size: var(--fs-16);
  line-height: var(--lh-normal); font-weight: 400;
  -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;
  padding-bottom: 168px;
}
img { display:block; max-width:100%; }
h1,h2,h3,h4 { font-family: var(--font-display); color: var(--ink); margin:0; line-height: var(--lh-tight); letter-spacing:-0.01em; }
p { margin:0; }
:focus-visible { outline:none; box-shadow: var(--ring-focus); border-radius: var(--r-2); }
::selection { background: color-mix(in srgb, var(--brand) 25%, transparent); }
.sr-only { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0 0 0 0); white-space:nowrap; border:0; }
[hidden]:not([hidden="until-found"]) { display:none !important; }
.container { max-width: var(--container-w); margin: 0 auto; padding-left: var(--container-pad); padding-right: var(--container-pad); }
button { font: inherit; }
.linklike { background:none; border:0; padding:9px 10px; color: var(--brand-ink); font-family: var(--font-display); font-weight:600; font-size: var(--fs-14); cursor:pointer; border-radius: var(--r-2); }
.linklike:hover { background: var(--brand-tint); }

/* ===== Faixa de protótipo (topo) ===== */
.notice-strip {
  background: var(--bg-ink); color: #FFFFFF;
  font-family: var(--font-display); font-weight: 500; font-size: var(--fs-14);
  padding: 10px var(--container-pad); text-align: center; line-height: var(--lh-snug);
}
.notice-strip .dot { display:inline-block; width:8px; height:8px; border-radius:2px; background: var(--brand-soft); margin-right: 8px; vertical-align: 1px; }
.notice-strip strong { font-weight: 700; letter-spacing: .04em; }

/* ===== Topbar ===== */
.topbar { background: var(--bg); border-bottom: 1px solid var(--line); }
.topbar-inner { display:flex; align-items:center; justify-content:space-between; gap: var(--sp-4); padding-top: var(--sp-4); padding-bottom: var(--sp-4); flex-wrap: wrap; }
.topbar img.logo { height: 30px; width: auto; }
.topbar .meta { text-align:right; }
.topbar .meta .rid { font-family: var(--font-mono); font-size: var(--fs-12); color: var(--ink-3); }
.topbar .meta .rdate { font-family: var(--font-display); font-weight:500; font-size: var(--fs-12); color: var(--ink-3); margin-top:2px; }

/* ===== Hero compacto (orçamento: ≤180px de altura no desktop) ===== */
.hero { padding-top: var(--sp-5); }
.hero-card { background: var(--bg); border:1px solid var(--line); border-radius: var(--r-5); box-shadow: var(--shadow-2); padding: 14px var(--sp-6); }
.hero-top .linklike { padding: 2px 6px; }
.hero-top { display:flex; align-items:center; justify-content:space-between; gap: var(--sp-3); flex-wrap:wrap; }
.eyebrow { font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); letter-spacing:.08em; text-transform:uppercase; color: var(--brand-ink); }
.hero h1 { font-size: clamp(1.25rem, 2vw, 1.5rem); font-weight: 800; margin-top: 3px; }
.objective-box { margin-top: 7px; background: var(--brand-tint); border:1px solid color-mix(in srgb, var(--brand) 22%, var(--line)); border-radius: var(--r-3); padding: 7px 14px; font-size: var(--fs-14); color: var(--ink); line-height: 1.4; }
.objective-box .obj-label { font-family: var(--font-display); font-weight:700; font-size: var(--fs-12); letter-spacing:.05em; text-transform:uppercase; color: var(--brand-ink); margin-right: 6px; }
.hero-instr { margin-top: 7px; font-size: var(--fs-14); color: var(--ink-3); line-height: var(--lh-snug); }
.hero-instr strong { color: var(--ink-2); font-weight:600; }

/* ===== Avisos (rascunho de versão anterior / dica de anotação) ===== */
.draft-notice { background: var(--warn-tint); border:1px solid color-mix(in srgb, var(--warning) 30%, var(--line)); border-radius: var(--r-3); padding: var(--sp-3) var(--sp-4); margin-top: var(--sp-4); font-size: var(--fs-14); color: var(--ink-2); line-height: var(--lh-normal); display:flex; gap: var(--sp-3); align-items:flex-start; justify-content:space-between; flex-wrap:wrap; }
.annot-hint { margin-top: var(--sp-3); font-size: var(--fs-14); color: var(--ink-3); display:flex; align-items:center; gap: var(--sp-2); flex-wrap:wrap; }
.boot-fallback { background: var(--danger-tint); color: var(--danger-ink); border:1px solid color-mix(in srgb, var(--danger) 30%, var(--line)); border-radius: var(--r-3); padding: var(--sp-3) var(--sp-4); margin: var(--sp-4) auto 0; max-width: var(--container-w); font-family: var(--font-display); font-weight:600; font-size: var(--fs-14); }

/* ===== Tabela comparativa = a lista (consenso 2/3 do conselho) ===== */
.compare { margin-top: var(--sp-6); }
.compare-head { display:flex; align-items:flex-end; justify-content:space-between; gap: var(--sp-3); flex-wrap:wrap; margin-bottom: var(--sp-3); }
.compare h2 { font-size: var(--fs-20); font-weight: 700; margin-bottom: var(--sp-1); }
.compare .sub { font-size: var(--fs-14); color: var(--ink-3); max-width: 72ch; }
.table-card { background: var(--bg); border:1px solid var(--line); border-radius: var(--r-5); box-shadow: var(--shadow-2); position: relative; }
.table-scroll { overflow-x: auto; border-radius: var(--r-5); }
.table-card .scroll-fade { display:none; position:absolute; top:0; right:0; bottom:0; width:44px; border-radius: 0 var(--r-5) var(--r-5) 0; background: linear-gradient(to right, rgba(255,255,255,0), var(--bg) 82%); pointer-events:none; }
.table-hint { display:none; font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); color: var(--ink-3); margin-top: var(--sp-2); }
.table-card.scrollable .scroll-fade { display:block; }
.table-card.scrollable.at-end .scroll-fade { display:none; }
.table-card.scrollable + .table-hint { display:block; }
table.direcoes { width:100%; min-width: 880px; border-collapse: collapse; }
table.direcoes th { font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); letter-spacing:.05em; text-transform:uppercase; color: var(--ink-3); text-align:left; padding: 12px; border-bottom: 1.5px solid var(--line); white-space: nowrap; user-select:none; }
table.direcoes td { padding: 14px 12px; border-bottom: 1px solid var(--line-soft); font-size: var(--fs-14); color: var(--ink-2); vertical-align: middle; }
table.direcoes tr:last-child td { border-bottom: none; }
tr.dir-row { cursor: pointer; min-height: 64px; }
tr.dir-row:hover td { background: color-mix(in srgb, var(--bg-soft) 60%, transparent); }
tr.dir-row:focus-within td { background: color-mix(in srgb, var(--bg-soft) 60%, transparent); }
tr.dir-row.is-reco td { background: var(--ok-tint); }
tr.dir-row.is-reco:hover td { background: color-mix(in srgb, var(--success) 16%, var(--bg) 84%); }
tr.dir-row.is-fdc td { border-top: 1.5px dashed color-mix(in srgb, var(--brand) 45%, var(--line)); }
tr.dir-row.row-chosen { outline: 2px solid var(--brand-strong); outline-offset: -2px; }
table.direcoes .t-dir { font-family: var(--font-display); font-weight:600; color: var(--ink); min-width: 250px; }
table.direcoes .t-limit { min-width: 200px; color: var(--ink-3); line-height: var(--lh-normal); font-size: var(--fs-14); }
table.direcoes .td-custo { min-width: 108px; }
table.direcoes .td-custo .custo-curto { display:block; font-size: var(--fs-12); color: var(--ink-3); }
table.direcoes .td-escolha { min-width: 150px; }
.letter-pill { display:inline-flex; align-items:center; justify-content:center; width:26px; height:26px; border-radius: 8px; background: var(--brand-strong); color:#fff; font-family: var(--font-display); font-weight:700; font-size: var(--fs-14); flex:none; user-select:none; }
.t-dir-inner { display:flex; align-items:flex-start; gap:10px; }
.row-open { background:none; border:0; padding:0; text-align:left; font-family: var(--font-display); font-weight:600; font-size: var(--fs-14); color: var(--ink); cursor:pointer; display:inline-flex; align-items:center; gap:6px; }
.row-open .chev { width:13px; height:13px; color: var(--ink-4); flex:none; }
.row-resumo { margin-top: 3px; font-family: var(--font-body); font-weight:400; font-size: var(--fs-14); color: var(--ink-3); line-height: var(--lh-snug); }
.t-badges { margin-top: 5px; display:flex; gap:6px; flex-wrap:wrap; }
.adr { display:flex; align-items:center; gap:10px; min-width: 128px; user-select:none; }
.adr .adr-num { font-family: var(--font-mono); font-size: var(--fs-14); color: var(--ink); min-width: 3ch; }
.adr .adr-bar { flex:1; height:8px; min-width: 64px; border-radius: var(--r-pill); background: var(--line-soft); overflow:hidden; }
.adr .adr-bar > span { display:block; height:100%; background: var(--brand-strong); border-radius: var(--r-pill); }
.badge-reco { display:inline-flex; align-items:center; gap:6px; border-radius: var(--r-pill); background: var(--ok-tint); color: var(--ok-ink); border:1px solid color-mix(in srgb, var(--success) 30%, var(--line)); font-family: var(--font-display); font-weight:700; font-size: 0.6875rem; letter-spacing:.03em; text-transform:uppercase; padding: 3px 10px; user-select:none; }
.badge-reco::before { content:""; width:7px; height:7px; border-radius:50%; background: var(--success); }
.badge-fdc { display:inline-flex; align-items:center; gap:6px; border-radius: var(--r-pill); background: var(--bg); color: var(--brand-ink); border:1.5px dashed color-mix(in srgb, var(--brand) 55%, var(--line)); font-family: var(--font-display); font-weight:700; font-size: 0.6875rem; letter-spacing:.03em; text-transform:uppercase; padding: 3px 10px; user-select:none; }
.btn-choose { min-height: 44px; padding: 8px 16px; border-radius: var(--r-3); border:1.5px solid color-mix(in srgb, var(--brand) 45%, var(--line)); background: var(--bg); color: var(--brand-ink); font-family: var(--font-display); font-weight:600; font-size: var(--fs-14); cursor:pointer; white-space:nowrap; user-select:none; }
.btn-choose:hover { background: var(--brand-tint); }
.btn-choose.is-chosen { background: var(--ok-tint); border-color: color-mix(in srgb, var(--success) 40%, var(--line)); color: var(--ok-ink); }
.btn-choose.is-chosen::before { content:"✓ "; }
.row-annot { display:inline-flex; align-items:center; justify-content:center; min-width:18px; height:18px; border-radius:50%; background: var(--brand-strong); margin-left: 8px; vertical-align: middle; position:relative; }
.row-annot::after { content: attr(data-count); color:#fff; font-family: var(--font-display); font-weight:700; font-size: 11px; line-height:1; padding: 0 4px; }
@keyframes chip-pulse { 0% { opacity:.35; } 100% { opacity:1; } }
.pulse { animation: chip-pulse 200ms ease 1; }

/* ===== Chips de estado (linguagem leiga, tokens AA do DS) ===== */
.status-chip { display:inline-flex; align-items:center; gap:7px; border-radius: var(--r-pill); padding: 5px 12px; font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); background: var(--bg-soft); color: var(--ink-3); border:1px solid var(--line); user-select:none; white-space:nowrap; }
.status-chip::before { content:""; width:7px; height:7px; border-radius:50%; background: var(--ink-4); flex:none; }
.status-chip.ok { background: var(--ok-tint); color: var(--ok-ink); border-color: color-mix(in srgb, var(--success) 30%, var(--line)); }
.status-chip.ok::before { background: var(--success); }

/* ===== Critérios (compacto) ===== */
.criteria-card { margin-top: var(--sp-5); background: var(--bg); border:1px solid var(--line); border-radius: var(--r-5); box-shadow: var(--shadow-1); padding: var(--sp-5) var(--sp-6); }
.criteria-card h2 { font-size: var(--fs-16); font-weight:700; margin-bottom: var(--sp-1); }
.criteria-card .crit-intro { font-size: var(--fs-14); color: var(--ink-3); line-height: var(--lh-normal); margin-bottom: var(--sp-3); max-width: 80ch; }
.crit-grid { display:grid; grid-template-columns: repeat(2, 1fr); gap: var(--sp-2) var(--sp-6); }
.crit-item { border-left:3px solid var(--brand); padding-left: var(--sp-3); }
.crit-item .crit-name { font-family: var(--font-display); font-weight:600; font-size: var(--fs-14); color: var(--ink); display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
.crit-item .crit-q { margin:1px 0 0; font-size: var(--fs-14); color: var(--ink-3); line-height: var(--lh-snug); }
.tag-peso { display:inline-flex; align-items:center; border-radius: var(--r-pill); border:1px solid var(--line); background: var(--bg-soft); color: var(--ink-3); font-family: var(--font-display); font-weight:600; font-size: 0.6875rem; padding: 1px 8px; }
.tag-peso.alto { background: var(--brand-tint); color: var(--brand-ink); border-color: color-mix(in srgb, var(--brand) 25%, var(--line)); }
.tag-sempre { display:inline-flex; align-items:center; border-radius: var(--r-pill); background: var(--ok-tint); color: var(--ok-ink); border:1px solid color-mix(in srgb, var(--success) 30%, var(--line)); font-family: var(--font-display); font-weight:600; font-size: 0.6875rem; padding: 1px 8px; }

/* ===== Documento (conteúdo real renderizado; wizard é aprimoramento por cima) ===== */
.documento { margin-top: var(--sp-8); }
.documento h2 { font-size: var(--fs-20); font-weight:700; }
.documento .sub { font-size: var(--fs-14); color: var(--ink-3); margin-top: 4px; max-width: 72ch; }
article.dir-doc { background: var(--bg); border:1.5px solid var(--line); border-radius: var(--r-5); box-shadow: var(--shadow-1); padding: var(--sp-6) var(--sp-8); margin-top: var(--sp-4); }
article.dir-doc.is-fdc { border-style: dashed; border-color: color-mix(in srgb, var(--brand) 45%, var(--line)); }
article.dir-doc.doc-chosen { border-color: var(--brand-strong); border-style: solid; }
.doc-head { display:flex; align-items:flex-start; justify-content:space-between; gap: var(--sp-3); flex-wrap:wrap; }
.dir-title { display:flex; align-items:flex-start; gap: 12px; }
.dir-title h3 { font-size: var(--fs-20); font-weight:700; line-height: var(--lh-snug); }
.dir-title .dir-origin { margin-top: 3px; font-size: var(--fs-14); color: var(--ink-3); }
.card-badges { display:flex; gap:8px; flex-wrap:wrap; align-items:center; }
.doc-head-actions { display:flex; align-items:center; gap: var(--sp-2); }
.block-label { font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); letter-spacing:.07em; text-transform:uppercase; color: var(--ink-3); margin: var(--sp-5) 0 var(--sp-2); }
.dir-explica { color: var(--ink-2); line-height: var(--lh-loose); max-width: 72ch; }
.dir-meta { display:grid; grid-template-columns: repeat(4, 1fr); gap: var(--sp-3); margin-top: var(--sp-5); }
.meta-field { background: var(--bg-soft); border:1px solid var(--line-soft); border-radius: var(--r-3); padding: 10px 14px; }
.meta-field .mf-label { font-family: var(--font-display); font-weight:600; font-size: 0.6875rem; letter-spacing:.06em; text-transform:uppercase; color: var(--ink-3); }
.meta-field .mf-value { margin-top: 2px; font-family: var(--font-display); font-weight:600; font-size: var(--fs-14); color: var(--ink); }
.meta-field .mf-note { font-size: var(--fs-12); color: var(--ink-3); margin-top: 1px; }
.limit-box { margin-top: var(--sp-4); background: var(--warn-tint); border:1px solid color-mix(in srgb, var(--warning) 30%, var(--line)); border-radius: var(--r-3); padding: var(--sp-3) var(--sp-4); font-size: var(--fs-14); color: var(--ink-2); line-height: var(--lh-normal); }
.limit-box strong { color: var(--warn-ink); font-family: var(--font-display); font-weight: 700; font-size: var(--fs-12); letter-spacing:.05em; text-transform:uppercase; display:block; margin-bottom: 3px; }
.scores { margin-top: var(--sp-2); display:flex; flex-direction:column; gap: 8px; }
.score-row { display:grid; grid-template-columns: 190px 1fr auto; align-items:center; gap: var(--sp-3); }
.score-row .sc-name { font-family: var(--font-display); font-weight:500; font-size: var(--fs-12); color: var(--ink-3); }
.score-dots { display:flex; gap:5px; user-select:none; }
.score-dots span { width:22px; height:8px; border-radius: 3px; background: var(--line-soft); }
.score-dots span.on { background: var(--brand-strong); }
.score-row .sc-val { font-family: var(--font-mono); font-size: var(--fs-12); color: var(--ink-3); }
.cons-grid { display:grid; grid-template-columns: 1fr 1fr; gap: var(--sp-4); }
.cons-box { border:1px solid var(--line-soft); border-radius: var(--r-4); padding: var(--sp-4) var(--sp-5); }
.cons-box h4 { font-size: var(--fs-14); font-weight:700; margin-bottom: var(--sp-2); display:flex; align-items:center; gap:8px; }
.cons-box h4::before { content:""; width:8px; height:8px; border-radius:2px; flex:none; }
.cons-box.ok { background: var(--ok-tint); border-color: color-mix(in srgb, var(--success) 25%, var(--line)); }
.cons-box.ok h4 { color: var(--ok-ink); } .cons-box.ok h4::before { background: var(--success); }
.cons-box.warn { background: var(--warn-tint); border-color: color-mix(in srgb, var(--warning) 28%, var(--line)); }
.cons-box.warn h4 { color: var(--warn-ink); } .cons-box.warn h4::before { background: var(--warning); }
.cons-box ul { margin:0; padding-left: 18px; display:flex; flex-direction:column; gap: 6px; }
.cons-box li { font-size: var(--fs-14); color: var(--ink-2); line-height: var(--lh-normal); }
.cons-box.ok li::marker { color: var(--success); }
.cons-box.warn li::marker { color: var(--warning); }
.cons-facts { display:grid; grid-template-columns: 1fr 1fr; gap: var(--sp-3); margin-top: var(--sp-4); }
.cons-fact { background: var(--bg-soft); border:1px solid var(--line-soft); border-radius: var(--r-3); padding: 10px 14px; }
.cons-fact .cf-label { font-family: var(--font-display); font-weight:600; font-size: 0.6875rem; letter-spacing:.06em; text-transform:uppercase; color: var(--ink-3); }
.cons-fact .cf-value { margin-top: 2px; font-size: var(--fs-14); color: var(--ink); line-height: var(--lh-normal); }
.vs-note { margin-top: var(--sp-4); background: var(--brand-tint); border:1px solid color-mix(in srgb, var(--brand) 22%, var(--line)); border-radius: var(--r-3); padding: var(--sp-3) var(--sp-4); font-size: var(--fs-14); color: var(--ink-2); line-height: var(--lh-normal); }
.vs-note strong { display:block; font-family: var(--font-display); font-weight:700; font-size: var(--fs-12); letter-spacing:.05em; text-transform:uppercase; color: var(--brand-ink); margin-bottom: 3px; }
.reco-note { margin-top: var(--sp-4); background: var(--ok-tint); border:1px solid color-mix(in srgb, var(--success) 25%, var(--line)); border-radius: var(--r-3); padding: var(--sp-3) var(--sp-4); font-size: var(--fs-14); color: var(--ink-2); line-height: var(--lh-normal); }
.reco-note strong { display:block; font-family: var(--font-display); font-weight:700; font-size: var(--fs-12); letter-spacing:.05em; text-transform:uppercase; color: var(--ok-ink); margin-bottom: 3px; }

/* ===== Wizard (dialog nativo + remendos do parecer técnico) ===== */
dialog.wiz { border:0; padding:0; margin:auto; background: var(--bg); color: var(--ink);
  width: min(720px, calc(100vw - 48px)); max-width:none; max-height: 86vh;
  border-radius: var(--r-5); box-shadow: var(--shadow-3); }
dialog.wiz[open] { display:flex; flex-direction:column; animation: wiz-in 180ms cubic-bezier(.2,0,0,1); }
dialog.wiz::backdrop { background: color-mix(in srgb, var(--bg-ink) 45%, transparent); animation: fade-in 160ms ease; }
@keyframes wiz-in { from { opacity:0; transform: translateY(8px) scale(.98); } }
@keyframes fade-in { from { opacity:0; } }
.wiz-handle { display:none; }
.wiz-head { flex:none; display:flex; align-items:flex-start; gap: 12px; padding: var(--sp-4) var(--sp-6); border-bottom:1px solid var(--line-soft); background: var(--bg); border-radius: var(--r-5) var(--r-5) 0 0; }
.wiz-head-main { flex:1; min-width:0; }
.wiz-head .eyebrow { margin-bottom: 2px; }
.wiz-head h2 { font-size: var(--fs-20); font-weight:700; line-height: var(--lh-snug); }
.wiz-head h2:focus-visible { box-shadow:none; outline:none; }
.wiz-head .card-badges { margin-top: 6px; }
.wiz-close { flex:none; width:44px; height:44px; border:0; background:none; border-radius: var(--r-3); color: var(--ink-3); font-size: 26px; line-height:1; cursor:pointer; user-select:none; }
.wiz-close:hover { background: var(--bg-soft); color: var(--ink); }
.wiz-body { overflow-y:auto; overscroll-behavior: contain; padding: var(--sp-5) var(--sp-8) var(--sp-6); transition: opacity 120ms ease; }
.wiz-body .doc-body > .block-label:first-child { margin-top: 0; }
.wiz-foot { flex:none; display:flex; align-items:center; gap: var(--sp-3); padding: var(--sp-3) var(--sp-6); border-top:1px solid var(--line); background: var(--bg); border-radius: 0 0 var(--r-5) var(--r-5); }
.wiz-nav { min-width:44px; padding:10px; }
.wiz-nav svg { width:16px; height:16px; display:block; }
.wiz-nav:disabled { opacity:.35; cursor:default; }
.wiz-segs { display:flex; gap:5px; margin:0 auto; }
.seg { position:relative; width:22px; height:24px; background:none; border:0; padding:0; cursor:pointer; border-radius: var(--r-2); user-select:none; }
.seg::before { content:""; position:absolute; inset:-10px -5px; }
.seg::after { content:""; position:absolute; left:0; right:0; top:8px; height:8px; border-radius:3px; background: var(--line-soft); }
.seg.cur::after { box-shadow: var(--ring-focus); }
.seg.chosen::after { background: var(--brand-strong); }
#wiz-choose { white-space:nowrap; }
#wiz-choose.is-chosen { background: var(--ok-tint); color: var(--ok-ink); border:1.5px solid color-mix(in srgb, var(--success) 40%, var(--line)); }
dialog.wiz--info { width: min(560px, calc(100vw - 48px)); }
.info-body { padding: var(--sp-5) var(--sp-6) var(--sp-6); overflow-y:auto; overscroll-behavior: contain; }
.info-step { display:flex; gap: 12px; margin-top: var(--sp-4); }
.info-step .num { display:inline-flex; align-items:center; justify-content:center; width:26px; height:26px; border-radius: 8px; background: var(--brand-strong); color:#fff; font-family: var(--font-display); font-weight:700; font-size: var(--fs-14); flex:none; }
.info-step h3 { font-size: var(--fs-14); font-weight:600; margin-bottom: 2px; }
.info-step p { font-size: var(--fs-14); color: var(--ink-3); line-height: var(--lh-normal); }
.info-note { margin-top: var(--sp-4); background: var(--bg-soft); border:1px solid var(--line-soft); border-radius: var(--r-3); padding: var(--sp-3) var(--sp-4); font-size: var(--fs-14); color: var(--ink-2); line-height: var(--lh-normal); }

/* ===== Anotações ancoradas ===== */
[data-anotavel] { position: relative; }
mark.annot { background: color-mix(in srgb, var(--brand) 14%, transparent); border-bottom: 2px dotted var(--brand-ink); border-radius: 2px; padding: 0 1px; color: inherit; cursor: pointer; }
mark.annot.is-active { background: color-mix(in srgb, var(--brand) 22%, transparent); border-bottom-style: solid; }
.annot-badge { display:inline-flex; align-items:center; justify-content:center; min-width:18px; height:18px; border-radius: var(--r-pill); background: var(--brand-strong); vertical-align: super; margin-left: 2px; cursor:pointer; position:relative; user-select:none; }
.annot-badge::after { content: attr(data-count); color:#fff; font-family: var(--font-display); font-weight:700; font-size: 11px; line-height:1; padding: 0 5px; }
.annot-badge::before { content:""; position:absolute; inset:-13px; }
.has-block-annot { outline: 2px dotted color-mix(in srgb, var(--brand) 45%, var(--line)); outline-offset: 4px; border-radius: var(--r-2); }
.annot-block-btn { position:absolute; top:0; right:8px; transform: translateY(-55%); z-index:2; opacity:0; pointer-events:none; background: var(--bg); border:1px solid color-mix(in srgb, var(--brand) 45%, var(--line)); color: var(--brand-ink); border-radius: var(--r-pill); font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); padding: 4px 10px; min-height: 30px; cursor:pointer; user-select:none; }
.annot-block-btn::before { content:"Anotar bloco"; }
.annot-block-btn::after { content:""; position:absolute; inset:-7px; }
[data-anotavel]:hover > .annot-block-btn, [data-anotavel]:focus-within > .annot-block-btn, .annot-block-btn:focus { opacity:1; pointer-events:auto; }
.sel-toolbar { position:fixed; z-index:80; background: var(--bg-ink); border-radius: var(--r-pill); box-shadow: var(--shadow-2); padding: 3px; display:flex; }
.sel-toolbar button { background:none; border:0; color:#fff; font-family: var(--font-display); font-weight:600; font-size: var(--fs-14); padding: 10px 18px; min-height: 44px; border-radius: var(--r-pill); cursor:pointer; user-select:none; }
.sel-toolbar button:hover { background: rgba(255,255,255,.12); }
.annot-pop { position:fixed; z-index:85; width: min(340px, calc(100vw - 32px)); background: var(--bg); border:1px solid var(--line); border-radius: var(--r-4); box-shadow: var(--shadow-3); padding: var(--sp-4); }
.annot-pop.sheet { left:0 !important; right:0; bottom:0; top:auto !important; width:100%; border-radius: var(--r-5) var(--r-5) 0 0; padding-bottom: calc(var(--sp-4) + env(safe-area-inset-bottom)); }
.annot-pop h3 { font-size: var(--fs-14); font-weight:700; margin-bottom: var(--sp-2); }
.annot-quote { font-size: var(--fs-12); color: var(--ink-3); border-left: 3px solid var(--brand); padding: 2px 0 2px 10px; margin-bottom: var(--sp-3); max-height: 72px; overflow:hidden; line-height: var(--lh-snug); }
.annot-trunc-note { font-size: var(--fs-12); color: var(--warn-ink); font-family: var(--font-display); font-weight:600; margin-bottom: var(--sp-2); }
.annot-pop textarea { min-height: 72px; }
.annot-pop-actions { margin-top: var(--sp-3); display:flex; gap: var(--sp-2); }
.annot-pop-actions .btn { min-height: 44px; padding: 8px 16px; }

/* ===== Painel de anotações (drawer desktop / sheet mobile) ===== */
.annot-panel { position:fixed; top:0; right:0; bottom:0; z-index:60; width:min(360px, 100vw); background:var(--bg); border-left:1px solid var(--line); box-shadow: var(--shadow-3); display:none; flex-direction:column; }
.annot-panel.open { display:flex; }
.ap-head { flex:none; display:flex; align-items:center; justify-content:space-between; gap: var(--sp-2); padding: var(--sp-4) var(--sp-5); border-bottom:1px solid var(--line-soft); }
.ap-head h2 { font-size: var(--fs-16); font-weight:700; }
.ap-close { width:44px; height:44px; border:0; background:none; border-radius: var(--r-3); color: var(--ink-3); font-size: 24px; line-height:1; cursor:pointer; }
.ap-close:hover { background: var(--bg-soft); color: var(--ink); }
.ap-undo { display:none; padding: var(--sp-2) var(--sp-5); background: var(--warn-tint); font-size: var(--fs-14); color: var(--ink-2); align-items:center; gap: var(--sp-2); justify-content:space-between; }
.ap-undo.on { display:flex; }
.ap-body { flex:1; overflow-y:auto; overscroll-behavior:contain; padding: var(--sp-4) var(--sp-5); display:flex; flex-direction:column; gap: var(--sp-3); }
.ap-empty { font-size: var(--fs-14); color: var(--ink-3); line-height: var(--lh-normal); }
.ap-section { font-family: var(--font-display); font-weight:700; font-size: var(--fs-12); letter-spacing:.06em; text-transform:uppercase; color: var(--warn-ink); margin-top: var(--sp-2); }
.ap-item { background: var(--bg-soft); border-radius: var(--r-3); padding: var(--sp-3) var(--sp-4); }
.ap-item .ap-quote { font-size: var(--fs-12); color: var(--ink-3); border-left: 3px solid var(--brand); padding-left: 10px; line-height: var(--lh-snug); }
.ap-item.orfa .ap-quote { border-left-color: var(--warning); }
.ap-item .ap-status { margin-top: 4px; font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); color: var(--warn-ink); }
.ap-item .ap-text { margin-top: 6px; font-size: var(--fs-14); color: var(--ink-2); line-height: var(--lh-normal); }
.ap-item .ap-meta { margin-top: 6px; font-family: var(--font-mono); font-size: var(--fs-12); color: var(--ink-3); }
.ap-item .ap-actions { margin-top: 8px; display:flex; gap: var(--sp-1); flex-wrap:wrap; }
@media (max-width: 760px) {
  .annot-panel { top:auto; left:0; right:0; width:100%; max-height: 80dvh; border-left:0; border-top:1px solid var(--line); border-radius: var(--r-5) var(--r-5) 0 0; }
}

/* ===== Conferência + comentário ===== */
.confer { margin-top: var(--sp-8); background: var(--bg); border:1px solid var(--line); border-radius: var(--r-5); box-shadow: var(--shadow-2); padding: var(--sp-6) var(--sp-8); }
.confer h2 { font-size: var(--fs-18); font-weight:700; margin-bottom: var(--sp-2); }
.confer .sub { font-size: var(--fs-14); color: var(--ink-3); margin-bottom: var(--sp-3); max-width: 72ch; }
.confer-status { display:flex; align-items:center; gap: var(--sp-3); flex-wrap:wrap; margin-bottom: var(--sp-4); font-family: var(--font-display); font-weight:600; font-size: var(--fs-14); color: var(--ink-2); }
.confer label { display:block; font-family: var(--font-display); font-weight:600; font-size: var(--fs-14); color: var(--ink-2); margin-bottom: 7px; }
textarea { width:100%; padding: 12px 14px; font-family: var(--font-body); font-size: var(--fs-16); color: var(--ink); line-height: var(--lh-normal); background: var(--bg); border: 1.5px solid var(--line); border-radius: var(--r-3); resize: vertical; min-height: 96px; overflow: hidden; }
textarea:focus { border-color: var(--brand); outline:none; box-shadow: var(--ring-focus); }
textarea::placeholder { color: var(--ink-3); opacity: 1; }
.confer-annot-list { margin: 0; padding-left: 18px; display:flex; flex-direction:column; gap: 4px; }
.confer-annot-list li { font-size: var(--fs-14); color: var(--ink-2); }
.confer-annot-list .linklike { padding: 2px 4px; }

/* ===== Barra fixa de export ===== */
.export-bar { position: fixed; left:0; right:0; bottom:0; z-index: 40; background: var(--bg); border-top: 1px solid var(--line); box-shadow: var(--shadow-3); }
.storage-alert { display:none; background: var(--danger-tint); color: var(--danger-ink); border-bottom:1px solid color-mix(in srgb, var(--danger) 30%, var(--line)); font-family: var(--font-display); font-weight:600; font-size: var(--fs-14); padding: 8px var(--container-pad); }
.storage-alert.on { display:block; }
.export-progress { height:4px; background: var(--line-soft); }
.export-progress > span { display:block; height:100%; width:0; background: var(--brand-strong); transition: width .2s ease; }
.export-inner { display:flex; align-items:center; justify-content:space-between; gap: var(--sp-3); padding-top: var(--sp-3); padding-bottom: calc(var(--sp-3) + env(safe-area-inset-bottom)); flex-wrap: wrap; }
.export-state { min-width: 0; flex:1; }
.export-count { font-family: var(--font-display); font-weight:700; font-size: var(--fs-14); color: var(--ink-2); }
.copy-feedback { font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); color: var(--ok-ink); min-height: 1em; }
.export-note { font-size: var(--fs-12); color: var(--ink-3); margin-top: 2px; }
.export-actions { display:flex; gap: var(--sp-2); flex-wrap: wrap; align-items:center; }
.btn { display:inline-flex; align-items:center; justify-content:center; gap:8px; min-height: 46px; padding: 10px 18px; border-radius: var(--r-3); font-family: var(--font-display); font-weight:600; font-size: var(--fs-14); cursor:pointer; border:1.5px solid transparent; user-select:none; }
.btn-primary { background: var(--brand-strong); color: #FFFFFF; }
.btn-primary:hover { background: color-mix(in srgb, var(--brand) 62%, var(--ink) 38%); }
.btn-secondary { background: var(--bg); color: var(--brand-ink); border-color: color-mix(in srgb, var(--brand) 45%, var(--line)); }
.btn-secondary:hover { background: var(--brand-tint); }
#btn-annot-panel { gap: 0; }

/* ===== Prévia manual (fallback de cópia) ===== */
.preview-panel { display:none; margin-top: var(--sp-6); background: var(--bg); border:1px solid var(--line); border-radius: var(--r-4); box-shadow: var(--shadow-2); padding: var(--sp-5); }
.preview-panel.open { display:block; }
.preview-panel h2 { font-size: var(--fs-16); font-weight:700; margin-bottom: var(--sp-2); }
.preview-panel p { font-size: var(--fs-14); color: var(--ink-3); margin-bottom: var(--sp-3); }
.preview-panel pre { margin:0; max-height: 340px; overflow:auto; background: var(--bg-soft); border:1px solid var(--line-soft); border-radius: var(--r-3); padding: var(--sp-3); font-family: var(--font-mono); font-size: var(--fs-12); line-height: 1.55; white-space: pre-wrap; word-break: break-word; user-select: all; }
.preview-panel .preview-actions { margin-top: var(--sp-3); display:flex; gap: var(--sp-2); }

/* ===== Footer ===== */
.pagefoot { margin-top: var(--sp-12); border-top:1px solid var(--line); background: var(--bg); }
.pagefoot-inner { padding-top: var(--sp-6); padding-bottom: var(--sp-8); display:flex; flex-direction:column; gap: var(--sp-2); }
.pagefoot .mono { font-family: var(--font-mono); font-size: var(--fs-12); color: var(--ink-3); word-break: break-all; }
.pagefoot .foot-note { font-size: var(--fs-14); color: var(--ink-3); line-height: var(--lh-normal); max-width: 72ch; }
.pagefoot img.logo { height: 22px; width:auto; align-self: flex-start; margin-bottom: var(--sp-2); }

/* ===== Mobile ===== */
@media (max-width: 760px) {
  body { padding-bottom: 240px; }
  .hero-card, .criteria-card, .confer { padding: var(--sp-5); }
  article.dir-doc { padding: var(--sp-5); }
  .crit-grid { grid-template-columns: 1fr; }
  .topbar .meta { text-align:left; }
  .dir-meta { grid-template-columns: 1fr 1fr; }
  .cons-grid { grid-template-columns: 1fr; }
  .cons-facts { grid-template-columns: 1fr; }
  .score-row { grid-template-columns: 1fr auto; gap: 4px var(--sp-3); }
  .score-row .sc-name { grid-column: 1 / -1; }
  .score-dots span { width: 34px; }
  .export-inner { display:grid; grid-template-columns: 1fr 1fr; gap: var(--sp-2); }
  .export-state { grid-column: 1 / -1; }
  .export-count { white-space: normal; line-height: var(--lh-snug); }
  .export-actions { display: contents; }
  .export-note { display:none; }
  .export-state { order:-2; }
  #btn-copy-json { order:-1; grid-column: 1 / -1; }
  /* tabela vira lista empilhada (rows de 76px+, parecer DS) */
  .table-scroll { overflow-x: visible; }
  table.direcoes { min-width: 0; display:block; }
  table.direcoes thead { display:none; }
  table.direcoes tbody { display:block; }
  table.direcoes tr.dir-row { display:grid; grid-template-columns: 1fr 1fr; gap: 6px var(--sp-3); padding: var(--sp-4); border-bottom:1px solid var(--line-soft); min-height: 76px; }
  table.direcoes tr.dir-row td { display:block; border:0; padding:0; min-width:0; background:none !important; }
  table.direcoes tr.dir-row.is-reco { background: var(--ok-tint); }
  table.direcoes .t-dir { grid-column: 1 / -1; }
  table.direcoes .td-custo::before { content:"Custo: "; font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); color: var(--ink-3); text-transform:uppercase; letter-spacing:.05em; }
  table.direcoes .td-adr { display:flex; align-items:center; gap:8px; }
  table.direcoes .td-adr::before { content:"Aderência: "; font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); color: var(--ink-3); text-transform:uppercase; letter-spacing:.05em; }
  table.direcoes .t-limit { grid-column: 1 / -1; }
  table.direcoes .td-escolha { grid-column: 1 / -1; display:flex; align-items:center; gap: var(--sp-2); }
  .table-hint { display:none !important; }
  html { scrollbar-gutter: auto; }
  /* wizard vira folha inferior */
  dialog.wiz { width:100%; max-width:100%; margin:0; inset:auto 0 0 0; border-radius: var(--r-5) var(--r-5) 0 0; max-height: 92dvh; }
  dialog.wiz[open] { animation: sheet-in 240ms ease-out; }
  .wiz-handle { display:block; width:36px; height:4px; border-radius: var(--r-pill); background: var(--line); margin: 8px auto 0; }
  .wiz-head { border-radius:0; padding: var(--sp-3) var(--sp-4); }
  .wiz-body { padding: var(--sp-4) var(--sp-5); }
  .wiz-foot { padding: var(--sp-3) var(--sp-4) calc(var(--sp-3) + env(safe-area-inset-bottom)); flex-wrap:wrap; }
  .wiz-segs { order:-1; width:100%; justify-content:center; margin-bottom: 2px; }
  #wiz-choose { flex:1; }
  .doc-head-actions { width:100%; }
  .doc-head-actions .btn-choose { width:100%; }
}
@keyframes sheet-in { from { transform: translateY(100%); } }

/* artigo em modo compacto não desenha casca vazia (P2-2); o chrome volta onde o conteúdo é revelado */
article.dir-doc[hidden] { border:0; box-shadow:none; padding:0; margin:0; }
html.js-failed article.dir-doc[hidden] { border:1.5px solid var(--line); box-shadow: var(--shadow-1); padding: var(--sp-6) var(--sp-8); margin-top: var(--sp-4); }
html.js-failed article.dir-doc.is-fdc[hidden] { border-style: dashed; }

/* ===== Degradação sem JS / falha de boot: conteúdo integral visível ===== */
html.js-failed [hidden="until-found"] { content-visibility: visible !important; }

/* ===== Impressão: documento completo + anotações (consenso 3/3 nº 2) ===== */
@media print {
  body { background:#fff; padding-bottom: 0; }
  [hidden="until-found"] { content-visibility: visible !important; }
  .export-bar, .sel-toolbar, .annot-pop, .annot-hint, .preview-panel, .wiz-close, .annot-block-btn, .compare-head .linklike, .hero-top .linklike, .draft-notice, .boot-fallback { display:none !important; }
  dialog { display:none !important; }
  .annot-panel { display:block !important; position:static; width:auto; max-height:none; border:1px solid var(--line); border-radius: var(--r-4); box-shadow:none; margin-top: var(--sp-6); }
  .annot-panel.is-empty { display:none !important; }
  .ap-close, .ap-undo { display:none !important; }
  .table-scroll { overflow: visible; }
  table.direcoes { min-width: 0; }
  article.dir-doc, .table-card, .criteria-card, .confer { box-shadow:none; break-inside: avoid-page; }
  article.dir-doc[hidden] { border:1.5px solid var(--line); padding: var(--sp-6) var(--sp-8); margin-top: var(--sp-4); }
  article.dir-doc.is-fdc[hidden] { border-style: dashed; }
  mark.annot, .annot-badge, .letter-pill, .status-chip, .adr .adr-bar > span, .score-dots span.on { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; transition-duration: 0.01ms !important; }
  html { scroll-behavior: auto; }
}
.anotacoes-incompletas { border:1px solid var(--warn-line); background:var(--warn-tint);
  border-radius:var(--r-md); padding:14px 16px; margin:0 0 12px; max-width:100%; }
.anotacoes-incompletas .ai-title { font:600 15px/1.3 var(--f-ui); margin:0 0 6px; color:var(--warn-ink); }
.anotacoes-incompletas .ai-sub { font:400 14px/1.5 var(--f-body); margin:0 0 10px; color:var(--ink-2); }
.anotacoes-incompletas .ai-item { border-top:1px solid var(--warn-line); padding-top:10px; margin-top:10px; }
.anotacoes-incompletas blockquote { font:400 14px/1.5 var(--f-body); margin:0 0 8px; color:var(--ink-1); }
.anotacoes-incompletas .ai-acoes { display:flex; gap:8px; flex-wrap:wrap; }
</style>
</head>
<body data-tarefa-id="%%TAREFA_ID%%" data-schema-export="%%SCHEMA_EXPORT%%">

%%FAIXA_EXEMPLO%%

<header class="topbar">
  <div class="container topbar-inner">
    <img class="logo" alt="QualiApps" width="1638" height="395" src="%%LOGO_SRC%%">
    <div class="meta">
      <div class="rid">%%RID%%</div>
      <div class="rdate">%%RDATE%%</div>
    </div>
  </div>
</header>

<div id="boot-fallback" class="boot-fallback container" hidden role="alert"></div>

<main class="container">
  <section class="hero" aria-labelledby="hero-title">
    <div class="hero-card" id="hero-card">
      <div class="hero-top">
        <div class="eyebrow">%%EYEBROW%%</div>
        <button type="button" class="linklike" id="btn-info">Como funciona esta página</button>
      </div>
      <h1 id="hero-title">%%PERGUNTA%%</h1>
      <p class="objective-box" data-anotavel="objetivo"><span class="obj-label">O objetivo, em palavras simples:</span>%%OBJETIVO%%<button type="button" class="annot-block-btn" data-bloco="objetivo" aria-label="Anotar este bloco inteiro"></button></p>
      <p class="hero-instr">%%HERO_INSTRUCAO%%</p>
    </div>
  </section>

  <div class="draft-notice" id="draft-notice" hidden role="status"><span id="draft-notice-text"></span><button type="button" class="linklike" id="draft-notice-dismiss">Entendi</button></div>

  <section class="compare" aria-labelledby="compare-title">
    <div class="compare-head">
      <div>
        <h2 id="compare-title">%%COMPARE_TITULO%%</h2>
        <p class="sub">Aderência mede, de 0 a 100, o quanto o caminho entrega exatamente o que você pediu. O recomendado vem destacado, mas <strong>nada vem escolhido de fábrica</strong> — a escolha só vale quando você apertar "Escolher".</p>
      </div>
      <button type="button" class="linklike" id="btn-doc-mode">Ver tudo como documento</button>
    </div>
    <div class="table-card">
      <div class="scroll-fade" aria-hidden="true"></div>
      <div class="table-scroll" tabindex="0" role="region" aria-labelledby="compare-title">
        <table class="direcoes">
          <caption class="sr-only">Comparação dos %%CAMINHOS%%: custo, aderência ao objetivo, limite principal e a sua escolha</caption>
          <thead>
            <tr>
              <th scope="col">Caminho</th>
              <th scope="col">Custo</th>
              <th scope="col">Aderência (0–100)</th>
              <th scope="col">Limite principal</th>
              <th scope="col">Sua escolha</th>
            </tr>
          </thead>
          <tbody id="compare-body">
%%ROWS%%
          </tbody>
        </table>
      </div>
    </div>
    <p class="table-hint">A tabela continua para o lado — arraste ou role horizontalmente para ver todas as colunas.</p>
    <p class="annot-hint" id="annot-hint" hidden>Dica: selecione qualquer trecho de texto desta página para deixar uma anotação presa a ele.<button type="button" class="linklike" id="hint-dismiss">Entendi</button></p>
  </section>

  <section class="criteria-card" aria-labelledby="crit-title">
    <h2 id="crit-title">Como as direções foram ranqueadas</h2>
    <p class="crit-intro">Os %%CAMINHOS%% foram avaliados com os mesmos critérios, sempre declarados — nenhuma nota é "achismo" escondido. A integração agêntica está presente em toda avaliação do temcomo, por regra.</p>
    <div class="crit-grid">
%%CRITERIA%%
    </div>
  </section>

  <section class="documento" aria-labelledby="doc-title">
    <h2 id="doc-title">%%DOC_TITULO%%</h2>
    <p class="sub" id="doc-sub">É o mesmo conteúdo que abre ao tocar num caminho da tabela, em página corrida — para ler tudo de uma vez, imprimir ou buscar (Ctrl+F). Escolher funciona aqui também.</p>
%%ARTICLES%%
  </section>

  <section class="confer" aria-labelledby="confer-title">
    <h2 id="confer-title">Confira antes de devolver</h2>
    <div class="confer-status">
      <span class="status-chip" id="confer-chip">Falta decidir</span>
      <span id="confer-text">%%TEXTO_SEM_ESCOLHA%%</span>
      <button type="button" class="linklike" id="btn-undo" hidden>Desfazer minha escolha</button>
    </div>
    <label for="comentario">Seu comentário (opcional) — vai junto na resposta e muda o que será feito</label>
    <p class="sub">Ajuste, condição ou dúvida sobre a escolha — por exemplo: "quero esse caminho, mas só se der para começar no mês que vem". Anotação é diferente: é um bilhete preso a um trecho do texto, para quem escreveu o material.</p>
    <textarea id="comentario" maxlength="%%MAX_COMENTARIO%%" placeholder="Escreva aqui, se quiser. Pode ficar em branco."></textarea>
    <div class="confer-annots">
      <div class="block-label">Suas anotações (<span id="confer-annot-count">0</span>)</div>
      <ul id="confer-annot-list" class="confer-annot-list"></ul>
      <p class="sub" id="confer-annot-empty">Nenhuma anotação ainda. Selecione um trecho de texto para anotar.</p>
    </div>
  </section>

  <section class="preview-panel" id="preview-panel" aria-label="Prévia para cópia manual">
    <h2 id="preview-title">Prévia para cópia manual</h2>
    <p>A cópia automática não funcionou neste navegador. Toque no texto abaixo para selecioná-lo inteiro e copie manualmente (Cmd+C ou Ctrl+C).</p>
    <pre id="preview-pre" tabindex="0"></pre>
    <div class="preview-actions">
      <button type="button" class="btn btn-secondary" id="preview-select">Selecionar tudo</button>
      <button type="button" class="btn btn-secondary" id="preview-close">Fechar prévia</button>
    </div>
  </section>
</main>

<footer class="pagefoot">
  <div class="container pagefoot-inner">
    <img class="logo" alt="QualiApps" width="1638" height="395" src="%%LOGO_SRC%%">
    %%RODAPE%%</div>
</footer>

<div class="export-bar" role="region" aria-label="Devolver resposta">
  <div class="storage-alert" id="storage-alert" role="alert"></div>
  <div class="export-progress" aria-hidden="true"><span id="progress-fill"></span></div>
  <div class="container export-inner">
    <div class="export-state">
      <div class="export-count" id="export-count">Nenhum caminho escolhido ainda</div>
      <div class="copy-feedback" id="copy-feedback" role="status" aria-live="polite"></div>
      <div class="export-note" id="autosave-note">O rascunho fica salvo automaticamente neste navegador. Esta página não executa nada — só registra a sua escolha.</div>
    </div>
    <div class="anotacoes-incompletas" id="anotacoes-incompletas" role="alert" hidden></div>
    <div class="anotacoes-incompletas" id="campos-estourados" role="alert" hidden></div>
    <div class="export-actions">
      <button type="button" class="btn btn-secondary" id="btn-annot-sel" hidden>Anotar seleção</button>
      <button type="button" class="btn btn-secondary" id="btn-annot-panel">Anotações (<span id="annot-count">0</span>)</button>
      <button type="button" class="btn btn-primary" id="btn-copy-json">Copiar resposta</button>
      <button type="button" class="btn btn-secondary" id="btn-download-json">Baixar arquivo</button>
    </div>
  </div>
</div>

<dialog class="wiz" id="wizard" aria-labelledby="wiz-title">
  <div class="wiz-handle" aria-hidden="true"></div>
  <div class="wiz-head">
    <span class="letter-pill" id="wiz-pill" aria-hidden="true">A</span>
    <div class="wiz-head-main">
      <div class="eyebrow" id="wiz-eyebrow"></div>
      <h2 id="wiz-title" tabindex="-1"></h2>
      <div class="card-badges" id="wiz-badges"></div>
    </div>
    <button type="button" class="wiz-close" id="wiz-close" aria-label="Salvar e fechar">×</button>
  </div>
  <div class="wiz-body" id="wiz-body"></div>
  <div class="wiz-foot">
    <button type="button" class="btn btn-secondary wiz-nav" id="wiz-prev" aria-label="Caminho anterior"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M10 3L5 8l5 5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
    <div class="wiz-segs" id="wiz-segs" role="group" aria-label="Ir direto para um caminho"></div>
    <button type="button" class="btn btn-secondary wiz-nav" id="wiz-next" aria-label="Próximo caminho"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M6 3l5 5-5 5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
    <button type="button" class="btn btn-primary" id="wiz-choose">Escolher este caminho</button>
  </div>
</dialog>

<dialog class="wiz wiz--info" id="info-dialog" aria-labelledby="info-title">
  <div class="wiz-handle" aria-hidden="true"></div>
  <div class="wiz-head">
    <div class="wiz-head-main">
      <div class="eyebrow">temcomo · relatório de direções</div>
      <h2 id="info-title" tabindex="-1">Como funciona esta página</h2>
    </div>
    <button type="button" class="wiz-close" id="info-close" aria-label="Fechar">×</button>
  </div>
  <div class="info-body">
    <div class="info-step"><span class="num">1</span><div><h3>Compare na tabela</h3><p>A tabela mostra os %%CAMINHOS%% lado a lado: custo, aderência ao objetivo e o principal limite de cada um. O recomendado vem destacado — mas nada é gravado antes de você agir.</p></div></div>
    <div class="info-step"><span class="num">2</span><div><h3>Abra e escolha</h3><p>Toque num caminho para ler os detalhes em palavras simples. O botão "Escolher este caminho" funciona na tabela, nos detalhes e no modo documento. Para trocar, é só escolher outro; fechar a janela (Esc, fundo ou ×) sempre salva o rascunho, nunca descarta.</p></div></div>
    <div class="info-step"><span class="num">3</span><div><h3>Anote, confira e devolva</h3><p>Selecione qualquer trecho de texto para deixar uma anotação presa a ele. No fim, confira o resumo na seção "Confira antes de devolver" e use a barra de baixo para copiar ou baixar sua resposta e me mandar na conversa.</p></div></div>
    <div class="info-note"><strong>Fique tranquilo:</strong> esta página não executa nada e não acessa a internet — ela só registra a sua escolha. O rascunho fica salvo automaticamente neste navegador enquanto você decide.</div>
  </div>
</dialog>

<div class="sel-toolbar" id="sel-toolbar" hidden><button type="button" id="sel-annotate">Anotar</button></div>

<div class="annot-pop" id="annot-pop" role="dialog" aria-label="Nova anotação" hidden>
  <h3>Anotação presa ao trecho</h3>
  <div class="annot-quote" id="annot-pop-quote"></div>
  <div class="annot-trunc-note" id="annot-pop-note" hidden>A seleção passou do bloco: anotei só o trecho do primeiro bloco selecionado.</div>
  <textarea id="annot-pop-text" maxlength="%%MAX_ANOTACAO%%" placeholder="Escreva o seu bilhete sobre este trecho (pode ficar em branco — o marcador já vale)."></textarea>
  <div class="annot-pop-actions">
    <button type="button" class="btn btn-primary" id="annot-pop-save">Salvar anotação</button>
    <button type="button" class="btn btn-secondary" id="annot-pop-cancel">Descartar</button>
  </div>
</div>

<aside class="annot-panel" id="annot-panel" aria-label="Suas anotações">
  <div class="ap-head">
    <h2>Anotações (<span id="ap-count">0</span>)</h2>
    <button type="button" class="ap-close" id="ap-close" aria-label="Fechar painel">×</button>
  </div>
  <div class="ap-undo" id="ap-undo"><span>Anotação apagada.</span><button type="button" class="linklike" id="ap-undo-btn">Desfazer</button></div>
  <div class="ap-body" id="ap-body"></div>
</aside>

<div class="sr-only" aria-live="polite" id="live"></div>

<noscript><style>[hidden="until-found"] { content-visibility: visible !important; } article.dir-doc[hidden] { border:1.5px solid #E4E8EF; padding:24px 32px; margin-top:16px; } article.dir-doc.is-fdc[hidden] { border-style:dashed; }</style></noscript>

<script type="application/json" id="contrato-json">%%CONTRATO_JSON%%</script>
<script>
(function () {
  "use strict";
  /* Boot inteiro em try/catch: exceção => página degrada para documento completo legível (parecer técnico §2.4). */
  try {

  var docEl = document.documentElement;
  docEl.classList.add("js-on");

  var CONTRATO = JSON.parse(document.getElementById("contrato-json").textContent);

  /* Dado do contrato NUNCA entra em seletor: id com aspas montaria seletor inválido e
     derrubaria o boot inteiro. A busca é por comparação de atributo, em JavaScript. */
  function elemPorDado(seletor, atributo, valor) {
    var achados = document.querySelectorAll(seletor);
    for (var i = 0; i < achados.length; i++) {
      if (achados[i].getAttribute(atributo) === valor) return achados[i];
    }
    return null;
  }
  function elemsPorDado(seletor, atributo, valor) {
    var achados = document.querySelectorAll(seletor), fora = [];
    for (var i = 0; i < achados.length; i++) {
      if (achados[i].getAttribute(atributo) === valor) fora.push(achados[i]);
    }
    return fora;
  }
  var STORAGE_KEY = CONTRATO.export.chave_localstorage;
  var SCHEMA = CONTRATO.export.schema_version;
  var TAREFA = CONTRATO.tarefa_id;
  var CONTRACT_SHA = "%%CONTRATO_SHA%%";
  var DIRS = CONTRATO.direcoes;
  /* A letra é rótulo de apresentação: vem do contrato quando o autor a declara e, se não,
     sai da posição na lista. O documento embutido não a carrega — inventar dado que
     ninguém deu é justamente o que a decisão 19 proíbe. */
  function letraDe(d) {
    if (d && typeof d.letra === "string" && d.letra !== "") return d.letra;
    var i = DIRS.indexOf(d);
    return i >= 0 ? String.fromCharCode(65 + i) : "";
  }
  var VALID_IDS = DIRS.map(function (d) { return d.id; });
  var RECO = CONTRATO.recomendacao.direcao_id;
  var DIR_RECO = DIRS.filter(function (d) { return d.id === RECO; })[0];
  var TEXTO_SEM_ESCOLHA = "Nenhum caminho escolhido ainda." + (DIR_RECO
    ? " A recomendação (" + letraDe(DIR_RECO) + ") está destacada na tabela — aceitar custa um clique em “Escolher”."
    : "");
  var prefersReduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var coarsePointer = window.matchMedia && window.matchMedia("(pointer: coarse)").matches;

  function $(id) { return document.getElementById(id); }
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined && text !== null) n.textContent = text;
    return n;
  }
  function dirById(id) { return DIRS.filter(function (d) { return d.id === id; })[0] || null; }
  function dirIndex(id) { return VALID_IDS.indexOf(id); }
  function annotId() {
    if (window.crypto && typeof crypto.randomUUID === "function") { return "an-" + crypto.randomUUID().slice(0, 13); }
    return "an-" + Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
  }

  /* ===== Estado de trabalho (rascunho ≠ export; B1/B2 do parecer técnico) ===== */
  var state = { direcao_escolhida: null, comentario: "", dica_dispensada: false };
  var anotacoes = [];
  var storageOk = true;
  var persistTimer = null;

  function draftBlob() {
    return {
      rascunho_versao: 1,
      schema_export: SCHEMA,
      tarefa_id: TAREFA,
      contrato_sha256: CONTRACT_SHA,
      atualizado_em: new Date().toISOString(),
      estado: {
        direcao_escolhida: state.direcao_escolhida,
        comentario: state.comentario,
        dica_anotacao_dispensada: state.dica_dispensada
      },
      anotacoes: anotacoes
    };
  }
  function storageUI() {
    var alertBox = $("storage-alert");
    var note = $("autosave-note");
    if (storageOk) {
      alertBox.classList.remove("on"); alertBox.textContent = "";
      note.textContent = "O rascunho fica salvo automaticamente neste navegador. Esta página não executa nada — só registra a sua escolha.";
    } else {
      alertBox.classList.add("on");
      alertBox.textContent = "Atenção: o rascunho NÃO está sendo salvo neste navegador (armazenamento cheio ou bloqueado). Antes de fechar a página, copie ou baixe a sua resposta.";
      note.textContent = "O rascunho NÃO está sendo salvo neste navegador. Esta página não executa nada — só registra a sua escolha.";
    }
  }
  function persistNow() {
    if (persistTimer) { clearTimeout(persistTimer); persistTimer = null; }
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(draftBlob()));
      if (!storageOk) { storageOk = true; storageUI(); }
    } catch (e) {
      if (storageOk) { storageOk = false; storageUI(); }
    }
  }
  function schedulePersist() {
    if (persistTimer) clearTimeout(persistTimer);
    persistTimer = setTimeout(persistNow, 250);
  }
  document.addEventListener("visibilitychange", function () { if (document.visibilityState === "hidden" && persistTimer) persistNow(); });
  window.addEventListener("pagehide", function () { if (persistTimer) persistNow(); });

  /* Sonda de escrita no boot (B9): falha vira alerta visível, nunca catch mudo. */
  try { localStorage.setItem(STORAGE_KEY + ":probe", "1"); localStorage.removeItem(STORAGE_KEY + ":probe"); }
  catch (e) { storageOk = false; }

  function showDraftNotice(msg) {
    $("draft-notice-text").textContent = msg;
    $("draft-notice").hidden = false;
  }
  $("draft-notice-dismiss").addEventListener("click", function () { $("draft-notice").hidden = true; });

  /* Mesma régua do motor: o que não aparece para quem lê não conta como conteúdo.
     A regra é por categoria Unicode; se o navegador for antigo demais para entender
     categorias, degrada para espaço em branco em vez de quebrar a página. */
  var SEM_CONTEUDO = (function () {
    try { return new RegExp("[\\p{Cf}\\p{Cc}\\p{Z}]", "gu"); }
    catch (e) { return /\s/g; }
  })();
  function temConteudo(s) {
    return typeof s === "string" && s.replace(SEM_CONTEUDO, "") !== "";
  }

  /* Mesma régua do motor: NUL e CR o parser de HTML troca ou normaliza, e aí o id do
     JSON deixa de casar com o atributo no DOM; substituto solto nem chega a ser texto
     válido. Id assim não é preservável — o bilhete é, e ganha um id novo. */
  function idInternoEstavel(s) {
    if (!temConteudo(s) || s.indexOf(String.fromCharCode(0)) !== -1 ||
        s.indexOf(String.fromCharCode(13)) !== -1) return false;
    for (var i = 0; i < s.length; i++) {
      var unidade = s.charCodeAt(i);
      if (unidade >= 0xD800 && unidade <= 0xDBFF) {
        if (i + 1 >= s.length) return false;
        var seguinte = s.charCodeAt(i + 1);
        if (seguinte < 0xDC00 || seguinte > 0xDFFF) return false;
        i++;
      } else if (unidade >= 0xDC00 && unidade <= 0xDFFF) return false;
    }
    return true;
  }

  function sanitizarAnotacoes(lista) {
    /* Dois bilhetes com o mesmo id viram um só no export, e o motor reprova id repetido.
       Quem chegou depois recebe id novo — ninguém é descartado por causa disso. */
    var vistos = Object.create(null);
    return (Array.isArray(lista) ? lista : []).map(sanitizeAnnot).filter(Boolean)
      .map(function (a) {
        while (Object.prototype.hasOwnProperty.call(vistos, a.id)) a.id = annotId();
        vistos[a.id] = true;
        return a;
      });
  }

  function sanitizeAnnot(a) {
    /* Decisão 17: nada que o usuário escreveu é jogado fora sem ele mandar. Anotação
       que perdeu o trecho OU a âncora volta marcada como incompleta e vai para a fila
       de "manter ou jogar fora". Só some se não houver nada humano a preservar. */
    if (!a || typeof a !== "object") return null;
    var temBloco = temConteudo(a.bloco_id);
    var temTrecho = temConteudo(a.trecho);
    /* O comentário pode ficar em branco — a própria interface promete isso, porque o
       marcador sobre o trecho já vale por si. Some só o que não tem nada humano dentro:
       nem bilhete, nem trecho, nem âncora. (auditoria cega, P2/item 3) */
    if (!temConteudo(a.comentario) && !temBloco && !temTrecho) return null;
    return {
      id: idInternoEstavel(a.id) ? a.id : annotId(),
      item_id: typeof a.item_id === "string" ? a.item_id : null,
      bloco_id: temBloco ? a.bloco_id : "",
      ancora_tipo: a.ancora_tipo === "bloco" ? "bloco" : "trecho",
      ancora_status: a.ancora_status === "orfa" || a.ancora_status === "truncada" ? a.ancora_status : "resolvida",
      ancora_truncada: !!a.ancora_truncada,
      trecho: temTrecho ? a.trecho : "",
      incompleta: !(temBloco && temTrecho),
      resolucao: a.resolucao === "manter" ? "manter" : null,
      prefixo: typeof a.prefixo === "string" ? a.prefixo : "",
      sufixo: typeof a.sufixo === "string" ? a.sufixo : "",
      inicio: typeof a.inicio === "number" ? a.inicio : 0,
      fim: typeof a.fim === "number" ? a.fim : 0,
      comentario: a.comentario,
      criado_em: typeof a.criado_em === "string" ? a.criado_em : "",
      forced_orfa: !!a.forced_orfa
    };
  }

  /* Restauração: nunca descarta em silêncio (parecer técnico §5.4). */
  function restore() {
    var raw = null;
    try { raw = localStorage.getItem(STORAGE_KEY); } catch (e) { return; }
    if (!raw) return;
    var saved = null;
    try { saved = JSON.parse(raw); } catch (e) {
      try { localStorage.setItem(STORAGE_KEY + ":backup:ilegivel", raw); } catch (e2) {}
      showDraftNotice("Encontrei um rascunho antigo que não consegui ler. Ele ficou guardado como cópia de segurança neste navegador; nada foi apagado.");
      return;
    }
    if (!saved || typeof saved !== "object") return;
    if (saved.rascunho_versao === 1 && saved.schema_export === SCHEMA && saved.tarefa_id === TAREFA) {
      var est = saved.estado || {};
      if (VALID_IDS.indexOf(est.direcao_escolhida) !== -1) state.direcao_escolhida = est.direcao_escolhida;
      if (typeof est.comentario === "string") state.comentario = est.comentario;
      state.dica_dispensada = !!est.dica_anotacao_dispensada;
      if (Array.isArray(saved.anotacoes)) {
        anotacoes = sanitizarAnotacoes(saved.anotacoes);
      }
      if (saved.contrato_sha256 !== CONTRACT_SHA) {
        anotacoes.forEach(function (a) { a.forced_orfa = true; a.ancora_status = "orfa"; });
        showDraftNotice("Este relatório foi atualizado desde o seu último rascunho. Suas anotações foram preservadas, mas os trechos podem ter mudado de lugar — elas aparecem no painel como “trecho não encontrado nesta versão”.");
      }
      return;
    }
    /* Rascunho de versão anterior (ex.: v1): guarda cópia, migra só o que é confiável. */
    var schemaAntigo = saved.schema_export || saved.schema_version || "desconhecido";
    try { localStorage.setItem(STORAGE_KEY + ":backup:" + schemaAntigo, raw); } catch (e3) {}
    var comentAntigo = "";
    if (typeof saved.comentario === "string") comentAntigo = saved.comentario;
    else if (saved.estado && typeof saved.estado.comentario === "string") comentAntigo = saved.estado.comentario;
    if (comentAntigo) state.comentario = comentAntigo;
    showDraftNotice("Encontrei um rascunho de uma versão anterior desta página. Recuperei o seu comentário; a escolha de caminho precisa ser confirmada de novo, porque a versão antiga não distinguia escolha sua de sugestão minha. O rascunho antigo ficou guardado, nada foi apagado.");
  }

  /* ===== Export = função pura do rascunho (sem new Date aqui dentro; B12) ===== */
  function exportAnnot(a, momentoISO) {
    /* Decisão 17: anotação que voltou incompleta do rascunho e o usuário mandou MANTER
       sai marcada como órfã, com trecho-marcador literal. Nada é descartado sozinho. */
    var trecho = a.trecho;
    var bloco = a.bloco_id;
    var status = a.ancora_status;
    var criado = a.criado_em;
    if (a.incompleta) {
      if (!trecho) trecho = TRECHO_NAO_RECUPERADO;
      if (!bloco) bloco = BLOCO_NAO_RECUPERADO;
      status = "orfa";
      if (!criado || criado.length < 10) criado = momentoISO || new Date().toISOString();
    }
    return { id: a.id, item_id: a.item_id, bloco_id: bloco, ancora_tipo: a.ancora_tipo,
      ancora_status: status, trecho: trecho, prefixo: a.prefixo, sufixo: a.sufixo,
      inicio: a.inicio, fim: a.fim, comentario: a.comentario, criado_em: criado };
  }
  /* ===== Decisão 17 (2026-08-20): rascunho restaurado com anotação incompleta
     trava o envio até você decidir, uma a uma. O sistema nunca descarta sozinho. ===== */
  var TRECHO_NAO_RECUPERADO = "(trecho não recuperado do rascunho)";
  var BLOCO_NAO_RECUPERADO = "(bloco não recuperado do rascunho)";

  function escTexto(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  function anotacoesPendentes() {
    return anotacoes.filter(function (a) { return a.incompleta && a.resolucao !== "manter"; });
  }
  function resolverAnotacao(id, decisao) {
    for (var i = 0; i < anotacoes.length; i++) {
      if (anotacoes[i].id !== id) continue;
      if (decisao === "descartar") anotacoes.splice(i, 1);   /* só com clique seu */
      else anotacoes[i].resolucao = "manter";
      break;
    }
    persistNow();
    pintarAnotacoesIncompletas();
    syncAnnotUI();
  }
  /* ————— limite de texto: preservar o que o usuário escreveu, travar o envio —————
     O atributo maxlength só limita quem DIGITA. Um rascunho gravado por uma versão
     anterior da página volta inteiro quando o JavaScript atribui `.value`, e aí o export
     saía maior do que o contrato aceita. Truncar em silêncio seria jogar fora texto que a
     pessoa escreveu — o oposto da decisão 17.

     Então: o texto fica, o envio trava, a página diz QUAL campo encolher e leva até ele.
     Toda trava que o usuário causa precisa de destrava que ele mesmo alcance — por isso
     `atualizarTravas()` roda a cada tecla, e a anotação restaurada ganhou editor. */
  var LIMITES_DE_TEXTO = %%LIMITES_DE_TEXTO%%;
  function conferirLimite(lista, rotulo, texto, limite, alvo) {
    var t = typeof texto === "string" ? texto : "";
    if (t.length > limite) {
      lista.push({ rotulo: rotulo, excesso: t.length - limite, tamanho: t.length,
                   limite: limite, alvo: alvo });
    }
  }
  function pintarCamposEstourados() {
    var caixa = document.getElementById("campos-estourados");
    if (!caixa) return;
    var estourados = camposEstourados();
    caixa.hidden = estourados.length === 0;
    if (!estourados.length) { caixa.innerHTML = ""; return; }
    var partes = ['<h3 class="ai-title">Antes de enviar: ' + estourados.length +
      (estourados.length === 1 ? " campo passou" : " campos passaram") +
      ' do tamanho máximo</h3>' +
      '<p class="ai-sub">O que você escreveu está inteiro e continua guardado — nada foi ' +
      'cortado. Só não cabe no formato da resposta. Use “Encurtar” para ir até o campo; ' +
      'assim que ele couber, o envio volta a ficar disponível.</p>'];
    estourados.forEach(function (c, i) {
      partes.push('<div class="ai-item"><blockquote>' + escTexto(c.rotulo) +
        ' — ' + c.tamanho + ' caracteres, ' + c.excesso + ' a mais do que cabe (' +
        c.limite + ')</blockquote><div class="ai-acoes">' +
        '<button type="button" class="btn btn-primary" data-encurtar="' + i +
        '">Encurtar este campo</button></div></div>');
    });
    caixa.innerHTML = partes.join("");
    /* sem isto o aviso promete e não cumpre: o botão nasce e nada acontece ao clicar */
    var gatilhos = caixa.querySelectorAll("[data-encurtar]");
    Array.prototype.forEach.call(gatilhos, function (botao) {
      botao.addEventListener("click", function () {
        var i = parseInt(botao.getAttribute("data-encurtar"), 10);
        irParaCampoEstourado(estourados[i] && estourados[i].alvo);
      });
    });
  }
  function irParaCampoEstourado(alvo) {
    if (!alvo) return;
    if (alvo.tipo === "anotacao") { abrirEdicaoDaAnotacao(alvo.id); return; }
    var campo = document.getElementById(alvo.id);
    if (campo) { campo.focus(); if (campo.scrollIntoView) campo.scrollIntoView(); }
  }
  function envioTravado() {
    return anotacoesPendentes().length > 0 || camposEstourados().length > 0;
  }

  function camposEstourados() {
    var lista = [];
    conferirLimite(lista, "Seu comentário sobre a decisão", state.comentario,
                   LIMITES_DE_TEXTO.comentario, { tipo: "campo", id: "comentario" });
    anotacoes.forEach(function (a, i) {
      conferirLimite(lista, "Anotação " + (i + 1) + " (“" +
        String(a.trecho || "").slice(0, 30) + "”)", a.comentario,
        LIMITES_DE_TEXTO.anotacao, { tipo: "anotacao", id: a.id });
    });
    return lista;
  }
  function anotacaoPorId(id) {
    return anotacoes.filter(function (a) { return a.id === id; })[0] || null;
  }
  function editarAnotacao(id, texto) {
    var a = anotacaoPorId(id);
    if (!a) return false;
    a.comentario = typeof texto === "string" ? texto : a.comentario;
    persistNow();
    atualizarTravas();
    renderPanel();
    return true;
  }
  function abrirEdicaoDaAnotacao(id) {
    openPanel(id);
    /* id de anotação vem do rascunho: comparar atributo, nunca montar seletor com ele */
    var campo = elemPorDado("textarea[data-editar-anotacao]", "data-editar-anotacao", id);
    if (campo && campo.focus) campo.focus();
  }
  function atualizarTravas() {
    pintarCamposEstourados();
    var travado = envioTravado();
    $("btn-copy-json").disabled = travado;
    $("btn-download-json").disabled = travado;
  }
  function aoDigitarNoCampoPrincipal() {
    state.comentario = comentario.value;
    autogrow(comentario);
    atualizarTravas();
    schedulePersist();
  }

  function pintarAnotacoesIncompletas() {
    var caixa = $("anotacoes-incompletas");
    if (!caixa) return;
    var pendentes = anotacoesPendentes();
    caixa.hidden = pendentes.length === 0;
    atualizarTravas();
    if (!pendentes.length) { caixa.innerHTML = ""; return; }
    var partes = ['<h3 class="ai-title">Antes de enviar: ' + pendentes.length +
      (pendentes.length === 1 ? " anotação precisa" : " anotações precisam") +
      ' da sua decisão</h3>' +
      '<p class="ai-sub">Estas anotações voltaram do rascunho sem o trecho a que estavam ' +
      'presas — o texto da página mudou desde que você as escreveu. O seu comentário está ' +
      'inteiro. Diga o que fazer com cada uma; nada é jogado fora sem você mandar.</p>'];
    pendentes.forEach(function (a) {
      partes.push('<div class="ai-item"><blockquote>' + escTexto(a.comentario) +
        '</blockquote><div class="ai-acoes">' +
        '<button type="button" class="btn btn-primary" data-manter="' + escTexto(a.id) +
        '">Manter a anotação</button>' +
        '<button type="button" class="btn btn-secondary" data-descartar="' + escTexto(a.id) +
        '">Jogar fora</button></div></div>');
    });
    caixa.innerHTML = partes.join("");
    Array.prototype.forEach.call(caixa.querySelectorAll("[data-manter]"), function (b) {
      b.addEventListener("click", function () { resolverAnotacao(b.getAttribute("data-manter"), "manter"); });
    });
    Array.prototype.forEach.call(caixa.querySelectorAll("[data-descartar]"), function (b) {
      b.addEventListener("click", function () { resolverAnotacao(b.getAttribute("data-descartar"), "descartar"); });
    });
  }

  function buildExport(momentoISO) {
    return {
      schema_version: SCHEMA,
      tarefa_id: TAREFA,
      gerado_em: momentoISO,
      /* decisão 20: a resposta carrega a impressão digital do formulário que foi lido —
         se o relatório mudar depois, o motor percebe e bloqueia em vez de reinterpretar */
      contrato_sha256: CONTRACT_SHA,
      produzido_por: { agente: "usuario" },
      estado: state.direcao_escolhida ? "decidida" : "pendente",
      direcao_escolhida: state.direcao_escolhida,
      comentario: state.comentario,
      anotacoes: anotacoes.map(function (a) { return exportAnnot(a, momentoISO); })
    };
  }

  /* ===== Blocos anotáveis: snapshot pristino ANTES de qualquer marcador (B11) ===== */
  var blocks = {};
  Array.prototype.forEach.call(document.querySelectorAll("[data-anotavel]"), function (b) {
    blocks[b.getAttribute("data-anotavel")] = { el: b, pristine: b.textContent, item: b.getAttribute("data-item") || null };
  });

  /* ===== Feedback / aria-live ===== */
  function feedback(msg, isWarn) {
    var node = $("copy-feedback");
    node.textContent = msg;
    node.style.color = isWarn ? "var(--warn-ink)" : "var(--ok-ink)";
  }
  function announce(msg) { $("live").textContent = msg; }

  /* ===== Escolha (sem decisão fantasma: só ação do usuário grava; B1) ===== */
  function escolher(id, origem) {
    if (VALID_IDS.indexOf(id) === -1) return;
    state.direcao_escolhida = id;
    persistNow();
    syncChoiceView();
    var d = dirById(id);
    announce("Caminho " + letraDe(d) + " escolhido: " + d.nome + ".");
    feedback("Escolha salva no rascunho: " + letraDe(d) + " — " + d.nome + ".");
    if (origem === "wizard") { closeWizard(); }
  }
  function desfazerEscolha() {
    state.direcao_escolhida = null;
    persistNow();
    syncChoiceView();
    announce("Escolha desfeita. Nenhum caminho gravado.");
    feedback("Escolha desfeita — o relatório voltou para pendente.", true);
  }
  function pulseRow(id) {
    var tr = elemPorDado("tr.dir-row", "data-dir-id", id);
    if (!tr) return;
    tr.classList.remove("pulse");
    void tr.offsetWidth;
    tr.classList.add("pulse");
  }
  function syncChoiceView() {
    var chosen = state.direcao_escolhida;
    var d = chosen ? dirById(chosen) : null;
    DIRS.forEach(function (dir) {
      var on = dir.id === chosen;
      var tr = elemPorDado("tr.dir-row", "data-dir-id", dir.id);
      if (tr) tr.classList.toggle("row-chosen", on);
      var art = $("doc-" + dir.id);
      if (art) art.classList.toggle("doc-chosen", on);
      Array.prototype.forEach.call(elemsPorDado(".btn-choose", "data-dir-id", dir.id), function (b) {
        b.classList.toggle("is-chosen", on);
        b.textContent = on ? "Sua escolha" : "Escolher";
        if (b.classList.contains("btn-choose-doc")) b.textContent = on ? "Sua escolha" : "Escolher este caminho";
        b.setAttribute("aria-pressed", on ? "true" : "false");
      });
    });
    $("export-count").textContent = d
      ? ("Você escolheu: " + letraDe(d) + " — " + d.nome)
      : "Nenhum caminho escolhido ainda — a recomendação está destacada, mas nada foi gravado";
    $("progress-fill").style.width = d ? "100%" : "0";
    var chip = $("confer-chip");
    chip.classList.toggle("ok", !!d);
    chip.textContent = d ? "Decidido" : "Falta decidir";
    $("confer-text").textContent = d
      ? ("Você escolheu: " + letraDe(d) + " — " + d.nome + ". Se mudar de ideia, é só escolher outro caminho.")
      : TEXTO_SEM_ESCOLHA;
    $("btn-undo").hidden = !d;
    if (wizard.open && currentDirId) syncWizardFoot();
  }
  $("btn-undo").addEventListener("click", desfazerEscolha);

  /* Guarda B5: arrasto de seleção que termina sobre um controle não pode virar clique de decisão. */
  document.addEventListener("click", function (e) {
    var alvo = e.target.closest ? e.target.closest(".btn-choose, tr.dir-row") : null;
    if (!alvo) return;
    var sel = window.getSelection();
    if (sel && !sel.isCollapsed && sel.toString().length > 0) { e.preventDefault(); e.stopPropagation(); }
  }, true);

  Array.prototype.forEach.call(document.querySelectorAll(".btn-choose"), function (b) {
    b.addEventListener("click", function (e) {
      e.stopPropagation();
      var id = b.getAttribute("data-dir-id");
      if (state.direcao_escolhida === id) {
        feedback("Este já é o seu caminho escolhido. Para trocar, escolha outro; para desfazer, use “Desfazer minha escolha” na conferência.");
        return;
      }
      escolher(id, b.getAttribute("data-source") || "tabela");
      pulseRow(id);
    });
  });

  /* ===== Linhas da tabela abrem o wizard ===== */
  Array.prototype.forEach.call(document.querySelectorAll("tr.dir-row"), function (tr) {
    tr.addEventListener("click", function (e) {
      if (e.target.closest("button, a, input, label, mark, .annot-badge")) return;
      var sel = window.getSelection();
      if (sel && !sel.isCollapsed && sel.toString().length > 0) return;
      openWizard(tr.getAttribute("data-dir-id"), tr.querySelector(".row-open"));
    });
  });
  Array.prototype.forEach.call(document.querySelectorAll(".row-open"), function (b) {
    b.addEventListener("click", function (e) {
      e.stopPropagation();
      openWizard(b.getAttribute("data-dir-id"), b);
    });
  });

  /* ===== Wizard: um único dialog, conteúdo trocado por adoção do markup real (B4/B7) ===== */
  var wizard = $("wizard");
  var wizBody = $("wiz-body");
  var wizTitle = $("wiz-title");
  var currentDirId = null;
  var openerEl = null;
  var lastOpenedId = null;

  function lockScroll() { docEl.style.overflow = "hidden"; }
  function unlockScroll() { docEl.style.overflow = ""; }

  function restoreBody() {
    if (!currentDirId) return;
    var art = $("doc-" + currentDirId);
    var body = $("body-" + currentDirId);
    if (art && body && body.parentNode !== art) art.appendChild(body);
    currentDirId = null;
  }
  function mountDir(id) {
    restoreBody();
    var d = dirById(id);
    var body = $("body-" + id);
    $("wiz-pill").textContent = letraDe(d);
    $("wiz-eyebrow").textContent = "Caminho " + letraDe(d) + " · " + (dirIndex(id) + 1) + " de " + DIRS.length + " · " + d.origem_leiga;
    wizTitle.textContent = d.nome;
    var badges = $("wiz-badges");
    badges.textContent = "";
    if (d.recomendada) badges.appendChild(el("span", "badge-reco", "Recomendado"));
    if (d.fora_da_caixa) badges.appendChild(el("span", "badge-fdc", "Fora da caixa"));
    wizBody.appendChild(body);
    currentDirId = id;
    lastOpenedId = id;
    wizBody.scrollTop = 0;
    syncWizardFoot();
  }
  function syncWizardFoot() {
    var idx = dirIndex(currentDirId);
    $("wiz-prev").disabled = idx <= 0;
    $("wiz-next").disabled = idx >= DIRS.length - 1;
    var segs = $("wiz-segs");
    segs.textContent = "";
    DIRS.forEach(function (d, i) {
      var s = el("button", "seg" + (i === idx ? " cur" : "") + (d.id === state.direcao_escolhida ? " chosen" : ""));
      s.type = "button";
      s.setAttribute("aria-label", "Ir para o caminho " + letraDe(d) + " — " + d.nome + (d.id === state.direcao_escolhida ? " (sua escolha)" : ""));
      s.addEventListener("click", function () { swapTo(d.id); });
      segs.appendChild(s);
    });
    var btn = $("wiz-choose");
    var isChosen = state.direcao_escolhida === currentDirId;
    btn.classList.toggle("is-chosen", isChosen);
    btn.textContent = isChosen ? "Sua escolha ✓ — voltar à lista" : "Escolher este caminho";
  }
  var swapTimer = null;
  function swapTo(id) {
    if (!wizard.open || id === currentDirId) return;
    if (prefersReduced) {
      mountDir(id); wizTitle.focus();
      announce("Caminho " + letraDe(dirById(id)) + ": " + dirById(id).nome);
      return;
    }
    wizBody.style.opacity = "0";
    if (swapTimer) clearTimeout(swapTimer);
    swapTimer = setTimeout(function () {
      swapTimer = null;
      if (!wizard.open) { wizBody.style.opacity = "1"; return; } /* fechou durante o cross-fade: não montar no dialog fechado (P1-2) */
      mountDir(id);
      wizBody.style.opacity = "1";
      wizTitle.focus();
      announce("Caminho " + letraDe(dirById(id)) + ": " + dirById(id).nome);
    }, 120);
  }
  function openWizard(id, opener) {
    if (VALID_IDS.indexOf(id) === -1) return;
    closePanel();
    closePopover(false);
    hideSelToolbar();
    if ($("info-dialog").open) $("info-dialog").close();
    if (wizard.open) { swapTo(id); return; }
    openerEl = opener || document.activeElement;
    mountDir(id);
    lockScroll();
    wizard.showModal();
    wizTitle.focus(); /* foco no título, nunca no primeiro botão (B10) */
  }
  function closeWizard() { if (wizard.open) wizard.close(); }
  wizard.addEventListener("close", function () {
    /* nunca persistir estado aqui (evento close é assíncrono — B4); só devolver o markup e o foco */
    if (swapTimer) { clearTimeout(swapTimer); swapTimer = null; }
    wizBody.style.opacity = "1";
    restoreBody();
    unlockScroll();
    if (openerEl) { try { openerEl.focus(); } catch (e) {} openerEl = null; }
    if (lastOpenedId) pulseRow(lastOpenedId);
  });
  /* Fechar pelo fundo exige mousedown E mouseup no fundo (B3: arrasto de seleção não fecha). */
  var downOnBackdrop = false;
  wizard.addEventListener("pointerdown", function (e) { downOnBackdrop = (e.target === wizard); });
  wizard.addEventListener("click", function (e) { if (e.target === wizard && downOnBackdrop) { downOnBackdrop = false; closeWizard(); } });
  $("wiz-close").addEventListener("click", closeWizard);
  $("wiz-prev").addEventListener("click", function () { var i = dirIndex(currentDirId); if (i > 0) swapTo(VALID_IDS[i - 1]); });
  $("wiz-next").addEventListener("click", function () { var i = dirIndex(currentDirId); if (i < DIRS.length - 1) swapTo(VALID_IDS[i + 1]); });
  $("wiz-choose").addEventListener("click", function () {
    if (state.direcao_escolhida === currentDirId) { closeWizard(); return; }
    escolher(currentDirId, "wizard");
  });

  /* ===== Dialog "como funciona" ===== */
  var infoDialog = $("info-dialog");
  var infoDown = false;
  $("btn-info").addEventListener("click", function () {
    closeWizard(); closePanel();
    lockScroll();
    infoDialog.showModal();
    $("info-title").focus();
  });
  infoDialog.addEventListener("close", unlockScroll);
  infoDialog.addEventListener("pointerdown", function (e) { infoDown = (e.target === infoDialog); });
  infoDialog.addEventListener("click", function (e) { if (e.target === infoDialog && infoDown) { infoDown = false; infoDialog.close(); } });
  $("info-close").addEventListener("click", function () { infoDialog.close(); });

  /* ===== Modo documento + revelação por busca (Ctrl+F acha via hidden=until-found; B7) ===== */
  var docModeOn = false;
  var artigos = Array.prototype.slice.call(document.querySelectorAll("article.dir-doc"));
  function setDocMode(on) {
    docModeOn = on;
    artigos.forEach(function (a) {
      if (on) a.removeAttribute("hidden");
      else a.setAttribute("hidden", "until-found");
    });
    $("btn-doc-mode").textContent = on ? "Voltar ao modo compacto" : "Ver tudo como documento";
    $("doc-sub").textContent = on
      ? "Página corrida com tudo aberto — para ler de uma vez, imprimir ou buscar (Ctrl+F). Escolher funciona aqui também."
      : "É o mesmo conteúdo que abre ao tocar num caminho da tabela, em página corrida — para ler tudo de uma vez, imprimir ou buscar (Ctrl+F). Escolher funciona aqui também.";
  }
  $("btn-doc-mode").addEventListener("click", function () {
    setDocMode(!docModeOn);
    if (docModeOn) document.querySelector(".documento").scrollIntoView({ block: "start" });
  });
  artigos.forEach(function (a) {
    a.addEventListener("beforematch", function () { a.removeAttribute("hidden"); });
  });
  window.addEventListener("beforeprint", function () { closeWizard(); });

  /* ===== Menu de contexto: atalho, nunca sequestro (B6) ===== */
  document.addEventListener("contextmenu", function (e) {
    if (e.target.closest && e.target.closest("input, textarea, select, [contenteditable]")) return;
    var sel = window.getSelection();
    if (!sel || sel.isCollapsed || !sel.toString().trim()) return;
    var cap = captureSelection();
    if (!cap) return;
    e.preventDefault();
    pendingCapture = cap;
    showSelToolbarAt(e.clientX, e.clientY - 56, cap.inDialog);
  });

  /* ===== Anotações: captura congelada no instante da seleção (B8) ===== */
  var pendingCapture = null;
  var activeCapture = null;
  var selDebounce = null;

  function blockOf(node) {
    var eln = node ? (node.nodeType === 1 ? node : node.parentNode) : null;
    if (!eln || !eln.closest) return null;
    if (eln.closest("input, textarea, select, [contenteditable]")) return null;
    return eln.closest("[data-anotavel]");
  }
  function offsetInBlock(blockEl, container, offset) {
    var r = document.createRange();
    r.selectNodeContents(blockEl);
    try { r.setEnd(container, offset); } catch (e) { return null; }
    return r.toString().length;
  }
  function captureSelection() {
    var sel = window.getSelection();
    if (!sel || sel.rangeCount === 0 || sel.isCollapsed) return null;
    var range = sel.getRangeAt(0);
    var startBlock = blockOf(range.startContainer);
    if (!startBlock) return null;
    var bid = startBlock.getAttribute("data-anotavel");
    var blk = blocks[bid];
    if (!blk) return null;
    var pris = blk.pristine;
    var inicio = offsetInBlock(startBlock, range.startContainer, range.startOffset);
    if (inicio === null) return null;
    var endBlock = blockOf(range.endContainer);
    var truncada = false, fim;
    if (endBlock !== startBlock) { fim = pris.length; truncada = true; }
    else {
      fim = offsetInBlock(startBlock, range.endContainer, range.endOffset);
      if (fim === null) return null;
    }
    if (fim <= inicio) return null;
    if (fim - inicio > 300) { fim = inicio + 300; truncada = true; }
    var trecho = pris.slice(inicio, fim);
    if (!trecho.trim()) return null;
    var rect = range.getBoundingClientRect();
    return {
      bloco_id: bid, item_id: blk.item, ancora_tipo: "trecho",
      trecho: trecho,
      prefixo: pris.slice(Math.max(0, inicio - 32), inicio),
      sufixo: pris.slice(fim, Math.min(pris.length, fim + 32)),
      inicio: inicio, fim: fim, truncada: truncada,
      rect: { left: rect.left, top: rect.top, width: rect.width, height: rect.height, bottom: rect.bottom },
      inDialog: !!startBlock.closest("dialog[open]")
    };
  }

  var selToolbar = $("sel-toolbar");
  function hideSelToolbar() { selToolbar.hidden = true; $("btn-annot-sel").hidden = true; }
  function showSelToolbarAt(x, y, inDialog) {
    (inDialog && wizard.open ? wizard : document.body).appendChild(selToolbar);
    selToolbar.hidden = false;
    var w = selToolbar.offsetWidth || 96;
    var left = Math.max(8, Math.min(x - w / 2, window.innerWidth - w - 8));
    var top = Math.max(8, y);
    selToolbar.style.left = left + "px";
    selToolbar.style.top = top + "px";
  }
  function updateSelUI() {
    pendingCapture = captureSelection();
    if (!pendingCapture) { hideSelToolbar(); return; }
    if (coarsePointer) {
      /* toque: sem disputa com o callout nativo — botão fixo na barra (parecer técnico §4.2.3) */
      selToolbar.hidden = true;
      $("btn-annot-sel").hidden = false;
    } else {
      var r = pendingCapture.rect;
      showSelToolbarAt(r.left + r.width / 2, r.top - 52, pendingCapture.inDialog);
      $("btn-annot-sel").hidden = true;
    }
  }
  document.addEventListener("selectionchange", function () {
    if (selDebounce) clearTimeout(selDebounce);
    selDebounce = setTimeout(updateSelUI, 140);
  });

  /* Captura no pointerdown, antes de a seleção evaporar (B8). */
  function armAnnotTrigger(btn) {
    btn.addEventListener("pointerdown", function (e) {
      e.preventDefault();
      if (pendingCapture) openPopover(pendingCapture);
    });
    btn.addEventListener("click", function () {
      if ($("annot-pop").hidden && pendingCapture) openPopover(pendingCapture);
    });
  }
  armAnnotTrigger($("sel-annotate"));
  armAnnotTrigger($("btn-annot-sel"));

  /* Porta de teclado/leitor de tela: anotar o bloco inteiro (parecer técnico §4.2.5). */
  Array.prototype.forEach.call(document.querySelectorAll(".annot-block-btn"), function (btn) {
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var bid = btn.getAttribute("data-bloco");
      var blk = blocks[bid];
      if (!blk) return;
      var pris = blk.pristine;
      var fim = Math.min(pris.length, 300);
      openPopover({
        bloco_id: bid, item_id: blk.item, ancora_tipo: "bloco",
        trecho: pris.slice(0, fim), prefixo: "", sufixo: "",
        inicio: 0, fim: fim, truncada: false,
        rect: btn.getBoundingClientRect(),
        inDialog: !!btn.closest("dialog[open]")
      });
    });
  });

  var annotPop = $("annot-pop");
  function openPopover(cap) {
    activeCapture = cap;
    hideSelToolbar();
    (cap.inDialog && wizard.open ? wizard : document.body).appendChild(annotPop);
    $("annot-pop-quote").textContent = "“" + cap.trecho + "”";
    $("annot-pop-note").hidden = !cap.truncada;
    $("annot-pop-text").value = "";
    annotPop.hidden = false;
    annotPop.classList.toggle("sheet", coarsePointer);
    if (!coarsePointer) {
      var w = annotPop.offsetWidth || 340;
      var h = annotPop.offsetHeight || 220;
      var left = Math.max(8, Math.min(cap.rect.left, window.innerWidth - w - 8));
      var top = cap.rect.bottom + 8;
      if (top + h > window.innerHeight - 8) top = cap.rect.top - h - 8;
      top = Math.max(8, Math.min(top, window.innerHeight - h - 8));
      annotPop.style.left = left + "px";
      annotPop.style.top = top + "px";
    }
    $("annot-pop-text").focus();
  }
  function closePopover(refocus) {
    annotPop.hidden = true;
    activeCapture = null;
    if (refocus) { try { document.body.focus(); } catch (e) {} }
  }
  $("annot-pop-cancel").addEventListener("click", function () { closePopover(false); });
  function savePopover() {
    if (!activeCapture) { closePopover(false); return; }
    var cap = activeCapture;
    var rec = {
      id: annotId(), item_id: cap.item_id, bloco_id: cap.bloco_id,
      ancora_tipo: cap.ancora_tipo,
      ancora_status: cap.truncada ? "truncada" : "resolvida",
      ancora_truncada: !!cap.truncada,
      trecho: cap.trecho, prefixo: cap.prefixo, sufixo: cap.sufixo,
      inicio: cap.inicio, fim: cap.fim,
      comentario: $("annot-pop-text").value,
      criado_em: new Date().toISOString(),
      forced_orfa: false
    };
    anotacoes.push(rec);
    persistNow();
    paintAll();
    syncAnnotUI();
    closePopover(false);
    announce("Anotação salva.");
    feedback("Anotação salva no rascunho — ela vai junto na resposta.");
  }
  $("annot-pop-save").addEventListener("click", savePopover);
  /* Esc nunca descarta: com o popover aberto, o primeiro Esc salva o bilhete e fecha só o popover (P2-1) */
  wizard.addEventListener("cancel", function (e) {
    if (!annotPop.hidden) { e.preventDefault(); savePopover(); }
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !annotPop.hidden && !wizard.open) { savePopover(); }
  });

  /* ===== Pintura dos marcadores: resolver TODAS as âncoras sobre o texto pristino, depois pintar (B11) ===== */
  function clearMarks() {
    Array.prototype.forEach.call(document.querySelectorAll("mark.annot"), function (m) {
      var p = m.parentNode;
      while (m.firstChild) p.insertBefore(m.firstChild, m);
      p.removeChild(m);
    });
    Array.prototype.forEach.call(document.querySelectorAll(".annot-badge"), function (b) { b.remove(); });
    Object.keys(blocks).forEach(function (bid) {
      blocks[bid].el.normalize();
      blocks[bid].el.classList.remove("has-block-annot");
    });
  }
  function resolveAnchor(a) {
    var blk = blocks[a.bloco_id];
    if (!blk || a.forced_orfa) return null;
    if (a.ancora_tipo === "bloco") return { tipo: "bloco" };
    var pris = blk.pristine;
    if (!a.trecho) return null;
    if (pris.slice(a.inicio, a.fim) === a.trecho) return { inicio: a.inicio, fim: a.fim };
    var winStart = Math.max(0, a.inicio - 200);
    var idx = pris.indexOf(a.trecho, winStart);
    if (idx !== -1 && idx <= a.inicio + 200) return { inicio: idx, fim: idx + a.trecho.length };
    var first = pris.indexOf(a.trecho);
    if (first !== -1 && pris.indexOf(a.trecho, first + 1) === -1) return { inicio: first, fim: first + a.trecho.length };
    return null;
  }
  function wrapSegment(blockEl, seg) {
    var walker = document.createTreeWalker(blockEl, NodeFilter.SHOW_TEXT, null);
    var pos = 0, n, targets = [];
    while ((n = walker.nextNode())) {
      var len = n.nodeValue.length;
      var ns = pos, ne = pos + len;
      var s = Math.max(seg.s, ns), e = Math.min(seg.e, ne);
      if (s < e) targets.push({ node: n, start: s - ns, end: e - ns });
      pos = ne;
      if (ne >= seg.e) break;
    }
    targets.forEach(function (t, idx) {
      var target = t.node;
      if (t.start > 0) target = target.splitText(t.start);
      if (t.end - t.start < target.nodeValue.length) target.splitText(t.end - t.start);
      var mark = document.createElement("mark");
      mark.className = "annot" +
        (seg.starts && idx === 0 ? " annot-start" : "") +
        (seg.ends && idx === targets.length - 1 ? " annot-end" : "");
      mark.setAttribute("data-annot-ids", seg.ids.join(" "));
      target.parentNode.insertBefore(mark, target);
      mark.appendChild(target);
    });
  }
  function paintBlock(blockEl, items) {
    var bounds = [];
    items.forEach(function (it) { bounds.push(it.inicio, it.fim); });
    bounds = bounds.filter(function (v, i, arr) { return arr.indexOf(v) === i; }).sort(function (a, b) { return a - b; });
    var segs = [];
    for (var i = 0; i < bounds.length - 1; i++) {
      var s = bounds[i], e = bounds[i + 1];
      var cover = items.filter(function (it) { return it.inicio <= s && it.fim >= e; });
      if (!cover.length) continue;
      segs.push({
        s: s, e: e,
        ids: cover.map(function (c) { return c.a.id; }),
        starts: cover.some(function (c) { return c.inicio === s; }),
        ends: cover.some(function (c) { return c.fim === e; })
      });
    }
    segs.forEach(function (seg) { wrapSegment(blockEl, seg); });
    /* badge de contagem no fim de cada trecho (soma quando coincide o ponto final) */
    var lastMark = {};
    Array.prototype.forEach.call(blockEl.querySelectorAll("mark.annot"), function (m) {
      (m.getAttribute("data-annot-ids") || "").split(" ").forEach(function (id) { if (id) lastMark[id] = m; });
    });
    var badgeIds = [];
    items.forEach(function (it) {
      var m = lastMark[it.a.id];
      if (!m) return;
      var found = null;
      badgeIds.forEach(function (g) { if (g.mark === m) found = g; });
      if (found) found.ids.push(it.a.id);
      else badgeIds.push({ mark: m, ids: [it.a.id] });
    });
    badgeIds.forEach(function (g) {
      var b = document.createElement("span");
      b.className = "annot-badge";
      b.setAttribute("data-count", String(g.ids.length));
      b.setAttribute("data-annot-ids", g.ids.join(" "));
      b.setAttribute("role", "button");
      b.tabIndex = 0;
      b.setAttribute("aria-label", g.ids.length + (g.ids.length > 1 ? " anotações" : " anotação") + " neste trecho — abrir painel");
      g.mark.parentNode.insertBefore(b, g.mark.nextSibling);
    });
  }
  /* Decisão 17: perder a âncora é uma condição semântica, não só campo vazio. Se o
     bloco não existe mais no documento, a anotação volta para a fila de "manter ou
     jogar fora" — a não ser que você já tenha mandado manter. */
  function registrarAncoraPerdida(a) {
    a.ancora_status = "orfa";
    if (a.resolucao !== "manter") a.incompleta = true;
    return a;
  }

  function paintAll() {
    clearMarks();
    var byBlock = {};
    anotacoes.forEach(function (a) {
      var r = resolveAnchor(a);
      if (!r) { registrarAncoraPerdida(a); return; }
      if (a.ancora_status === "orfa") a.ancora_status = a.ancora_truncada ? "truncada" : "resolvida";
      if (a.ancora_tipo === "bloco") { blocks[a.bloco_id].el.classList.add("has-block-annot"); return; }
      (byBlock[a.bloco_id] = byBlock[a.bloco_id] || []).push({ a: a, inicio: r.inicio, fim: r.fim });
    });
    Object.keys(byBlock).forEach(function (bid) { paintBlock(blocks[bid].el, byBlock[bid]); });
  }

  /* Clique em marcador/badge abre o painel na anotação. */
  document.addEventListener("click", function (e) {
    var t = e.target.closest ? e.target.closest("mark.annot, .annot-badge") : null;
    if (!t) return;
    var ids = (t.getAttribute("data-annot-ids") || "").split(" ").filter(Boolean);
    if (ids.length) { openPanel(ids[0]); }
  });
  document.addEventListener("keydown", function (e) {
    if ((e.key === "Enter" || e.key === " ") && e.target.classList && e.target.classList.contains("annot-badge")) {
      e.preventDefault();
      var ids = (e.target.getAttribute("data-annot-ids") || "").split(" ").filter(Boolean);
      if (ids.length) openPanel(ids[0]);
    }
  });

  /* ===== Painel de anotações (drawer/sheet; nunca por cima do wizard) ===== */
  var panel = $("annot-panel");
  var lastDeleted = null;
  function blocoLabel(a) {
    var d = a.item_id ? dirById(a.item_id) : null;
    return d ? ("Caminho " + letraDe(d)) : (a.bloco_id === "objetivo" ? "Objetivo" : "Recomendação");
  }
  function renderPanel() {
    var body = $("ap-body");
    body.textContent = "";
    var vivas = anotacoes.filter(function (a) { return a.ancora_status !== "orfa"; });
    var orfas = anotacoes.filter(function (a) { return a.ancora_status === "orfa"; });
    if (!anotacoes.length) {
      var empty = el("p", "ap-empty", "Nenhuma anotação ainda. Selecione um trecho de texto da página (ou use o botão “Anotar bloco” que aparece sobre cada bloco) para deixar um bilhete preso ao texto.");
      body.appendChild(empty);
      return;
    }
    function item(a) {
      var it = el("div", "ap-item" + (a.ancora_status === "orfa" ? " orfa" : ""));
      it.setAttribute("data-annot-id", a.id);
      it.appendChild(el("div", "ap-quote", "“" + (a.trecho || "(sem trecho)") + "”"));
      if (a.ancora_status === "orfa") it.appendChild(el("div", "ap-status", "Trecho não encontrado nesta versão — anotação preservada"));
      if (a.ancora_status === "truncada") it.appendChild(el("div", "ap-status", "Trecho parcial (a seleção passava do bloco)"));
      /* editor de verdade: uma anotação restaurada longa demais precisa poder encolher
         sem ser apagada — antes o painel só mostrava o texto (r3/P1) */
      var editor = el("textarea", "ap-text ap-editar");
      editor.value = a.comentario || "";
      editor.setAttribute("data-editar-anotacao", a.id);
      editor.setAttribute("maxlength", String(LIMITES_DE_TEXTO.anotacao));
      editor.setAttribute("aria-label", "Editar o bilhete desta anotação");
      editor.addEventListener("input", function () { editarAnotacao(a.id, editor.value); });
      it.appendChild(editor);
      it.appendChild(el("div", "ap-meta", blocoLabel(a) + (a.criado_em ? " · " + a.criado_em.slice(0, 16).replace("T", " ") : "")));
      var acts = el("div", "ap-actions");
      if (a.ancora_status !== "orfa") {
        var go = el("button", "linklike", "Ir até o trecho");
        go.type = "button";
        go.addEventListener("click", function () { gotoAnnot(a.id); });
        acts.appendChild(go);
      }
      var del = el("button", "linklike", "Apagar");
      del.type = "button";
      del.addEventListener("click", function () { deleteAnnot(a.id); });
      acts.appendChild(del);
      it.appendChild(acts);
      return it;
    }
    vivas.forEach(function (a) { body.appendChild(item(a)); });
    if (orfas.length) {
      body.appendChild(el("div", "ap-section", "Anotações cujo trecho mudou"));
      orfas.forEach(function (a) { body.appendChild(item(a)); });
    }
  }
  function openPanel(focusId) {
    closeWizard();
    closePopover(false);
    hideSelToolbar();
    renderPanel();
    panel.classList.add("open");
    if (focusId) {
      var it = (function () {
        var itens = panel.querySelectorAll("[data-annot-id]");
        for (var i = 0; i < itens.length; i++) {
          if (itens[i].getAttribute("data-annot-id") === focusId) return itens[i];
        }
        return null;
      })();
      if (it) { it.scrollIntoView({ block: "nearest" }); it.classList.add("pulse"); }
    }
  }
  function closePanel() { panel.classList.remove("open"); }
  $("ap-close").addEventListener("click", closePanel);
  $("btn-annot-panel").addEventListener("click", function () {
    if (panel.classList.contains("open")) { closePanel(); return; }
    if (!anotacoes.length) feedback("Para anotar: selecione um trecho de texto da página e toque em “Anotar”.");
    openPanel();
  });
  function deleteAnnot(id) {
    var idx = -1;
    anotacoes.forEach(function (a, i) { if (a.id === id) idx = i; });
    if (idx === -1) return;
    lastDeleted = { rec: anotacoes[idx], index: idx };
    anotacoes.splice(idx, 1);
    persistNow();
    paintAll();
    syncAnnotUI();
    renderPanel();
    $("ap-undo").classList.add("on");
    announce("Anotação apagada. Há um botão de desfazer no painel.");
  }
  $("ap-undo-btn").addEventListener("click", function () {
    if (!lastDeleted) return;
    anotacoes.splice(Math.min(lastDeleted.index, anotacoes.length), 0, lastDeleted.rec);
    lastDeleted = null;
    $("ap-undo").classList.remove("on");
    persistNow();
    paintAll();
    syncAnnotUI();
    renderPanel();
    announce("Anotação restaurada.");
  });
  function gotoAnnot(id) {
    var a = anotacoes.filter(function (x) { return x.id === id; })[0];
    if (!a) return;
    var blk = blocks[a.bloco_id];
    if (!blk) return;
    var art = blk.el.closest("article.dir-doc");
    if (art && art.hasAttribute("hidden")) art.removeAttribute("hidden");
    closePanel();
    var alvo = null;
    Array.prototype.forEach.call(document.querySelectorAll("mark.annot"), function (m) {
      if (!alvo && (m.getAttribute("data-annot-ids") || "").split(" ").indexOf(id) !== -1) alvo = m;
    });
    var scrollAlvo = alvo || blk.el;
    scrollAlvo.scrollIntoView({ block: "center" });
    var acesos = [];
    Array.prototype.forEach.call(document.querySelectorAll("mark.annot"), function (m) {
      if ((m.getAttribute("data-annot-ids") || "").split(" ").indexOf(id) !== -1) { m.classList.add("is-active"); acesos.push(m); }
    });
    if (a.ancora_tipo === "bloco") { blk.el.classList.add("pulse"); }
    setTimeout(function () { acesos.forEach(function (m) { m.classList.remove("is-active"); }); }, 1200);
  }

  /* ===== Contadores e conferência ===== */
  function syncAnnotUI() {
    $("annot-count").textContent = String(anotacoes.length);
    $("ap-count").textContent = String(anotacoes.length);
    DIRS.forEach(function (d) {
      var cell = (function () {
        var linha = elemPorDado("tr.dir-row", "data-dir-id", d.id);
        return linha ? linha.querySelector(".row-annot") : null;
      })();
      if (!cell) return;
      var n = anotacoes.filter(function (a) { return a.item_id === d.id; }).length;
      cell.hidden = n === 0;
      cell.setAttribute("data-count", String(n));
      cell.setAttribute("aria-label", n + (n === 1 ? " anotação" : " anotações") + " neste caminho");
    });
    var lista = $("confer-annot-list");
    lista.textContent = "";
    $("confer-annot-count").textContent = String(anotacoes.length);
    $("confer-annot-empty").hidden = anotacoes.length > 0;
    anotacoes.forEach(function (a) {
      var li = document.createElement("li");
      var quote = a.trecho.length > 60 ? a.trecho.slice(0, 60) + "…" : a.trecho;
      var btn = el("button", "linklike", "“" + quote + "”");
      btn.type = "button";
      btn.addEventListener("click", function () { openPanel(a.id); });
      li.appendChild(btn);
      var extra = a.comentario ? " — " + (a.comentario.length > 80 ? a.comentario.slice(0, 80) + "…" : a.comentario) : "";
      if (a.ancora_status === "orfa") extra += " (trecho não encontrado nesta versão)";
      li.appendChild(document.createTextNode(extra));
      lista.appendChild(li);
    });
    panel.classList.toggle("is-empty", anotacoes.length === 0);
    renderPanel(); /* painel sempre atualizado: @media print o revela mesmo sem nunca ter sido aberto (P1-1 da revisão fresh) */
  }

  /* ===== Comentário (rascunho lossless: o texto persiste sempre; B2) ===== */
  var comentario = $("comentario");
  function autogrow(ta) { ta.style.height = "auto"; ta.style.height = Math.max(96, ta.scrollHeight) + "px"; }
  comentario.addEventListener("input", aoDigitarNoCampoPrincipal);

  /* ===== Export (copiar/baixar) — momento capturado na ação do usuário ===== */
  function showPreview(text) {
    var pv = $("preview-panel");
    $("preview-pre").textContent = text;
    pv.classList.add("open");
    pv.scrollIntoView({ block: "nearest" });
    $("preview-pre").focus();
  }
  function fallbackExecCopy(text) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.left = "-9999px";
    document.body.appendChild(ta);
    ta.select();
    var ok = false;
    try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
    document.body.removeChild(ta);
    return ok;
  }
  function copyText(text, okMsg, warn) {
    function onFail() {
      if (fallbackExecCopy(text)) { feedback(okMsg, warn); }
      else { showPreview(text); feedback("Use a prévia acima da barra para copiar manualmente.", true); }
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { feedback(okMsg, warn); }, onFail);
    } else { onFail(); }
  }
  $("btn-copy-json").addEventListener("click", function () {
    var momento = new Date().toISOString(); /* instante da ação do usuário (B3 da síntese) */
    persistNow();
    var pendente = !state.direcao_escolhida;
    var json = JSON.stringify(buildExport(momento), null, 2);
    copyText(json,
      pendente
        ? "Copiado, mas marcado como PENDENTE: você ainda não escolheu um caminho, e o conferente vai devolver assim. Escolha na tabela e copie de novo."
        : "Copiado ✓ — agora cole na conversa com o agente.",
      pendente);
  });
  $("btn-download-json").addEventListener("click", function () {
    var momento = new Date().toISOString();
    persistNow();
    var pendente = !state.direcao_escolhida;
    var blob = new Blob([JSON.stringify(buildExport(momento), null, 2)], { type: "application/json" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = CONTRATO.export.nome_arquivo;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 500);
    feedback(pendente
      ? "Arquivo baixado marcado como PENDENTE — escolha um caminho antes de devolver, ou o conferente vai devolver."
      : "Arquivo baixado ✓ — salve em respostas/ da tarefa ou mande na conversa.",
      pendente);
  });
  $("preview-select").addEventListener("click", function () {
    var pre = $("preview-pre");
    var range = document.createRange();
    range.selectNodeContents(pre);
    var sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
  });
  $("preview-close").addEventListener("click", function () { $("preview-panel").classList.remove("open"); });

  /* ===== Affordance de rolagem da tabela (desktop) ===== */
  function syncTableAffordance() {
    var card = document.querySelector(".table-card");
    var scroll = card.querySelector(".table-scroll");
    card.classList.toggle("scrollable", scroll.scrollWidth > scroll.clientWidth + 1);
    card.classList.toggle("at-end", scroll.scrollLeft + scroll.clientWidth >= scroll.scrollWidth - 1);
  }
  window.addEventListener("resize", syncTableAffordance);
  document.querySelector(".table-scroll").addEventListener("scroll", syncTableAffordance, { passive: true });

  /* ===== Dica de anotação (1ª visita) ===== */
  $("hint-dismiss").addEventListener("click", function () {
    state.dica_dispensada = true;
    $("annot-hint").hidden = true;
    persistNow();
  });

  /* ===== Boot (sem persist(): abrir a página não grava nada — B1) ===== */
  restore();
  storageUI();
  comentario.value = state.comentario;
  autogrow(comentario);
  paintAll();
  syncAnnotUI();
  syncChoiceView();
  syncTableAffordance();
  pintarAnotacoesIncompletas();
  if (!state.dica_dispensada) $("annot-hint").hidden = false;

  /* Gancho somente-leitura para o verificador determinístico (não é botão público). */
  window.__temcomo = {
    versao: "v2",
    chave: STORAGE_KEY,
    contratoSha: CONTRACT_SHA,
    buildExport: buildExport,
    getState: function () { return JSON.parse(JSON.stringify({ estado: state, anotacoes: anotacoes })); },
    storageOk: function () { return storageOk; }
  };

  } catch (err) {
    document.documentElement.classList.remove("js-on");
    document.documentElement.classList.add("js-failed");
    var fb = document.getElementById("boot-fallback");
    if (fb) {
      fb.hidden = false;
      fb.textContent = "O modo interativo não pôde iniciar neste navegador (" + err + "). O conteúdo completo está visível abaixo, em página corrida — nada foi perdido; use os botões de copiar/baixar se funcionarem, ou copie o texto manualmente.";
    }
  }
})();
</script>
</body>
</html>

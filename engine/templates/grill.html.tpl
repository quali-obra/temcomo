<!DOCTYPE html>
%%PROVENIENCIA%%
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%%TITULO%%</title>
<style>
/* ===== QualiApps Design System — tokens (fonte: skills/brand/qualiapps-design-system/tokens.css, via base aprovada 001) ===== */
%%TOKENS%%
*, *::before, *::after { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; scrollbar-gutter: stable; }
html.modal-open { overflow: hidden; }
body {
  margin: 0; background: var(--bg-soft); color: var(--ink);
  font-family: var(--font-body); font-size: var(--fs-16);
  line-height: var(--lh-normal); font-weight: 400;
  -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;
  padding-bottom: 148px;
}
img { display:block; max-width:100%; }
h1,h2,h3,h4 { font-family: var(--font-display); color: var(--ink); margin:0; line-height: var(--lh-tight); letter-spacing:-0.01em; }
p { margin:0; }
:focus-visible { outline:none; box-shadow: var(--ring-focus); border-radius: var(--r-2); }
::selection { background: color-mix(in srgb, var(--brand) 25%, transparent); }
.sr-only { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0 0 0 0); white-space:nowrap; border:0; }
[hidden] { display:none !important; }

.container { max-width: var(--container-w); margin: 0 auto; padding-left: var(--container-pad); padding-right: var(--container-pad); }

/* ===== Faixa de protótipo (topo) ===== */
.notice-strip {
  background: var(--bg-ink); color: #FFFFFF;
  font-family: var(--font-display); font-weight: 500; font-size: var(--fs-14);
  padding: 8px var(--container-pad); text-align: center; line-height: var(--lh-snug);
}
.notice-strip .dot { display:inline-block; width:8px; height:8px; border-radius:2px; background: var(--brand-soft); margin-right: 8px; vertical-align: 1px; }

/* ===== Topbar ===== */
.topbar { background: var(--bg); border-bottom: 1px solid var(--line); }
.topbar-inner { display:flex; align-items:center; justify-content:space-between; gap: var(--sp-4); padding-top: var(--sp-3); padding-bottom: var(--sp-3); flex-wrap: wrap; }
.topbar img.logo { height: 30px; width: auto; }
.topbar .top-right { display:flex; align-items:center; gap: var(--sp-4); }
.topbar .meta { text-align:right; }
.topbar .meta .rid { font-family: var(--font-mono); font-size: var(--fs-12); color: var(--ink-3); word-break: break-word; }
.topbar .meta .rdate { font-family: var(--font-display); font-weight:500; font-size: var(--fs-12); color: var(--ink-3); margin-top:2px; }
.btn-docmode { display:inline-flex; align-items:center; gap:8px; min-height:44px; padding: 8px 14px; border-radius: var(--r-3); border:1.5px solid var(--line); background: var(--bg); color: var(--ink-2); font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); cursor:pointer; }
.btn-docmode:hover { background: var(--bg-soft); }
.btn-docmode[aria-pressed="true"] { background: var(--brand-tint); border-color: color-mix(in srgb, var(--brand) 45%, var(--line)); color: var(--brand-ink); }

/* ===== Hero compacto (orçamento: ≤180px) ===== */
.hero { padding-top: var(--sp-3); }
.hero-card { background: var(--bg); border:1px solid var(--line); border-radius: var(--r-5); box-shadow: var(--shadow-2); padding: var(--sp-4) var(--sp-5); }
.hero-top { display:flex; align-items:center; justify-content:space-between; gap: var(--sp-4); }
.eyebrow { font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); letter-spacing:.08em; text-transform:uppercase; color: var(--brand-ink); margin-bottom: 4px; }
.hero h1 { font-size: var(--fs-20); font-weight: 800; line-height: var(--lh-snug); }
.hero .task-line { margin-top: 4px; font-size: var(--fs-14); color: var(--ink-3); line-height: var(--lh-snug); }
.hero .task-line strong { font-family: var(--font-display); font-weight:600; color: var(--ink-2); }
#btn-comecar { flex: 0 0 auto; }
.hero-progress { display:flex; align-items:center; gap: var(--sp-4); margin-top: var(--sp-3); }
.hero-progress .progress { flex:1 1 auto; height:8px; border-radius: var(--r-pill); background: var(--line-soft); overflow:hidden; }
.hero-progress .progress > div { height:100%; width:0%; background: var(--brand); border-radius: var(--r-pill); transition: width .24s ease; }
.hero-progress .ptext { font-family:var(--font-display); font-size: var(--fs-12); font-weight:600; color: var(--ink-3); white-space:nowrap; }
.hero-progress a.howto-link { font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); color: var(--brand-ink); white-space:nowrap; }

/* ===== Avisos de página (rascunho migrado, relatório atualizado) ===== */
#page-notice { margin-top: var(--sp-3); display:flex; flex-direction:column; gap: var(--sp-2); }
.pnotice { display:flex; align-items:flex-start; gap: var(--sp-3); background: var(--brand-tint); border:1px solid color-mix(in srgb, var(--brand) 22%, var(--line)); border-radius: var(--r-3); padding: var(--sp-3) var(--sp-4); font-size: var(--fs-14); color: var(--ink-2); }
.pnotice .pn-actions { margin-left:auto; display:flex; gap: var(--sp-2); flex:0 0 auto; }
.pnotice button { min-height: 36px; padding: 6px 12px; border-radius: var(--r-2); border:1.5px solid color-mix(in srgb, var(--brand) 45%, var(--line)); background: var(--bg); color: var(--brand-ink); font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); cursor:pointer; }

/* ===== Lista compacta ===== */
.lista { margin-top: var(--sp-3); display:flex; flex-direction:column; gap: var(--sp-2); }
details.q-item { background: var(--bg); border:1px solid var(--line); border-radius: var(--r-4); box-shadow: var(--shadow-1); }
details.q-item[open] { box-shadow: var(--shadow-2); }
summary.q-row { list-style:none; display:grid; grid-template-columns: 30px minmax(0,1fr) auto 18px; gap: 0 var(--sp-3); align-items:center; padding: 8px var(--sp-4) 8px var(--sp-3); min-height: 64px; cursor:pointer; border-radius: var(--r-4); }
summary.q-row::-webkit-details-marker, summary.q-row::marker { display:none; content:""; }
summary.q-row:hover { background: var(--bg-soft); }
summary.q-row:focus-visible { outline:none; box-shadow: var(--ring-focus); }
.q-num { display:inline-flex; align-items:center; justify-content:center; width:26px; height:26px; border-radius: 8px; background: var(--brand-strong); color:#FFF; font-family: var(--font-display); font-weight:700; font-size: var(--fs-14); }
.q-main { min-width:0; display:flex; flex-direction:column; gap:2px; }
.q-start-badge { align-self:flex-start; font-family: var(--font-display); font-weight:600; font-size: 0.6875rem; color: var(--brand-ink); background: var(--brand-tint); border:1px solid color-mix(in srgb, var(--brand) 22%, var(--line)); border-radius: var(--r-pill); padding: 1px 8px; }
.q-title { font-family: var(--font-display); font-weight:600; font-size: var(--fs-16); color: var(--ink); line-height: var(--lh-snug); }
.q-line2 { font-size: var(--fs-14); color: var(--ink-3); line-height: var(--lh-snug); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.q-line2 .q-outcome strong { font-family: var(--font-display); font-weight:600; color: var(--ink-2); }
.q-line3 { font-size: var(--fs-12); color: var(--ink-4); line-height: var(--lh-snug); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; font-family: var(--font-display); }
.q-line3 .q-sug strong { font-weight:600; color: var(--ink-3); }
.q-line3 .q-dotsep { margin: 0 5px; }
.q-line3 .q-rev.irrev { color: var(--warn-ink); font-weight:600; }
/* Destaque de irreversibilidade (ajuste aprovado em 2026-08-20): linhas com
   reversivel:false ganham fundo em tint suave de danger (token --danger-tint, 10% sobre branco).
   Não é estado: o chip segue normal e o destaque persiste em qualquer estado, no modo
   documento e na impressão. Pares AA: ink/ink-3 e danger-ink sobre o tint (≥4.5:1). */
details.q-item.is-irrev > summary.q-row { background: var(--danger-tint); -webkit-print-color-adjust: exact; print-color-adjust: exact; }
details.q-item.is-irrev > summary.q-row:hover { background: color-mix(in srgb, var(--danger) 14%, var(--bg) 86%); }
details.q-item.is-irrev[open] > summary.q-row { border-radius: var(--r-4) var(--r-4) 0 0; }
details.q-item.is-irrev .q-line3 { color: var(--ink-3); }
details.q-item.is-irrev .q-line3 .q-rev.irrev { color: var(--danger-ink); }
.q-side { display:flex; align-items:center; gap: var(--sp-2); justify-self:end; }
.q-annot { display:inline-flex; align-items:center; gap:4px; font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); color: var(--brand-ink); }
.q-annot svg { width:14px; height:14px; stroke: var(--brand-ink); fill:none; stroke-width:2; }
.chev { width:16px; height:16px; stroke: var(--ink-4); fill:none; stroke-width:2; justify-self:end; transition: transform .16s ease; }
body.doc-mode details.q-item[open] .chev { transform: rotate(90deg); }

/* chips de estado (linguagem leiga) */
.status-chip { display:inline-flex; align-items:center; gap:7px; border-radius: var(--r-pill); padding: 5px 12px; font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); border:1px solid var(--line); background: var(--bg-soft); color: var(--ink-3); white-space:nowrap; }
.status-chip::before { content:""; flex:0 0 auto; width:7px; height:7px; border-radius:50%; background: var(--ink-4); }
.status-chip.s-ok { background: var(--ok-tint); color: var(--ok-ink); border-color: color-mix(in srgb, var(--success) 30%, var(--line)); }
.status-chip.s-ok::before { background: var(--success); }
.status-chip.s-duvida { background: var(--doubt-tint); color: var(--doubt-ink); border-color: color-mix(in srgb, var(--doubt) 28%, var(--line)); }
.status-chip.s-duvida::before { background: var(--doubt); }
.status-chip.s-adiada { background: var(--warn-tint); color: var(--warn-ink); border-color: color-mix(in srgb, var(--warning) 30%, var(--line)); }
.status-chip.s-adiada::before { background: var(--warning); }
@keyframes chip-pulse { 0% { box-shadow: 0 0 0 0 color-mix(in srgb, var(--brand) 45%, transparent); } 100% { box-shadow: 0 0 0 9px transparent; } }
.status-chip.pulse { animation: chip-pulse .7s ease-out 1; }
@media (prefers-reduced-motion: reduce) { .status-chip.pulse { animation: none; } .hero-progress .progress > div, .chev { transition: none; } }

/* ===== Corpo da pergunta (conteúdo real no documento; o wizard só o move) ===== */
.q-home { border-top: 1px solid var(--line-soft); }
article.q-card { padding: var(--sp-5) var(--sp-6); }
article.q-card .card-title { font-size: var(--fs-18); font-weight:700; line-height: var(--lh-snug); margin-bottom: var(--sp-2); }
.wz-block { margin-top: var(--sp-4); }
.wz-block:first-of-type { margin-top: 0; }
.block-label { font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); letter-spacing:.07em; text-transform:uppercase; color: var(--ink-3); margin-bottom: var(--sp-2); }
.card-context, .card-impact { color: var(--ink-2); line-height: var(--lh-loose); max-width: 72ch; }
.rev-note { margin-top: var(--sp-2); font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); color: var(--ink-3); }
/* Callout de irreversibilidade dentro do cartão (delta aprovado em 2026-08-20):
   substitui a nota fraca; warn-tint (universal de atenção), triângulo SVG inline, frase em
   negrito com par AA warn-ink sobre warn-tint. Aparece também no modo documento e impressão. */
.irrev-callout { display:flex; gap: var(--sp-3); align-items:flex-start; margin-top: var(--sp-4); background: var(--warn-tint); border:1px solid color-mix(in srgb, var(--warning) 30%, var(--line)); border-radius: var(--r-3); padding: var(--sp-3) var(--sp-4); color: var(--warn-ink); font-family: var(--font-display); font-weight:700; font-size: var(--fs-14); line-height: var(--lh-normal); -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.irrev-callout svg { flex:0 0 auto; width:20px; height:20px; margin-top:1px; stroke: var(--warn-ink); fill:none; stroke-width:2; }

/* opções (radio) — recomendada destacada, nunca pré-gravada */
fieldset.options { border:0; margin: var(--sp-4) 0 0; padding:0; }
fieldset.options legend { padding:0; margin:0; }
.options-list { display:flex; flex-direction:column; gap: var(--sp-2); margin-top: var(--sp-2); }
.option { position:relative; display:flex; gap: var(--sp-3); align-items:flex-start; background: var(--bg); border:1.5px solid var(--line); border-radius: var(--r-4); padding: var(--sp-3) var(--sp-4); min-height: 44px; cursor:pointer; transition: border-color .15s ease, background-color .15s ease; }
.option:hover { background: var(--bg-soft); }
.option input[type="radio"] { flex:0 0 auto; width: 22px; height: 22px; margin: 2px 0 0; accent-color: var(--brand); cursor:pointer; }
.option input[type="radio"]:focus-visible { outline:none; box-shadow: var(--ring-focus); border-radius: 50%; }
.option .opt-body { display:block; flex:1 1 auto; min-width:0; }
.option .opt-title { display:block; font-family: var(--font-display); font-weight:600; font-size: var(--fs-16); color: var(--ink); line-height: var(--lh-snug); }
.option .opt-detail { display:block; margin-top: 3px; font-size: var(--fs-14); color: var(--ink-3); line-height: var(--lh-normal); }
.option.selected { border-color: var(--brand); background: var(--brand-tint); }
.option.selected .opt-detail { color: var(--ink-2); }
.opt-badge { display:inline-block; margin-left: 8px; vertical-align: 2px; border-radius: var(--r-pill); padding: 2px 10px; font-family: var(--font-display); font-weight:600; font-size: 0.6875rem; letter-spacing:.02em; }
.opt-badge.b-recomendada { background: var(--brand-strong); color: #FFFFFF; }
.opt-badge.b-fora { background: var(--bg); color: var(--brand-ink); border: 1.5px dashed var(--brand-ink); }
.option.fora-da-caixa { border-style: dashed; border-color: color-mix(in srgb, var(--brand) 45%, var(--line)); }
.option.fora-da-caixa.selected { border-color: var(--brand); background: var(--brand-tint); }
/* painel ganha / abre mão — colado na opção marcada, reage à troca */
.opt-cons { display:none; margin-top: var(--sp-2); }
.option.selected .opt-cons { display:grid; grid-template-columns: 1fr 1fr; gap: var(--sp-2); }
.opt-cons .cons-box { display:block; border-radius: var(--r-3); padding: var(--sp-2) var(--sp-3); font-size: var(--fs-14); line-height: var(--lh-normal); }
.opt-cons .cons-ganha { background: var(--ok-tint); color: var(--ok-ink); border:1px solid color-mix(in srgb, var(--success) 25%, var(--line)); }
.opt-cons .cons-abre { background: var(--warn-tint); color: var(--warn-ink); border:1px solid color-mix(in srgb, var(--warning) 25%, var(--line)); }
.opt-cons .cons-h { display:block; font-family: var(--font-display); font-weight:700; font-size: 0.6875rem; letter-spacing:.05em; text-transform:uppercase; margin-bottom: 3px; }

/* botões de estado por pergunta */
.answer-row { margin-top: var(--sp-2); display:flex; flex-wrap:wrap; gap: var(--sp-3); align-items:flex-start; }
.state-buttons { display:flex; flex-wrap:wrap; gap: var(--sp-2); }
.state-btn { display:inline-flex; align-items:center; gap:8px; min-height: 46px; padding: 10px 16px; border-radius: var(--r-3); font-family: var(--font-display); font-weight:600; font-size: var(--fs-14); cursor:pointer; background: var(--bg); color: var(--ink-2); border:1.5px solid var(--line); transition: background-color .15s ease, border-color .15s ease; user-select: none; -webkit-user-select: none; }
.state-btn::before { content:""; width:8px; height:8px; border-radius:50%; background: var(--ink-4); }
.state-btn:hover { background: var(--bg-soft); }
.state-btn.b-aprovar::before { background: var(--success); }
.state-btn.b-rejeitar::before { background: var(--danger); }
.state-btn.b-duvida::before { background: var(--doubt); }
.state-btn.b-adiar::before { background: var(--warning); }
.state-btn.b-aprovar[aria-pressed="true"] { background: var(--ok-tint); color: var(--ok-ink); border-color: var(--success); }
.state-btn.b-rejeitar[aria-pressed="true"] { background: var(--danger-tint); color: var(--danger-ink); border-color: var(--danger); }
.state-btn.b-duvida[aria-pressed="true"] { background: var(--doubt-tint); color: var(--doubt-ink); border-color: var(--doubt); }
.state-btn.b-adiar[aria-pressed="true"] { background: var(--warn-tint); color: var(--warn-ink); border-color: var(--warning); }
.reset-answer { margin-top: var(--sp-2); background:none; border:0; padding: 6px 0; min-height: 32px; font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); color: var(--ink-3); text-decoration: underline; cursor:pointer; }
.reset-answer:hover { color: var(--danger-ink); }

.duvida-box { flex: 1 1 280px; background: var(--doubt-tint); border:1.5px solid color-mix(in srgb, var(--doubt) 35%, var(--line)); border-radius: var(--r-3); padding: var(--sp-3) var(--sp-4); }
.duvida-box label { display:block; font-family: var(--font-display); font-weight:600; font-size: var(--fs-14); color: var(--doubt-ink); margin-bottom: 7px; }
.duvida-box textarea { min-height: 64px; border-color: color-mix(in srgb, var(--doubt) 35%, var(--line)); background: var(--bg); }
.duvida-box textarea:focus { border-color: var(--doubt); box-shadow: 0 0 0 3px color-mix(in srgb, var(--doubt) 30%, transparent); }
.duvida-box .duvida-hint { margin-top: 6px; font-size: var(--fs-12); color: var(--doubt-ink); line-height: var(--lh-normal); }

.decision-help { background: var(--bg-soft); border-left: 3px solid var(--brand); border-radius: 0 var(--r-2) var(--r-2) 0; padding: 10px 14px; font-size: var(--fs-14); color: var(--ink-2); line-height: var(--lh-normal); max-width: 640px; margin-top: var(--sp-3); }
.decision-help.h-duvida { border-left-color: var(--doubt); }
.decision-help.h-aprovada { border-left-color: var(--success); }
.decision-help.h-rejeitada { border-left-color: var(--danger); }
.decision-help.h-adiada { border-left-color: var(--warning); }

.field { margin-top: var(--sp-4); }
.field label { display:block; font-family: var(--font-display); font-weight:600; font-size: var(--fs-14); color: var(--ink-2); margin-bottom: 7px; }
.field .field-hint { margin-top: 6px; font-size: var(--fs-12); color: var(--ink-4); line-height: var(--lh-normal); }
textarea {
  width:100%; padding: 12px 14px; font-family: var(--font-body); font-size: var(--fs-16);
  color: var(--ink); line-height: var(--lh-normal); background: var(--bg);
  border: 1.5px solid var(--line); border-radius: var(--r-3); resize: vertical;
  min-height: 52px; overflow: hidden;
}
textarea:focus { border-color: var(--brand); outline:none; box-shadow: var(--ring-focus); }
textarea::placeholder { color: var(--ink-3); opacity: 1; }

details.evidence { margin-top: var(--sp-4); border:1px solid var(--line-soft); border-radius: var(--r-3); background: var(--bg-soft); }
details.evidence summary { cursor:pointer; min-height: 44px; display:flex; align-items:center; padding: 10px 14px; font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); color: var(--ink-3); list-style:none; }
details.evidence summary::before { content:"▸"; margin-right: 8px; color: var(--brand-ink); }
details.evidence[open] summary::before { content:"▾"; }
details.evidence summary::-webkit-details-marker, details.evidence summary::marker { display:none; content:""; }
details.evidence .evidence-body { padding: 0 14px 12px; font-size: var(--fs-14); color: var(--ink-3); line-height: var(--lh-normal); }
details.evidence .evidence-body .mono { font-family: var(--font-mono); font-size: var(--fs-12); color: var(--ink-2); word-break: break-all; }

/* ===== Dica de anotação + como funciona ===== */
.dica-anotacao { margin-top: var(--sp-3); display:flex; align-items:center; gap: var(--sp-3); font-size: var(--fs-14); color: var(--ink-3); }
.dica-anotacao button { background:none; border:0; min-height:32px; padding: 4px 8px; font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); color: var(--brand-ink); text-decoration:underline; cursor:pointer; }
details.howto { margin-top: var(--sp-3); border:1px solid var(--line); border-radius: var(--r-4); background: var(--bg); box-shadow: var(--shadow-1); }
details.howto > summary { cursor:pointer; min-height: 44px; display:flex; align-items:center; padding: 10px var(--sp-4); font-family: var(--font-display); font-weight:600; font-size: var(--fs-14); color: var(--ink-2); list-style:none; }
details.howto > summary::-webkit-details-marker, details.howto > summary::marker { display:none; content:""; }
details.howto > summary::before { content:"▸"; margin-right: 8px; color: var(--brand-ink); }
details.howto[open] > summary::before { content:"▾"; }
.howto-body { padding: 0 var(--sp-5) var(--sp-4); font-size: var(--fs-14); color: var(--ink-2); line-height: var(--lh-loose); }
.howto-body p + p { margin-top: var(--sp-2); }
.howto-body strong { font-family: var(--font-display); font-weight:600; }

/* ===== Conferência final ===== */
.conferencia { margin-top: var(--sp-6); }
.conf-card { background: var(--bg); border:1px solid var(--line); border-radius: var(--r-5); box-shadow: var(--shadow-2); padding: var(--sp-6) var(--sp-8); }
.conf-card h2 { font-size: var(--fs-20); font-weight:700; }
.conf-status { margin-top: var(--sp-2); font-size: var(--fs-14); color: var(--ink-3); }
.conf-status.pronto { color: var(--ok-ink); font-family: var(--font-display); font-weight:600; }
.conf-list { list-style:none; margin: var(--sp-4) 0 0; padding:0; display:flex; flex-direction:column; gap: 6px; }
.conf-list li button { width:100%; display:grid; grid-template-columns: 26px minmax(0,1fr); gap: 2px var(--sp-3); align-items:baseline; text-align:left; background: var(--bg-soft); border:1px solid var(--line-soft); border-radius: var(--r-3); padding: 10px var(--sp-3); min-height: 44px; cursor:pointer; font-family: var(--font-body); font-size: var(--fs-14); color: var(--ink-2); }
.conf-list li button:hover { background: var(--brand-tint); }
.conf-list .cf-num { grid-row: 1 / span 2; font-family: var(--font-display); font-weight:700; font-size: var(--fs-12); color: var(--brand-ink); }
.conf-list .cf-q { font-family: var(--font-display); font-weight:600; color: var(--ink); line-height: var(--lh-snug); }
.conf-list .cf-a { color: var(--ink-3); line-height: var(--lh-snug); }
.conf-list .cf-a strong { font-family: var(--font-display); font-weight:600; color: var(--ok-ink); }
.conf-list .cf-a.cf-pend strong { color: var(--ink-3); }
.conf-list .cf-a.cf-duvida strong { color: var(--doubt-ink); }
.conf-list .cf-a.cf-adiada strong { color: var(--warn-ink); }
.conf-duvidas { margin-top: var(--sp-3); font-size: var(--fs-14); color: var(--doubt-ink); background: var(--doubt-tint); border:1px solid color-mix(in srgb, var(--doubt) 28%, var(--line)); border-radius: var(--r-3); padding: var(--sp-2) var(--sp-3); }
.conf-actions { margin-top: var(--sp-5); display:flex; gap: var(--sp-6); flex-wrap:wrap; }
.conf-actions .ca { display:flex; flex-direction:column; gap: 4px; }
.btn-legend { font-size: var(--fs-12); color: var(--ink-4); }
.conf-tech { margin-top: var(--sp-4); font-family: var(--font-mono); font-size: var(--fs-12); color: var(--ink-4); }

/* ===== Barra fixa de export ===== */
.export-bar { position: fixed; left:0; right:0; bottom:0; z-index: 40; background: var(--bg); border-top: 1px solid var(--line); box-shadow: var(--shadow-3); padding-bottom: env(safe-area-inset-bottom); }
.export-progress { position:absolute; top:-1px; left:0; right:0; height: 4px; background: var(--line-soft); }
.export-progress > div { height:100%; width:0%; background: var(--brand); transition: width .24s ease; }
#storage-alert { background: var(--danger-tint); color: var(--danger-ink); border-bottom: 1px solid color-mix(in srgb, var(--danger) 30%, var(--line)); font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); padding: 8px var(--container-pad); text-align:center; }
.export-inner { display:flex; align-items:center; justify-content:space-between; gap: var(--sp-3); padding-top: var(--sp-2); padding-bottom: var(--sp-2); flex-wrap: wrap; }
.export-count { font-family: var(--font-display); font-weight:700; font-size: var(--fs-14); color: var(--ink-2); }
.copy-feedback { font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); color: var(--ok-ink); min-height: 1em; }
.export-actions { display:flex; gap: var(--sp-2); flex-wrap: wrap; align-items:center; }
.btn { display:inline-flex; align-items:center; justify-content:center; gap:8px; min-height: 46px; padding: 10px 18px; border-radius: var(--r-3); font-family: var(--font-display); font-weight:600; font-size: var(--fs-14); cursor:pointer; border:1.5px solid transparent; }
.btn-primary { background: var(--brand-strong); color: #FFFFFF; }
.btn-primary:hover { background: color-mix(in srgb, var(--brand) 62%, var(--ink) 38%); }
.btn-secondary { background: var(--bg); color: var(--brand-ink); border-color: color-mix(in srgb, var(--brand) 45%, var(--line)); }
.btn-secondary:hover { background: var(--brand-tint); }
.btn-ghost { background: var(--bg); color: var(--ink-2); border-color: var(--line); }
.btn-ghost:hover { background: var(--bg-soft); }
.btn-ghost:disabled { color: var(--ink-4); cursor: default; background: var(--bg); }
.export-note { padding: 0 0 8px; font-size: var(--fs-12); color: var(--ink-4); display:flex; gap: var(--sp-2); flex-wrap:wrap; align-items:baseline; }
.export-note .mono { font-family: var(--font-mono); }
#save-promise.falhou { color: var(--danger-ink); font-weight:600; }

/* ===== Prévia manual (fallback de cópia) ===== */
.preview-panel { display:none; margin-top: var(--sp-6); background: var(--bg); border:1px solid var(--line); border-radius: var(--r-4); box-shadow: var(--shadow-2); padding: var(--sp-5); }
.preview-panel.open { display:block; }
.preview-panel h2 { font-size: var(--fs-16); font-weight:700; margin-bottom: var(--sp-2); }
.preview-panel p { font-size: var(--fs-14); color: var(--ink-3); margin-bottom: var(--sp-3); }
.preview-panel pre { margin:0; max-height: 340px; overflow:auto; background: var(--bg-soft); border:1px solid var(--line-soft); border-radius: var(--r-3); padding: var(--sp-3); font-family: var(--font-mono); font-size: var(--fs-12); line-height: 1.55; white-space: pre-wrap; word-break: break-word; user-select: all; }
.preview-panel .preview-actions { margin-top: var(--sp-3); display:flex; gap: var(--sp-2); flex-wrap:wrap; }

/* ===== Wizard (dialog nativo, com os 7 remendos do parecer técnico) ===== */
dialog.wizard { border:0; padding:0; margin:auto; width:min(720px, calc(100vw - 48px)); max-width:none; max-height:86vh; border-radius: var(--r-5); box-shadow: var(--shadow-3); background: var(--bg); color: var(--ink); }
dialog.wizard[open] { display:flex; }
dialog.wizard::backdrop { background: rgba(14,23,38,.45); }
.wz-frame { display:flex; flex-direction:column; min-height:0; width:100%; }
.sheet-handle { display:none; }
.wz-head { flex:0 0 auto; display:grid; grid-template-columns: minmax(0,1fr) auto; gap: 2px var(--sp-3); align-items:start; padding: var(--sp-4) var(--sp-6); border-bottom: 1px solid var(--line-soft); background: var(--bg); border-radius: var(--r-5) var(--r-5) 0 0; }
.wz-eyebrow { grid-column:1; font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); letter-spacing:.08em; text-transform:uppercase; color: var(--brand-ink); }
.wz-title { grid-column:1; font-size: var(--fs-20); font-weight:700; line-height: var(--lh-snug); outline:none; }
.wz-title:focus-visible { box-shadow:none; }
.wz-close { grid-column:2; grid-row: 1 / span 2; align-self:center; display:inline-flex; align-items:center; gap:6px; min-height:44px; padding: 8px 14px; border-radius: var(--r-3); border:1.5px solid var(--line); background: var(--bg); color: var(--ink-2); font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); cursor:pointer; }
.wz-close:hover { background: var(--bg-soft); }
.wz-notice { flex:0 0 auto; background: var(--brand-tint); border-bottom:1px solid color-mix(in srgb, var(--brand) 22%, var(--line)); padding: 8px var(--sp-6); font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); color: var(--brand-ink); }
.wz-body { flex:1 1 auto; overflow-y:auto; overscroll-behavior: contain; min-height:0; }
.wz-body article.q-card { padding: var(--sp-5) var(--sp-6) var(--sp-6); }
.wz-body article.q-card .card-title { display:none; } /* o título vive no cabeçalho do wizard */
.wz-body.fade { opacity: 0; transition: opacity .12s ease; }
@media (prefers-reduced-motion: reduce) { .wz-body.fade { transition: none; } }
.wz-foot { flex:0 0 auto; display:flex; align-items:center; justify-content:space-between; gap: var(--sp-3); padding: var(--sp-3) var(--sp-6); border-top: 1px solid var(--line); background: var(--bg); border-radius: 0 0 var(--r-5) var(--r-5); }
.wz-dots { display:flex; gap: 6px; align-items:center; }
.wz-dot { width: 22px; height: 10px; border-radius: 3px; background: var(--line-soft); border:0; padding:0; cursor:pointer; min-height:0; }
.wz-dot.done { background: var(--brand-strong); }
.wz-dot.cur { box-shadow: var(--ring-focus); }
.wz-dot:focus-visible { outline:none; box-shadow: var(--ring-focus); }

/* ===== Anotações ancoradas ===== */
mark.annot { background: color-mix(in srgb, var(--brand) 14%, transparent); border-bottom: 2px dotted var(--brand-ink); border-radius: 2px; padding: 0 1px; color: inherit; }
mark.annot.is-active { background: color-mix(in srgb, var(--brand) 22%, transparent); border-bottom-style: solid; }
[data-anotavel].annot-bloco { box-shadow: inset 3px 0 0 color-mix(in srgb, var(--brand) 45%, transparent); padding-left: 8px; border-radius: 2px; }
.annot-badge { display:inline-flex; align-items:center; justify-content:center; min-width:18px; height:18px; border-radius:50%; background: var(--brand-strong); color:#FFF; font-family: var(--font-display); font-weight:700; font-size: 11px; border:0; padding:0 4px; cursor:pointer; vertical-align: super; margin-left: 2px; position:relative; }
.annot-badge::after { content:""; position:absolute; inset:-13px; }
[data-anotavel] { position:relative; }
.annot-block-btn { position:absolute; top:-6px; right:-4px; opacity:0; pointer-events:none; display:inline-flex; align-items:center; min-height:28px; padding: 3px 10px; border-radius: var(--r-pill); border:1px solid var(--line); background: var(--bg); color: var(--brand-ink); font-family: var(--font-display); font-weight:600; font-size: 0.6875rem; cursor:pointer; box-shadow: var(--shadow-1); }
[data-anotavel]:hover .annot-block-btn, [data-anotavel]:focus-within .annot-block-btn, .annot-block-btn:focus-visible { opacity:1; pointer-events:auto; }

#annot-bar { position:fixed; z-index: 70; display:none; }
#annot-bar.show { display:block; }
#annot-bar button { display:inline-flex; align-items:center; gap:6px; min-height: 44px; padding: 10px 16px; border-radius: var(--r-pill); background: var(--bg-ink); color:#FFF; border:0; font-family: var(--font-display); font-weight:600; font-size: var(--fs-14); cursor:pointer; box-shadow: var(--shadow-2); }
#annot-bar svg { width:14px; height:14px; stroke:#FFF; fill:none; stroke-width:2; }

#annot-popover { position:fixed; z-index: 71; display:none; width:min(340px, calc(100vw - 32px)); background: var(--bg); border:1px solid var(--line); border-radius: var(--r-4); box-shadow: var(--shadow-3); padding: var(--sp-4); }
#annot-popover.show { display:block; }
#annot-popover .ap-quote { font-size: var(--fs-12); color: var(--ink-3); border-left: 3px solid var(--brand); padding-left: 8px; margin-bottom: var(--sp-2); max-height: 64px; overflow:hidden; }
#annot-popover .ap-trunc { font-size: var(--fs-12); color: var(--warn-ink); margin-bottom: var(--sp-2); }
#annot-popover textarea { min-height: 72px; }
#annot-popover .ap-actions { margin-top: var(--sp-2); display:flex; gap: var(--sp-2); justify-content:flex-end; }

#annot-panel { position:fixed; top:0; right:0; bottom:0; z-index: 50; width:min(360px, 100vw); background: var(--bg); border-left:1px solid var(--line); box-shadow: var(--shadow-3); transform: translateX(105%); transition: transform .22s ease; display:flex; flex-direction:column; }
#annot-panel.open { transform: none; }
@media (prefers-reduced-motion: reduce) { #annot-panel { transition: none; } }
.ap-head { flex:0 0 auto; display:flex; align-items:center; justify-content:space-between; gap: var(--sp-2); padding: var(--sp-4) var(--sp-5); border-bottom:1px solid var(--line-soft); }
.ap-head h2 { font-size: var(--fs-16); font-weight:700; }
.ap-close { min-height:44px; min-width:44px; border-radius: var(--r-3); border:1.5px solid var(--line); background: var(--bg); color: var(--ink-2); font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); cursor:pointer; }
.ap-body { flex:1 1 auto; overflow-y:auto; padding: var(--sp-4) var(--sp-5); display:flex; flex-direction:column; gap: var(--sp-3); }
.ap-empty { font-size: var(--fs-14); color: var(--ink-3); line-height: var(--lh-loose); }
.ap-section-h { font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); letter-spacing:.07em; text-transform:uppercase; color: var(--warn-ink); margin-top: var(--sp-2); }
.ap-card { background: var(--bg-soft); border:1px solid var(--line-soft); border-radius: var(--r-3); padding: var(--sp-3) var(--sp-4); }
.ap-card.orfa { border-style:dashed; border-color: color-mix(in srgb, var(--warning) 40%, var(--line)); }
.ap-card .apc-quote { font-size: var(--fs-12); color: var(--ink-3); border-left: 3px solid var(--brand); padding-left: 8px; }
.ap-card.orfa .apc-quote { border-left-color: var(--warning); }
.ap-card .apc-orfa-tag { font-family: var(--font-display); font-weight:600; font-size: 0.6875rem; color: var(--warn-ink); margin-bottom: 4px; }
.ap-card .apc-text { margin-top: var(--sp-2); font-size: var(--fs-14); color: var(--ink-2); line-height: var(--lh-normal); }
.ap-card .apc-meta { margin-top: var(--sp-2); font-family: var(--font-mono); font-size: 0.6875rem; color: var(--ink-4); word-break: break-all; }
.ap-card .apc-actions { margin-top: var(--sp-2); display:flex; gap: var(--sp-3); }
.ap-card .apc-actions button { background:none; border:0; padding: 4px 0; min-height:32px; font-family: var(--font-display); font-weight:600; font-size: var(--fs-12); color: var(--brand-ink); text-decoration:underline; cursor:pointer; }
.ap-card .apc-actions button.apc-del { color: var(--danger-ink); }
.ap-card .apc-actions button:disabled { color: var(--ink-4); text-decoration:none; cursor:default; }
#ap-undo { display:none; background: var(--warn-tint); border:1px solid color-mix(in srgb, var(--warning) 30%, var(--line)); border-radius: var(--r-3); padding: var(--sp-2) var(--sp-3); font-size: var(--fs-12); color: var(--warn-ink); }
#ap-undo.show { display:flex; align-items:center; justify-content:space-between; gap: var(--sp-2); }
#ap-undo button { background:none; border:0; min-height:32px; font-family: var(--font-display); font-weight:700; font-size: var(--fs-12); color: var(--warn-ink); text-decoration:underline; cursor:pointer; }

/* ===== Footer ===== */
.pagefoot { margin-top: var(--sp-12); border-top:1px solid var(--line); background: var(--bg); }
.pagefoot-inner { padding-top: var(--sp-6); padding-bottom: var(--sp-8); display:flex; flex-direction:column; gap: var(--sp-2); }
.pagefoot .mono { font-family: var(--font-mono); font-size: var(--fs-12); color: var(--ink-3); word-break: break-all; }
.pagefoot .foot-note { font-size: var(--fs-14); color: var(--ink-3); line-height: var(--lh-normal); max-width: 72ch; }
.pagefoot img.logo { height: 22px; width:auto; align-self: flex-start; margin-bottom: var(--sp-2); }

/* ===== Ver como documento ===== */
body.doc-mode summary.q-row { cursor: pointer; }
body.doc-mode .opt-cons { display:grid !important; grid-template-columns: 1fr 1fr; gap: var(--sp-2); }
body.doc-mode #btn-comecar { display:none; }

/* ===== Impressão: o documento inteiro, sem cromo de interação ===== */
@media print {
  body { background:#FFF; padding-bottom: 0; }
  .export-bar, #annot-bar, #annot-popover, #annot-panel, .dica-anotacao, #btn-comecar, .btn-docmode, .chev, .annot-block-btn, .preview-panel, .reset-answer { display:none !important; }
  details.q-item, .hero-card, .conf-card, details.howto { box-shadow:none; }
  .opt-cons { display:grid !important; grid-template-columns: 1fr 1fr; gap: var(--sp-2); }
  summary.q-row { min-height: 0; }
  .conf-actions { display:none; }
}

/* ===== Mobile ===== */
@media (max-width: 760px) {
  body { padding-bottom: 188px; }
  .hero-card { padding: var(--sp-4); }
  .hero-top { flex-direction: column; align-items: stretch; }
  .hero-progress { flex-wrap: wrap; }
  summary.q-row { grid-template-columns: 26px minmax(0,1fr) 16px; min-height: 76px; }
  .q-side { grid-column: 2; grid-row: 2; justify-self: start; margin-top: 4px; }
  .chev { grid-column: 3; grid-row: 1; }
  .q-line2, .q-line3 { white-space: normal; }
  article.q-card { padding: var(--sp-4); }
  .conf-card { padding: var(--sp-5); }
  .answer-row { flex-direction: column; }
  .duvida-box { flex-basis: auto; width: 100%; }
  .state-buttons { width: 100%; }
  .state-btn { flex: 1 1 auto; justify-content: center; }
  .opt-cons, .option.selected .opt-cons, body.doc-mode .opt-cons { grid-template-columns: 1fr; }
  .export-inner { display:grid; grid-template-columns: 1fr 1fr; gap: var(--sp-2); }
  .export-inner > div:first-child { grid-column: 1 / -1; display:flex; justify-content:space-between; align-items:baseline; gap: var(--sp-2); }
  .export-actions { display: contents; }
  .topbar .meta { text-align:left; }
  /* wizard vira folha inferior */
  dialog.wizard { width:100%; margin:0; inset:auto 0 0 0; max-height: 92dvh; border-radius: var(--r-5) var(--r-5) 0 0; }
  .sheet-handle { display:block; width:36px; height:4px; border-radius: var(--r-pill); background: var(--line); margin: 8px auto 0; }
  .wz-head { padding: var(--sp-3) var(--sp-4); }
  .wz-body article.q-card { padding: var(--sp-4) var(--sp-4) var(--sp-5); }
  .wz-foot { padding: var(--sp-3) var(--sp-4); padding-bottom: calc(var(--sp-3) + env(safe-area-inset-bottom)); flex-wrap: wrap; }
  .wz-dots { order: -1; width:100%; justify-content:center; }
  #annot-panel { top:auto; left:0; right:0; bottom:0; width:100%; max-height: 80dvh; border-left:0; border-top:1px solid var(--line); border-radius: var(--r-5) var(--r-5) 0 0; transform: translateY(105%); }
  #annot-panel.open { transform:none; }
}
%%FONTS%%
.anotacoes-incompletas { border:1px solid var(--warn-line, #e5c07b); background:var(--warn-tint, #fff8e6);
  border-radius:var(--r-3, 10px); padding:14px 16px; margin:0 0 12px; max-width:100%; }
.anotacoes-incompletas .ai-title { font:600 15px/1.3 var(--f-ui); margin:0 0 6px; color:var(--warn-ink, #7a5a00); }
.anotacoes-incompletas .ai-sub { font:400 14px/1.5 var(--f-body); margin:0 0 10px; color:var(--ink-2); }
.anotacoes-incompletas .ai-item { border-top:1px solid var(--warn-line, #e5c07b); padding-top:10px; margin-top:10px; }
.anotacoes-incompletas blockquote { font:400 14px/1.5 var(--f-body); margin:0 0 8px; color:var(--ink); }
.anotacoes-incompletas .ai-acoes { display:flex; gap:8px; flex-wrap:wrap; }
</style>
</head>
<body data-tarefa-id="%%TAREFA_ID%%" data-rodada="%%RODADA%%" data-export-schema="%%SCHEMA_EXPORT%%">

<noscript><div class="notice-strip" role="note">Esta página precisa de JavaScript para registrar respostas. Sem ele, você ainda pode ler todas as perguntas abaixo (toque em cada linha para abrir).</div></noscript>
%%FAIXA_EXEMPLO%%

<header class="topbar">
  <div class="container topbar-inner">
    <img class="logo" alt="QualiApps" src="%%LOGO_SRC%%">
    <div class="top-right">
      <button type="button" class="btn-docmode" id="btn-docmode" aria-pressed="false">Ver como documento</button>
      <div class="meta">
        <div class="rid">%%RID%%</div>
        <div class="rdate">%%RDATE%%</div>
      </div>
    </div>
  </div>
</header>

<main class="container">
  <section class="hero" aria-label="Resumo da rodada">
    <div class="hero-card" id="hero-card">
      <div class="hero-top">
        <div>
          <div class="eyebrow">%%EYEBROW%%</div>
          <h1>%%TITULO_HERO%%</h1>
          %%LINHA_TAREFA%%
        </div>
        <button type="button" class="btn btn-primary" id="btn-comecar">Começar</button>
      </div>
      <div class="hero-progress">
        <div class="progress" role="progressbar" aria-label="Progresso da rodada" aria-valuemin="0" aria-valuemax="%%TOTAL_PERGUNTAS_ATR%%" aria-valuenow="0" id="progress-bar-wrap"><div id="progress-bar"></div></div>
        <span class="ptext" id="progress-text">%%PROGRESSO_INICIAL%%</span>
        <a class="howto-link" href="#howto">como funciona</a>
      </div>
    </div>
  </section>

  <div id="page-notice"></div>

  <section class="lista" id="lista" aria-label="%%ARIA_LISTA%%">
%%PERGUNTAS%%
  </section>

  <div class="dica-anotacao" id="dica-anotacao"><span>Dica: selecione qualquer trecho do texto para deixar um bilhete preso a ele.</span><button type="button" id="dica-dismiss">entendi, não mostrar de novo</button></div>

  <details class="howto" id="howto">
    <summary>Como funciona esta página</summary>
    <div class="howto-body">
      <p><strong>1 · Toque numa pergunta para abrir.</strong> Cada cartão explica o porquê em linguagem comum, mostra as opções (a sugerida vem destacada) e o que você ganha e abre mão em cada uma. A escolha só vale quando você responder com um dos botões.</p>
      <p><strong>2 · Responda com um botão.</strong> Aprovar, rejeitar ou “fiquei com dúvida” — dúvida não é rejeição: a pergunta volta mais bem explicada na próxima rodada. Algumas perguntas também deixam adiar. Fechar o cartão (de qualquer jeito) sempre salva; nada se perde.</p>
      <p><strong>3 · Confira e devolva.</strong> No fim, a conferência mostra todas as respostas numa tela só. Use “Copiar as respostas” ou “Baixar o arquivo” e devolva na conversa.</p>
      <p><strong>Comentário ou anotação?</strong> Comentário (dentro do cartão) muda a minha resposta e viaja junto com ela. Anotação é um bilhete no texto: selecione um trecho e toque em “Anotar” — vai para quem escreveu o material.</p>
      <p><strong>Fique tranquilo:</strong> esta página não executa nada e não acessa a internet — ela só coleta as suas respostas. O rascunho fica salvo automaticamente neste navegador. Pode devolver com pendências: o conferente devolve apontando o que falta.</p>
    </div>
  </details>

  <section class="conferencia" id="conferencia" aria-labelledby="conf-title">
    <div class="conf-card">
      <h2 id="conf-title" tabindex="-1">Conferência final — o que você vai devolver</h2>
      <p class="conf-status" id="conf-status">Nenhuma pergunta respondida ainda. Toque numa linha para abrir e responder.</p>
      <ol class="conf-list" id="conf-list">
%%LINHAS_CONFERENCIA%%
      </ol>
      <p class="conf-duvidas" id="conf-duvidas" hidden></p>
      <div class="conf-actions">
        <div class="ca"><button type="button" class="btn btn-primary btn-copy">Copiar as respostas</button><span class="btn-legend">depois é só colar na nossa conversa</span></div>
        <div class="ca"><button type="button" class="btn btn-secondary btn-download">Baixar o arquivo</button><span class="btn-legend">salve na pasta de respostas da tarefa</span></div>
      </div>
      <p class="conf-tech">formato técnico: JSON grill-respostas-v1 · as anotações vão junto no mesmo arquivo</p>
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
    <img class="logo" alt="QualiApps" src="%%LOGO_SRC%%">
    %%RODAPE%%</div>
</footer>

<div class="export-bar" role="region" aria-label="Devolver respostas">
  <div class="export-progress" aria-hidden="true"><div id="export-progress-bar"></div></div>
  <div id="storage-alert" role="alert" hidden>O rascunho NÃO está sendo salvo neste navegador (armazenamento cheio ou bloqueado). Copie ou baixe as respostas antes de fechar a página.</div>
  <div class="container export-inner">
    <div>
      <div class="export-count" id="export-count">%%CONTAGEM_INICIAL%%</div>
      <div class="copy-feedback" id="copy-feedback" role="status" aria-live="polite"></div>
    </div>
    <div class="anotacoes-incompletas" id="anotacoes-incompletas" role="alert" hidden></div>
    <div class="anotacoes-incompletas" id="campos-estourados" role="alert" hidden></div>
    <div class="export-actions">
      <button type="button" class="btn btn-ghost" id="btn-annot-panel">Anotações (0)</button>
      <button type="button" class="btn btn-secondary btn-download">Baixar o arquivo</button>
      <button type="button" class="btn btn-primary btn-copy">Copiar as respostas</button>
    </div>
  </div>
  <div class="container export-note"><span>Esta página não executa nada — só coleta as suas respostas.</span><span id="save-promise">O rascunho fica salvo automaticamente neste navegador.</span><span class="mono">JSON grill-respostas-v1</span></div>
</div>

<dialog class="wizard" id="wizard" aria-labelledby="wizard-title">
  <div class="wz-frame">
    <div class="sheet-handle" aria-hidden="true"></div>
    <header class="wz-head">
      <div class="wz-eyebrow" id="wizard-eyebrow">Pergunta 1 de %%TOTAL_PERGUNTAS_TEXTO%%</div>
      <h2 class="wz-title" id="wizard-title" tabindex="-1"></h2>
      <button type="button" class="wz-close" id="wizard-close">Salvar e fechar</button>
    </header>
    <div class="wz-notice" id="wizard-notice" hidden></div>
    <div class="wz-body" id="wizard-body"></div>
    <footer class="wz-foot">
      <button type="button" class="btn btn-ghost" id="wz-prev">Anterior</button>
      <div class="wz-dots" id="wz-dots" role="group" aria-label="Ir direto para outra pergunta"></div>
      <button type="button" class="btn btn-primary" id="wz-next">Salvar e ver a próxima</button>
    </footer>
  </div>
</dialog>

<aside id="annot-panel" aria-label="Anotações" aria-hidden="true">
  <div class="ap-head">
    <h2 id="ap-title">Anotações (0)</h2>
    <button type="button" class="ap-close" id="ap-close">Fechar</button>
  </div>
  <div class="ap-body" id="ap-body"></div>
</aside>

<div id="annot-bar"><button type="button" id="annot-bar-btn"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>Anotar</button></div>

<div id="annot-popover" role="dialog" aria-label="Nova anotação">
  <div class="ap-quote" id="ap-quote"></div>
  <div class="ap-trunc" id="ap-trunc" hidden>Anotei só o trecho do primeiro parágrafo selecionado.</div>
  <label class="sr-only" for="ap-textarea">Texto da anotação</label>
  <textarea id="ap-textarea" maxlength="%%MAX_ANOTACAO%%" placeholder="O que você quer dizer sobre este trecho?"></textarea>
  <div class="ap-actions">
    <button type="button" class="btn btn-ghost" id="ap-cancel">Cancelar</button>
    <button type="button" class="btn btn-primary" id="ap-save">Salvar anotação</button>
  </div>
</div>

<div id="announcer" class="sr-only" role="status" aria-live="polite"></div>

<script type="application/json" id="contrato-json">%%CONTRATO_JSON%%</script>
<script>
/* Protótipo temcomo v2 — wizard puro sobre conteúdo real renderizado.
   Regras do conselho de direção visual implementadas aqui:
   - rascunho ≠ export: o localStorage guarda o estado SEM PERDAS (duvida_texto sobrevive a troca de estado + reload);
   - nada é gravado no boot (sem decisão fantasma); export distingue "pendente" (escolha_id null);
   - "salvar e próximo" troca o conteúdo do MESMO dialog (nunca close()+showModal(): o evento close é assíncrono);
   - Esc/fundo/× sempre salvam; backdrop exige pointerdown E pointerup no fundo (arrastar seleção não fecha);
   - contextmenu só é interceptado com seleção válida dentro de [data-anotavel] e fora de campos;
   - anotações ancoradas por bloco+trecho+offsets sobre o texto pristino; órfã é preservada e marcada;
   - erros de quota do localStorage são visíveis (nunca catch mudo);
   - window.__temcomo é um gancho SOMENTE-LEITURA para o verificador determinístico (não executa nada). */
(function () {
  "use strict";
  var BOOT_OK = false;
  try {

  var CONTRATO = JSON.parse(document.getElementById("contrato-json").textContent);

  /* Dado do contrato NUNCA entra em seletor: um id com aspas montaria seletor inválido
     e derrubaria o boot inteiro. A busca é por comparação de atributo, em JavaScript. */
  function elemPorDado(seletor, atributo, valor) {
    var achados = document.querySelectorAll(seletor);
    for (var i = 0; i < achados.length; i++) {
      if (achados[i].getAttribute(atributo) === valor) return achados[i];
    }
    return null;
  }
  function elemPorDadoEm(escopo, seletor, atributo, valor) {
    var achados = escopo ? escopo.querySelectorAll(seletor) : [];
    for (var i = 0; i < achados.length; i++) {
      if (achados[i].getAttribute(atributo) === valor) return achados[i];
    }
    return null;
  }
  var TAREFA_ID = CONTRATO.tarefa_id;
  var RODADA = CONTRATO.rodada;
  var EXPORT_SCHEMA = CONTRATO.export.schema_version;
  var STORAGE_KEY = CONTRATO.export.chave_localstorage;
  var DOWNLOAD_NAME = CONTRATO.export.nome_arquivo;
  var CONTRATO_SHA = "%%CONTRATO_SHA%%";
  var PERGUNTAS = CONTRATO.perguntas;
  var TOTAL = PERGUNTAS.length;
  var IDX = Object.create(null); PERGUNTAS.forEach(function (q, i) { IDX[q.id] = i; });

  var WIZARD_OK = (typeof HTMLDialogElement === "function" || typeof HTMLDialogElement === "object") &&
                  !!document.getElementById("wizard") &&
                  typeof document.getElementById("wizard").showModal === "function";

  var ESTADOS = ["pendente", "aprovada", "rejeitada", "duvida", "adiada"];
  var BOTAO_ESTADO = { aprovar: "aprovada", rejeitar: "rejeitada", duvida: "duvida", adiar: "adiada" };
  var CHIP = {
    pendente: { txt: "Falta responder", cls: "" },
    aprovada: { txt: "Respondido", cls: "s-ok" },
    rejeitada: { txt: "Respondido", cls: "s-ok" },
    duvida: { txt: "Você pediu para explicarem melhor", cls: "s-duvida" },
    adiada: { txt: "Deixei para depois", cls: "s-adiada" }
  };
  var HELP_TEXT = {
    pendente: "Falta responder: esta pergunta sai no arquivo como pendente, e o conferente devolve a rodada apontando o que faltou.",
    aprovada: "Respondido: vale a opção marcada acima. Quer outra? Troque a opção — a resposta acompanha.",
    rejeitada: "Você recusou as opções. Conte no comentário o que faria sentido, para a próxima rodada vir melhor.",
    duvida: "Você pediu para explicarem melhor — não é rejeição: a pergunta volta reformulada na próxima rodada. Descrever a dúvida ajuda, mas pode ficar em branco.",
    adiada: "Deixei para depois: fica sem definição por agora, sem travar as demais. Volta numa rodada futura."
  };

  function $(id) { return document.getElementById(id); }
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined && text !== null) n.textContent = text;
    return n;
  }
  function novoId(prefixo) {
    var r = (window.crypto && typeof crypto.randomUUID === "function") ? crypto.randomUUID().slice(0, 13) : (Date.now().toString(36) + Math.random().toString(36).slice(2, 8));
    return prefixo + "-" + r;
  }
  function optDe(q, oid) { for (var i = 0; i < q.opcoes.length; i++) if (q.opcoes[i].id === oid) return q.opcoes[i]; return null; }
  function recomendadaDe(q) { for (var i = 0; i < q.opcoes.length; i++) if (q.opcoes[i].recomendada) return q.opcoes[i]; return q.opcoes[0]; }

  /* ===== rascunho (estado de trabalho completo, sem projeção) ===== */
  var draft = {
    rascunho_versao: 2,
    schema_export: EXPORT_SCHEMA,
    tarefa_id: TAREFA_ID,
    rodada: RODADA,
    contrato_sha256: CONTRATO_SHA,
    atualizado_em: null,
    respostas: Object.create(null),
    anotacoes: [],
    ui: { dica_anotacao_dispensada: false }
  };
  PERGUNTAS.forEach(function (q) {
    draft.respostas[q.id] = { estado: "pendente", escolha_id: recomendadaDe(q).id, comentario: "", duvida_texto: "" };
  });

  var interacted = false;      // nada é persistido antes da primeira ação do usuário
  var storageOk = true;
  var persistTimer = null;

  function storageFalhou() {
    storageOk = false;
    var alerta = $("storage-alert");
    alerta.hidden = false;
    var promessa = $("save-promise");
    promessa.textContent = "O rascunho NÃO está sendo salvo — copie ou baixe as respostas antes de fechar.";
    promessa.classList.add("falhou");
  }
  function persistNow() {
    if (!interacted) return;
    draft.atualizado_em = new Date().toISOString();
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(draft));
      if (!storageOk) { /* voltou a funcionar: mantém o alerta por honestidade até reload */ }
    } catch (e) { storageFalhou(); }
  }
  function persist() {
    if (persistTimer) clearTimeout(persistTimer);
    persistTimer = setTimeout(persistNow, 250);
  }
  function flush() { if (persistTimer) { clearTimeout(persistTimer); persistTimer = null; } persistNow(); }
  document.addEventListener("visibilitychange", function () { if (document.visibilityState === "hidden") flush(); });
  window.addEventListener("pagehide", flush);

  /* sonda de escrita no boot (não deixa promessa falsa em pé) */
  try { localStorage.setItem(STORAGE_KEY + ":sonda", "1"); localStorage.removeItem(STORAGE_KEY + ":sonda"); } catch (e) { storageFalhou(); }

  /* ===== avisos de página ===== */
  function pageNotice(texto, acoes) {
    var box = el("div", "pnotice");
    box.appendChild(el("span", null, texto));
    var act = el("div", "pn-actions");
    (acoes || [{ rotulo: "entendi" }]).forEach(function (a) {
      var b = el("button", null, a.rotulo);
      b.type = "button";
      b.addEventListener("click", function () { if (a.fn) a.fn(); box.remove(); });
      act.appendChild(b);
    });
    box.appendChild(act);
    $("page-notice").appendChild(box);
  }

  /* ===== restauração + migração (nunca descartar em silêncio) ===== */
  function restore() {
    var raw = null;
    try { raw = localStorage.getItem(STORAGE_KEY); } catch (e) { return; }
    if (!raw) return;
    var saved = null;
    try { saved = JSON.parse(raw); } catch (e) {
      try { localStorage.setItem(STORAGE_KEY + ":backup:ilegivel", raw); } catch (e2) {}
      pageNotice("Encontramos um rascunho antigo que não conseguimos ler. Guardamos uma cópia e começamos do zero.");
      return;
    }
    if (!saved || typeof saved !== "object") return;

    if (saved.rascunho_versao === 2 && saved.tarefa_id === TAREFA_ID && saved.rodada === RODADA) {
      PERGUNTAS.forEach(function (q) {
        var r = saved.respostas && saved.respostas[q.id];
        if (!r || typeof r !== "object") return;
        var s = draft.respostas[q.id];
        if (ESTADOS.indexOf(r.estado) !== -1) s.estado = r.estado;
        if (optDe(q, r.escolha_id)) s.escolha_id = r.escolha_id;
        if (typeof r.comentario === "string") s.comentario = r.comentario;
        if (typeof r.duvida_texto === "string") s.duvida_texto = r.duvida_texto;
      });
      if (Array.isArray(saved.anotacoes)) {
        draft.anotacoes = sanitizarAnotacoes(saved.anotacoes);
      }
      if (saved.ui && typeof saved.ui === "object") draft.ui.dica_anotacao_dispensada = !!saved.ui.dica_anotacao_dispensada;
      interacted = true;
      if (saved.contrato_sha256 && saved.contrato_sha256 !== CONTRATO_SHA) {
        pageNotice("Este relatório foi atualizado desde o seu último rascunho. Suas respostas e anotações foram preservadas; anotações cujo trecho mudou aparecem marcadas no painel de anotações.");
      }
      return;
    }

    if (saved.schema_version === EXPORT_SCHEMA && Array.isArray(saved.respostas)) {
      /* rascunho da versão 1 do protótipo: migrar campo a campo, com backup */
      try { localStorage.setItem(STORAGE_KEY + ":backup:v1", raw); } catch (e3) {}
      saved.respostas.forEach(function (r) {
        if (!r || typeof r !== "object" || !draft.respostas[r.pergunta_id]) return;
        var q = PERGUNTAS[IDX[r.pergunta_id]];
        var s = draft.respostas[r.pergunta_id];
        if (ESTADOS.indexOf(r.estado) !== -1) s.estado = r.estado;
        if (optDe(q, r.escolha_id)) s.escolha_id = r.escolha_id;
        if (typeof r.comentario === "string") s.comentario = r.comentario;
        if (typeof r.duvida_texto === "string") s.duvida_texto = r.duvida_texto;
      });
      interacted = true;
      flush();
      pageNotice("Encontramos um rascunho seu da versão anterior desta página e trouxemos as respostas. Confira antes de devolver (guardamos uma cópia do original).", [
        { rotulo: "ok, entendi" },
        { rotulo: "descartar esse rascunho antigo", fn: function () {
            PERGUNTAS.forEach(function (q) { draft.respostas[q.id] = { estado: "pendente", escolha_id: recomendadaDe(q).id, comentario: "", duvida_texto: "" }; });
            flush(); syncAll();
          } }
      ]);
      return;
    }

    try { localStorage.setItem(STORAGE_KEY + ":backup:desconhecido", raw); } catch (e4) {}
    pageNotice("Encontramos um rascunho de um formato que esta página não reconhece. Guardamos uma cópia e começamos do zero.");
  }

  /* ===== Decisão 17 (2026-08-20): rascunho restaurado com anotação incompleta
     trava o envio até você decidir, uma a uma. O sistema nunca descarta sozinho. ===== */
  var TRECHO_NAO_RECUPERADO = "(trecho não recuperado do rascunho)";
  var BLOCO_NAO_RECUPERADO = "(bloco não recuperado do rascunho)";

  /* Mesma régua do motor: o que não aparece para quem lê não conta como conteúdo. A
     regra é por categoria Unicode; navegador antigo degrada em vez de quebrar a página. */
  var SEM_CONTEUDO = (function () {
    try { return new RegExp("[\\p{Cf}\\p{Cc}\\p{Z}]", "gu"); }
    catch (e) { return /\s/g; }
  })();
  function temConteudo(s) {
    return typeof s === "string" && s.replace(SEM_CONTEUDO, "") !== "";
  }
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
  function escTexto(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  function sanitizeAnnot(a) {
    /* Nada que você escreveu é jogado fora sem você mandar: anotação que perdeu o
       trecho OU a âncora volta marcada como incompleta e vai para a fila. Só some
       quando não há nada humano a preservar. */
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
      ancora_status: (temBloco && temTrecho) ? (a.ancora_status === "truncada" ? "truncada"
                                                                              : "resolvida")
                                             : "orfa",
      ancora_truncada: !!a.ancora_truncada,
      trecho: temTrecho ? a.trecho : "",
      incompleta: !(temBloco && temTrecho),
      resolucao: a.resolucao === "manter" ? "manter" : null,
      prefixo: typeof a.prefixo === "string" ? a.prefixo : "",
      sufixo: typeof a.sufixo === "string" ? a.sufixo : "",
      inicio: typeof a.inicio === "number" ? a.inicio : 0,
      fim: typeof a.fim === "number" ? a.fim : 0,
      comentario: a.comentario,
      criado_em: typeof a.criado_em === "string" ? a.criado_em : ""
    };
  }

  function sanitizarAnotacoes(lista) {
    var vistos = Object.create(null);
    return (Array.isArray(lista) ? lista : []).map(sanitizeAnnot).filter(Boolean)
      .map(function (a) {
        while (Object.prototype.hasOwnProperty.call(vistos, a.id)) a.id = annotId();
        vistos[a.id] = true;
        return a;
      });
  }

  /* Perder a âncora é condição semântica, não campo vazio: se o bloco não existe mais
     no documento, a anotação volta para a fila — a não ser que você já tenha mandado
     manter. */
  function registrarAncoraPerdida(a) {
    a.ancora_status = "orfa";
    if (a.resolucao !== "manter") a.incompleta = true;
    return a;
  }

  function anotacoesPendentes() {
    return draft.anotacoes.filter(function (a) {
      return a.incompleta && a.resolucao !== "manter";
    });
  }
  function resolverAnotacao(id, decisao) {
    for (var i = 0; i < draft.anotacoes.length; i++) {
      if (draft.anotacoes[i].id !== id) continue;
      if (decisao === "descartar") draft.anotacoes.splice(i, 1);   /* só com clique seu */
      else draft.anotacoes[i].resolucao = "manter";
      break;
    }
    persistNow();
    paintAll();
  }
  function botoesDeEnvio() {
    return document.querySelectorAll(".btn-copy, .btn-download");
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
    (draft.anotacoes || []).forEach(function (a, i) {
      conferirLimite(lista, "Anotação " + (i + 1) + " (“" +
        String(a.trecho || "").slice(0, 30) + "”)", a.comentario,
        LIMITES_DE_TEXTO.anotacao, { tipo: "anotacao", id: a.id });
    });
    Object.keys(draft.respostas || {}).forEach(function (qid) {
      var r = draft.respostas[qid] || {};
      conferirLimite(lista, "Comentário da pergunta " + qid, r.comentario,
                     LIMITES_DE_TEXTO.comentario,
                     { tipo: "campo", id: "comentario-" + qid });
      conferirLimite(lista, "Dúvida da pergunta " + qid, r.duvida_texto,
                     LIMITES_DE_TEXTO.duvida, { tipo: "campo", id: "duvida-" + qid });
    });
    return lista;
  }
  function anotacaoPorId(id) {
    return (draft.anotacoes || []).filter(function (a) { return a.id === id; })[0] || null;
  }
  function editarAnotacao(id, texto) {
    var a = anotacaoPorId(id);
    if (!a) return false;
    a.comentario = typeof texto === "string" ? texto : a.comentario;
    persistNow();
    atualizarTravas();
    rebuildPanel();          /* nome real do painel deste template */
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
    Array.prototype.forEach.call(botoesDeEnvio(), function (b) { b.disabled = travado; });
  }
  function aoDigitarNoCampoPrincipal() {
    atualizarTravas();
  }

  function pintarAnotacoesIncompletas() {
    var caixa = document.getElementById("anotacoes-incompletas");
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
      b.addEventListener("click", function () {
        resolverAnotacao(b.getAttribute("data-manter"), "manter");
      });
    });
    Array.prototype.forEach.call(caixa.querySelectorAll("[data-descartar]"), function (b) {
      b.addEventListener("click", function () {
        resolverAnotacao(b.getAttribute("data-descartar"), "descartar");
      });
    });
  }

  /* ===== export = função pura do rascunho; gerado_em = instante da ação ===== */
  function buildEnvelope(momentoISO) {
    momentoISO = momentoISO || new Date().toISOString();
    return {
      schema_version: EXPORT_SCHEMA,
      tarefa_id: TAREFA_ID,
      rodada: RODADA,
      gerado_em: momentoISO,
      /* decisão 20: a resposta carrega a impressão digital da rodada que foi respondida —
         se as perguntas mudarem depois, o motor percebe e bloqueia */
      contrato_sha256: CONTRATO_SHA,
      produzido_por: { agente: "usuario" },
      respostas: PERGUNTAS.map(function (q) {
        var s = draft.respostas[q.id];
        return {
          pergunta_id: q.id,
          estado: s.estado,
          escolha_id: s.estado === "pendente" ? null : s.escolha_id,
          comentario: s.comentario,
          duvida_texto: s.duvida_texto
        };
      }),
      anotacoes: draft.anotacoes.map(function (a) {
        /* Decisão 17: mantida com âncora perdida sai marcada como órfã. Valor real é
           preservado quando existe; o marcador entra só no campo que ficou vazio. */
        var trecho = a.trecho, bloco = a.bloco_id, status = a.ancora_status;
        var criado = a.criado_em;
        if (a.incompleta) {
          if (!trecho) trecho = TRECHO_NAO_RECUPERADO;
          if (!bloco) bloco = BLOCO_NAO_RECUPERADO;
          status = "orfa";
          if (!criado || criado.length < 10) criado = momentoISO;
        }
        return { id: a.id, item_id: a.item_id, bloco_id: bloco, ancora_tipo: a.ancora_tipo,
          ancora_status: status, trecho: trecho, prefixo: a.prefixo, sufixo: a.sufixo,
          inicio: a.inicio, fim: a.fim, comentario: a.comentario, criado_em: criado };
      })
    };
  }
  function buildJSON() { return JSON.stringify(buildEnvelope(), null, 2); }
  window.__temcomo = { exportJson: buildJSON };   /* gancho somente-leitura do verificador */

  /* ===== contagens e textos globais ===== */
  function counts() {
    var c = { pendente: 0, aprovada: 0, rejeitada: 0, duvida: 0, adiada: 0 };
    PERGUNTAS.forEach(function (q) { c[draft.respostas[q.id].estado]++; });
    return c;
  }
  function announce(msg) { $("announcer").textContent = msg; }

  function outcomeText(q, s) {
    if (s.estado === "aprovada") {
      var o = optDe(q, s.escolha_id);
      return { html: "Sua escolha: <strong>" + escapeHtml(o ? o.titulo : "") + "</strong>" + (s.comentario ? " · com comentário" : ""), cls: "" };
    }
    if (s.estado === "rejeitada") return { html: "Você recusou as opções" + (s.comentario ? " · com comentário" : ""), cls: "" };
    if (s.estado === "duvida") return { html: "Vai voltar mais bem explicada na próxima rodada", cls: "" };
    if (s.estado === "adiada") return { html: "Sem definição por agora; volta numa rodada futura", cls: "" };
    return null;
  }
  function escapeHtml(t) { var d = document.createElement("div"); d.textContent = t; return d.innerHTML; }

  function updateRow(qid) {
    var q = PERGUNTAS[IDX[qid]];
    var s = draft.respostas[qid];
    var item = elemPorDado('details.q-item', 'data-pergunta-id', qid);
    if (!item) return;
    var chip = item.querySelector(".status-chip");
    chip.textContent = CHIP[s.estado].txt;
    chip.className = "status-chip " + CHIP[s.estado].cls;
    var impact = item.querySelector(".q-impact");
    var outcome = item.querySelector(".q-outcome");
    var out = outcomeText(q, s);
    if (out) { outcome.innerHTML = out.html; outcome.hidden = false; impact.hidden = true; }
    else { outcome.hidden = true; impact.hidden = false; }
    var nAn = draft.anotacoes.filter(function (a) { return a.item_id === qid; }).length;
    var an = item.querySelector(".q-annot");
    an.hidden = nAn === 0;
    an.querySelector(".q-annot-n").textContent = String(nAn);
    /* dentro do cartão — buscar por id: o article pode estar em casa OU dentro do wizard */
    var card = elemPorDado('article.q-card', 'data-pergunta-id', qid);
    if (!card) return;
    card.querySelectorAll(".state-btn").forEach(function (btn) {
      btn.setAttribute("aria-pressed", BOTAO_ESTADO[btn.getAttribute("data-botao")] === s.estado ? "true" : "false");
    });
    var help = card.querySelector(".decision-help");
    help.textContent = HELP_TEXT[s.estado];
    help.className = "decision-help" + (s.estado === "pendente" ? "" : " h-" + s.estado);
    card.querySelector(".duvida-box").hidden = s.estado !== "duvida";
    card.querySelector(".reset-answer").hidden = s.estado === "pendente";
    card.querySelectorAll(".option").forEach(function (opt) {
      var input = opt.querySelector('input[type="radio"]');
      opt.classList.toggle("selected", input.value === s.escolha_id);
      if (input.value === s.escolha_id && !input.checked) input.checked = true;
    });
  }

  function updateGlobal() {
    var c = counts();
    var done = TOTAL - c.pendente;
    var txt = done + " de " + TOTAL + " respondidas — faltam " + c.pendente;
    if (c.pendente === 0) txt = "As " + TOTAL + " perguntas foram respondidas";
    if (c.duvida > 0) txt += " · " + c.duvida + " para explicarem melhor";
    $("progress-text").textContent = txt;
    $("export-count").textContent = txt;
    var pct = (done / TOTAL * 100) + "%";
    $("progress-bar").style.width = pct;
    $("export-progress-bar").style.width = pct;
    $("progress-bar-wrap").setAttribute("aria-valuenow", String(done));
    /* botão começar */
    var btn = $("btn-comecar");
    if (done === 0) btn.textContent = "Começar";
    else if (c.pendente > 0) btn.textContent = "Continuar — faltam " + c.pendente;
    else btn.textContent = "Conferir e devolver";
    /* comece por aqui */
    var badge = document.querySelector(".q-start-badge");
    if (badge) badge.hidden = done !== 0;
    /* conferência */
    var st = $("conf-status");
    if (done === 0) { st.textContent = "Nenhuma pergunta respondida ainda. Toque numa linha para abrir e responder."; st.classList.remove("pronto"); }
    else if (c.pendente > 0) { st.textContent = "Você respondeu " + done + " das " + TOTAL + " perguntas — faltam " + c.pendente + ". Dá para devolver assim, mas o conferente vai pedir as que faltam."; st.classList.remove("pronto"); }
    else { st.textContent = "Pronto para me devolver: você respondeu as " + TOTAL + " perguntas. Agora é só copiar (ou baixar) e mandar na conversa."; st.classList.add("pronto"); }
    var cd = $("conf-duvidas");
    if (c.duvida > 0) { cd.hidden = false; cd.textContent = (c.duvida === 1 ? "1 pergunta volta reformulada" : c.duvida + " perguntas voltam reformuladas") + " na próxima rodada — você pediu para explicarem melhor."; }
    else cd.hidden = true;
    PERGUNTAS.forEach(function (q) {
      var s = draft.respostas[q.id];
      var li = (function () { var _e = elemPorDado('#conf-list li', 'data-pergunta-id', q.id); return _e ? _e.querySelector('.cf-a') : null; })();
      if (!li) return;
      var extras = [];
      if (s.comentario) extras.push("1 comentário");
      var nAn = draft.anotacoes.filter(function (a) { return a.item_id === q.id; }).length;
      if (nAn) extras.push(nAn === 1 ? "1 anotação" : nAn + " anotações");
      var sufixo = extras.length ? " · " + extras.join(" · ") : "";
      li.classList.remove("cf-pend", "cf-duvida", "cf-adiada");
      if (s.estado === "pendente") { li.classList.add("cf-pend"); li.innerHTML = "<strong>Falta responder</strong>" + sufixo; }
      else if (s.estado === "aprovada") { var o = optDe(q, s.escolha_id); li.innerHTML = "<strong>Aprovado — " + escapeHtml(o ? o.titulo : "") + "</strong>" + sufixo; }
      else if (s.estado === "rejeitada") { li.innerHTML = "<strong>Você recusou as opções</strong>" + sufixo; }
      else if (s.estado === "duvida") { li.classList.add("cf-duvida"); li.innerHTML = "<strong>Você pediu para explicarem melhor</strong>" + (s.duvida_texto ? " · dúvida descrita" : "") + sufixo; }
      else { li.classList.add("cf-adiada"); li.innerHTML = "<strong>Deixei para depois</strong>" + sufixo; }
    });
    updateWizardChrome();
    updatePanelCount();
    resetCopyButtons(false);
  }

  function syncAll() {
    pintarAnotacoesIncompletas();
    PERGUNTAS.forEach(function (q) {
      var s = draft.respostas[q.id];
      var item = elemPorDado('details.q-item', 'data-pergunta-id', q.id);
      var input = elemPorDadoEm(item, 'input', 'value', s.escolha_id);
      if (input) input.checked = true;
      var dTa = item.querySelector("textarea.duvida-texto");
      dTa.value = s.duvida_texto; autogrow(dTa);
      var cTa = item.querySelector("textarea.question-comment");
      cTa.value = s.comentario; autogrow(cTa);
      updateRow(q.id);
    });
    updateGlobal();
  }

  function autogrow(ta) { ta.style.height = "auto"; ta.style.height = (ta.scrollHeight + 2) + "px"; }

  /* ===== wizard: um único dialog; o conteúdo (article) é MOVIDO, nunca recriado ===== */
  var dlg = $("wizard");
  var wzBody = $("wizard-body");
  var current = null;           // qid aberto no wizard
  var originSummary = null;     // para devolver o foco
  var homeOf = Object.create(null); // qid -> .q-home
  PERGUNTAS.forEach(function (q) {
    homeOf[q.id] = (function () { var _e = elemPorDado('details.q-item', 'data-pergunta-id', q.id); return _e ? _e.querySelector('.q-home') : null; })();
  });
  function articleOf(qid) { return elemPorDado('article.q-card', 'data-pergunta-id', qid); }

  function returnArticleHome() {
    if (current && articleOf(current) && articleOf(current).parentNode === wzBody) {
      homeOf[current].appendChild(articleOf(current));
    }
  }
  function buildDots() {
    var box = $("wz-dots");
    box.textContent = "";
    PERGUNTAS.forEach(function (q, i) {
      var b = el("button", "wz-dot");
      b.type = "button";
      b.setAttribute("data-qid", q.id);
      b.setAttribute("aria-label", "Pergunta " + (i + 1) + ": " + q.pergunta);
      box.appendChild(b);
    });
  }
  function pendentes() { return PERGUNTAS.filter(function (q) { return draft.respostas[q.id].estado === "pendente"; }); }
  function updateWizardChrome() {
    if (!current) return;
    var i = IDX[current];
    $("wizard-eyebrow").textContent = "Pergunta " + (i + 1) + " de " + TOTAL;
    $("wizard-title").textContent = PERGUNTAS[i].pergunta;
    $("wz-prev").disabled = i === 0;
    var resto = pendentes().filter(function (q) { return q.id !== current; });
    $("wz-next").textContent = resto.length ? "Salvar e ver a próxima" : "Salvar e conferir tudo";
    document.querySelectorAll(".wz-dot").forEach(function (d, di) {
      d.classList.toggle("done", draft.respostas[PERGUNTAS[di].id].estado !== "pendente");
      d.classList.toggle("cur", di === i);
      d.setAttribute("aria-current", di === i ? "true" : "false");
    });
  }
  function mountArticle(qid) {
    returnArticleHome();
    current = qid;
    wzBody.appendChild(articleOf(qid));
    wzBody.scrollTop = 0;
    updateWizardChrome();
    $("wizard-notice").hidden = true;
  }
  function openWizard(qid, fromEl) {
    if (!WIZARD_OK) { var it = elemPorDado('details.q-item', 'data-pergunta-id', qid); if (it) it.open = true; return; }
    closePanel();
    originSummary = fromEl || (function () { var _e = elemPorDado('details.q-item', 'data-pergunta-id', qid); return _e ? _e.querySelector('summary') : null; })();
    mountArticle(qid);
    /* barra/popover de anotação precisam viver dentro do top-layer enquanto o dialog está aberto */
    dlg.appendChild($("annot-bar"));
    dlg.appendChild($("annot-popover"));
    if (!dlg.open) {
      document.documentElement.classList.add("modal-open");
      dlg.showModal();
    }
    $("wizard-title").focus();
  }
  function swapTo(qid, aviso) {
    flush();
    wzBody.classList.add("fade");
    mountArticle(qid);
    if (aviso) { var n = $("wizard-notice"); n.textContent = aviso; n.hidden = false; }
    requestAnimationFrame(function () { wzBody.classList.remove("fade"); });
    $("wizard-title").focus();
  }
  /* Housekeeping de fechamento é SÍNCRONO e idempotente: o evento close é assíncrono
     (e em Chrome headless pode nem disparar) — nunca dependa dele para estado. */
  function afterClose(qid) {
    document.body.appendChild($("annot-bar"));
    document.body.appendChild($("annot-popover"));
    hideAnnotBar(); hidePopover();
    document.documentElement.classList.remove("modal-open");
    current = null;
    if (qid) {
      var item = elemPorDado('details.q-item', 'data-pergunta-id', qid);
      var chip = item.querySelector(".status-chip");
      chip.classList.remove("pulse"); void chip.offsetWidth; chip.classList.add("pulse");
      /* o foco volta à linha do item que estava aberto (linha "de origem" atual) */
      var summ = item.querySelector("summary") || originSummary;
      if (summ) summ.focus();
    }
  }
  function closeWizard() {
    if (!dlg.open) return;
    flush();
    var qid = current;
    returnArticleHome();
    dlg.close();
    afterClose(qid);
  }
  dlg.addEventListener("close", function () {
    /* Rede de segurança para fechamentos iniciados pelo UA; nunca persistir aqui.
       O evento close é assíncrono e pode chegar ATRASADO, depois de o wizard já ter
       sido reaberto — nesse caso dlg.open é true e o evento é obsoleto: ignorar. */
    if (current && !dlg.open) { var qid = current; returnArticleHome(); afterClose(qid); }
  });
  dlg.addEventListener("cancel", function (e) {
    if (popoverAberto) { e.preventDefault(); hidePopover(); return; }  /* Esc fecha primeiro o popover */
    e.preventDefault();
    closeWizard();  /* Esc = salvar e fechar (caminho único, síncrono); nunca prender o usuário */
  });
  /* backdrop: fechar SÓ com pointerdown E pointerup no fundo (arrastar seleção não fecha) */
  var downOnBackdrop = false;
  dlg.addEventListener("pointerdown", function (e) { downOnBackdrop = (e.target === dlg); });
  dlg.addEventListener("pointerup", function (e) {
    if (downOnBackdrop && e.target === dlg) closeWizard();
    downOnBackdrop = false;
  });

  /* ===== estados / respostas ===== */
  function setEstado(qid, novo) {
    interacted = true;
    var s = draft.respostas[qid];
    s.estado = novo;
    updateRow(qid);
    updateGlobal();
    flush();
    var i = IDX[qid], c = counts();
    announce("Pergunta " + (i + 1) + " respondida: " + CHIP[novo].txt + ". Faltam " + c.pendente + ".");
    if (novo === "duvida") {
      var box = articleOf(qid).querySelector(".duvida-box");
      box.hidden = false;
      var ta = box.querySelector("textarea"); autogrow(ta); ta.focus();
    }
  }

  /* ===== anotações ===== */
  var pristine = {};   // bloco_id -> texto pristino
  var blocoEl = {};    // bloco_id -> elemento
  function snapshotBlocks() {
    document.querySelectorAll("[data-anotavel]").forEach(function (b) {
      var id = b.getAttribute("data-bloco-id");
      pristine[id] = b.textContent;
      blocoEl[id] = b;
      var btn = el("button", "annot-block-btn", "Anotar este bloco");
      btn.type = "button";
      btn.setAttribute("data-bloco-btn", id);
      b.appendChild(btn);
    });
  }
  function resolveAnchor(a) {
    var p = pristine[a.bloco_id];
    if (typeof p !== "string") return null;
    if (a.ancora_tipo === "bloco") return { inicio: 0, fim: 0 };
    if (typeof a.inicio === "number" && p.slice(a.inicio, a.fim) === a.trecho) return { inicio: a.inicio, fim: a.fim };
    if (a.trecho) {
      var from = Math.max(0, (a.inicio || 0) - 200);
      var idx = p.indexOf(a.trecho, from);
      if (idx !== -1 && idx <= (a.inicio || 0) + 200) return { inicio: idx, fim: idx + a.trecho.length };
      var first = p.indexOf(a.trecho);
      if (first !== -1 && p.indexOf(a.trecho, first + 1) === -1) return { inicio: first, fim: first + a.trecho.length };
    }
    return null;
  }
  function paintAll() {
    /* re-resolve tudo a partir do pristino e repinta bloco a bloco (segmentado; nunca marca aninhada) */
    var porBloco = {};
    draft.anotacoes.forEach(function (a) {
      var r = (blocoEl[a.bloco_id]) ? resolveAnchor(a) : null;
      if (!r) { registrarAncoraPerdida(a); }
      else { a.ancora_status = a.ancora_truncada ? "truncada" : "resolvida"; }
      if (r && a.ancora_tipo !== "bloco") {
        (porBloco[a.bloco_id] = porBloco[a.bloco_id] || []).push({ a: a, inicio: r.inicio, fim: r.fim });
      }
    });
    Object.keys(blocoEl).forEach(function (bid) {
      var b = blocoEl[bid];
      var btn = b.querySelector(".annot-block-btn");
      b.textContent = pristine[bid];
      var nBloco = draft.anotacoes.filter(function (a) { return a.bloco_id === bid && a.ancora_tipo === "bloco" && a.ancora_status !== "orfa"; }).length;
      b.classList.toggle("annot-bloco", nBloco > 0);
      var list = (porBloco[bid] || []).slice().sort(function (x, y) { return x.inicio - y.inicio || x.fim - y.fim; });
      if (list.length) {
        var bounds = [0, pristine[bid].length];
        list.forEach(function (r) { bounds.push(r.inicio, r.fim); });
        bounds = bounds.filter(function (v, i, arr) { return arr.indexOf(v) === i; }).sort(function (a2, b2) { return a2 - b2; });
        b.textContent = "";
        for (var i = 0; i < bounds.length - 1; i++) {
          var st = bounds[i], en = bounds[i + 1];
          if (st === en) continue;
          var cobre = list.filter(function (r) { return r.inicio <= st && r.fim >= en; });
          var txt = pristine[bid].slice(st, en);
          if (cobre.length) {
            var m = el("mark", "annot", txt);
            m.setAttribute("data-annot-ids", cobre.map(function (r) { return r.a.id; }).join(" "));
            b.appendChild(m);
          } else b.appendChild(document.createTextNode(txt));
          var terminam = list.filter(function (r) { return r.fim === en; });
          if (terminam.length) {
            var badge = el("button", "annot-badge", String(terminam.length));
            badge.type = "button";
            badge.setAttribute("data-annot-id", terminam[terminam.length - 1].a.id);
            badge.setAttribute("aria-label", terminam.length + (terminam.length === 1 ? " anotação neste trecho" : " anotações neste trecho"));
            b.appendChild(badge);
          }
        }
      }
      if (nBloco > 0) {
        var bb = el("button", "annot-badge", String(nBloco));
        bb.type = "button";
        bb.setAttribute("data-annot-bloco", bid);
        bb.setAttribute("aria-label", nBloco + " anotação(ões) neste bloco");
        b.appendChild(bb);
      }
      if (btn) b.appendChild(btn); else {
        var nb = el("button", "annot-block-btn", "Anotar este bloco");
        nb.type = "button"; nb.setAttribute("data-bloco-btn", bid); b.appendChild(nb);
      }
    });
    pintarAnotacoesIncompletas();
    updatePanelCount();
    PERGUNTAS.forEach(function (q) { updateRow(q.id); });
  }

  /* captura congelada no instante da seleção (a Selection mente depois de transições de UI) */
  var captured = null;
  var capturedRect = null;
  var selTimer = null;
  function dentroDeCampo(node) {
    var e = node && (node.nodeType === 1 ? node : node.parentElement);
    while (e) { var t = e.tagName; if (t === "INPUT" || t === "TEXTAREA" || t === "SELECT" || e.isContentEditable) return true; e = e.parentElement; }
    return false;
  }
  function blocoDe(node) {
    var e = node && (node.nodeType === 1 ? node : node.parentElement);
    while (e) { if (e.hasAttribute && e.hasAttribute("data-anotavel")) return e; e = e.parentElement; }
    return null;
  }
  function captureSelection() {
    var sel = window.getSelection();
    /* seleção colapsada só esconde a barra; a captura congelada fica viva (no toque, a
       seleção some antes do clique — B8 do parecer técnico) */
    if (!sel || sel.rangeCount === 0 || sel.isCollapsed) { if (!popoverAberto) hideAnnotBar(); return; }
    var range = sel.getRangeAt(0);
    if (dentroDeCampo(range.startContainer)) { hideAnnotBar(); return; }
    var block = blocoDe(range.startContainer);
    if (!block) { hideAnnotBar(); return; }
    var bid = block.getAttribute("data-bloco-id");
    var truncada = blocoDe(range.endContainer) !== block;
    var pre = document.createRange();
    pre.selectNodeContents(block);
    pre.setEnd(range.startContainer, range.startOffset);
    var inicio = pre.toString().length;
    var texto;
    if (truncada) {
      var cr = range.cloneRange();
      cr.setEnd(block, block.childNodes.length);
      texto = cr.toString();
    } else texto = range.toString();
    /* o botão "anotar este bloco" vive dentro do bloco; tira o rótulo dele da conta */
    var btn = block.querySelector(".annot-block-btn");
    if (btn && texto.indexOf(btn.textContent) !== -1) texto = texto.replace(btn.textContent, "");
    if (!texto.trim()) { hideAnnotBar(); return; }
    var fim = inicio + texto.length;
    if (texto.length > 300) { texto = texto.slice(0, 300); fim = inicio + 300; }
    var p = pristine[bid] || "";
    var casa = block.closest("article.q-card") || block.closest("details.q-item");
    captured = {
      bloco_id: bid,
      item_id: casa ? casa.getAttribute("data-pergunta-id") : null,
      ancora_tipo: "trecho",
      inicio: inicio, fim: fim,
      trecho: texto,
      prefixo: p.slice(Math.max(0, inicio - 32), inicio),
      sufixo: p.slice(fim, fim + 32),
      truncada: truncada
    };
    capturedRect = range.getBoundingClientRect();
    showAnnotBar(capturedRect);
  }
  document.addEventListener("selectionchange", function () {
    if (selTimer) clearTimeout(selTimer);
    selTimer = setTimeout(captureSelection, 120);
  });
  function showAnnotBar(rect) {
    var bar = $("annot-bar");
    bar.classList.add("show");
    var top = rect.bottom + 8;
    if (top > window.innerHeight - 64) top = Math.max(8, rect.top - 52);
    bar.style.top = top + "px";
    bar.style.left = Math.max(8, Math.min(window.innerWidth - 130, rect.left + rect.width / 2 - 55)) + "px";
  }
  function hideAnnotBar() { $("annot-bar").classList.remove("show"); }

  var popoverAberto = false;
  var popCap = null;   /* captura congelada no momento de abrir o popover */
  function openPopover(cap, rect) {
    popoverAberto = true;
    popCap = cap;
    hideAnnotBar();
    var po = $("annot-popover");
    $("ap-quote").textContent = "“" + cap.trecho.slice(0, 160) + (cap.trecho.length > 160 ? "…" : "") + "”";
    $("ap-trunc").hidden = !cap.truncada;
    $("ap-textarea").value = "";
    po.classList.add("show");
    var top = (rect ? rect.bottom : window.innerHeight / 2) + 10;
    if (top > window.innerHeight - 220) top = Math.max(8, (rect ? rect.top : 200) - 210);
    po.style.top = top + "px";
    po.style.left = Math.max(8, Math.min(window.innerWidth - 356, rect ? rect.left : 40)) + "px";
    $("ap-textarea").focus();
  }
  function hidePopover() { popoverAberto = false; $("annot-popover").classList.remove("show"); }

  function salvarAnotacao() {
    var cap = popCap || captured;
    if (!cap) { hidePopover(); return; }
    interacted = true;
    var a = {
      id: novoId("an"),
      item_id: cap.item_id,
      bloco_id: cap.bloco_id,
      ancora_tipo: cap.ancora_tipo,
      ancora_status: cap.truncada ? "truncada" : "resolvida",
      ancora_truncada: !!cap.truncada,
      trecho: cap.trecho,
      prefixo: cap.prefixo,
      sufixo: cap.sufixo,
      inicio: cap.inicio,
      fim: cap.fim,
      comentario: $("ap-textarea").value,
      criado_em: new Date().toISOString()
    };
    draft.anotacoes.push(a);
    flush();
    hidePopover();
    captured = null; popCap = null;
    var sel = window.getSelection(); if (sel) sel.removeAllRanges();
    paintAll();
    updateGlobal();
    announce("Anotação salva.");
  }

  /* painel de anotações (drawer; nunca por cima do wizard) */
  var lastDeleted = null;
  function updatePanelCount() {
    var n = draft.anotacoes.length;
    $("btn-annot-panel").textContent = "Anotações (" + n + ")";
    $("ap-title").textContent = "Anotações (" + n + ")";
  }
  function rebuildPanel() {
    var body = $("ap-body");
    body.textContent = "";
    var undo = el("div"); undo.id = "ap-undo";
    if (lastDeleted) {
      undo.classList.add("show");
      undo.appendChild(el("span", null, "Anotação apagada."));
      var ub = el("button", null, "Desfazer");
      ub.type = "button";
      ub.addEventListener("click", function () { draft.anotacoes.push(lastDeleted); lastDeleted = null; flush(); paintAll(); rebuildPanel(); updateGlobal(); });
      undo.appendChild(ub);
    }
    body.appendChild(undo);
    if (!draft.anotacoes.length) {
      body.appendChild(el("p", "ap-empty", "Nenhuma anotação ainda. Selecione um trecho de texto da página e toque em “Anotar” — o bilhete fica preso ao trecho e vai junto com as respostas. Comentário muda a sua resposta; anotação é um bilhete no texto."));
      return;
    }
    var vivas = draft.anotacoes.filter(function (a) { return a.ancora_status !== "orfa"; });
    var orfas = draft.anotacoes.filter(function (a) { return a.ancora_status === "orfa"; });
    function card(a, orfa) {
      var c = el("div", "ap-card" + (orfa ? " orfa" : ""));
      if (orfa) c.appendChild(el("div", "apc-orfa-tag", "Trecho não encontrado nesta versão — anotação preservada"));
      c.appendChild(el("div", "apc-quote", "“" + (a.trecho || "(bloco inteiro)").slice(0, 140) + ((a.trecho || "").length > 140 ? "…" : "") + "”"));
      /* editor de verdade: anotação restaurada longa demais precisa poder encolher sem
         ser apagada — antes o card só exibia o texto (r3/P1) */
      var editor = el("textarea", "apc-text apc-editar");
      editor.value = a.comentario || "";
      editor.setAttribute("data-editar-anotacao", a.id);
      editor.setAttribute("maxlength", String(LIMITES_DE_TEXTO.anotacao));
      editor.setAttribute("aria-label", "Editar o bilhete desta anotação");
      editor.addEventListener("input", function () { editarAnotacao(a.id, editor.value); });
      c.appendChild(editor);
      c.appendChild(el("div", "apc-meta", (a.item_id ? a.item_id + " · " : "") + a.bloco_id + " · " + (a.criado_em || "").slice(0, 16).replace("T", " ")));
      var acts = el("div", "apc-actions");
      var ver = el("button", null, "Ver no texto"); ver.type = "button";
      if (orfa) ver.disabled = true;
      ver.addEventListener("click", function () { irParaAnotacao(a); });
      var del = el("button", "apc-del", "Apagar"); del.type = "button";
      del.addEventListener("click", function () {
        var i = draft.anotacoes.indexOf(a);
        if (i !== -1) { lastDeleted = draft.anotacoes.splice(i, 1)[0]; flush(); paintAll(); rebuildPanel(); updateGlobal(); announce("Anotação apagada. Dá para desfazer no painel."); }
      });
      acts.appendChild(ver); acts.appendChild(del);
      c.appendChild(acts);
      return c;
    }
    vivas.forEach(function (a) { body.appendChild(card(a, false)); });
    if (orfas.length) {
      body.appendChild(el("div", "ap-section-h", "Anotações cujo trecho mudou nesta versão"));
      orfas.forEach(function (a) { body.appendChild(card(a, true)); });
    }
  }
  function irParaAnotacao(a) {
    closePanel();
    var item = a.item_id ? elemPorDado('details.q-item', 'data-pergunta-id', a.item_id) : null;
    if (item && !item.open && !document.body.classList.contains("doc-mode") && WIZARD_OK) {
      openWizard(a.item_id);
    } else if (item && !item.open) item.open = true;
    requestAnimationFrame(function () {
      var b = blocoEl[a.bloco_id];
      if (!b) return;
      b.scrollIntoView({ block: "center" });
      b.querySelectorAll("mark.annot").forEach(function (m) {
        if ((m.getAttribute("data-annot-ids") || "").indexOf(a.id) !== -1) {
          m.classList.add("is-active");
          setTimeout(function () { m.classList.remove("is-active"); }, 1400);
        }
      });
    });
  }
  function openPanel() {
    if (dlg.open) closeWizard();
    rebuildPanel();
    var p = $("annot-panel");
    p.classList.add("open");
    p.setAttribute("aria-hidden", "false");
    $("ap-close").focus();
  }
  function closePanel() {
    var p = $("annot-panel");
    p.classList.remove("open");
    p.setAttribute("aria-hidden", "true");
  }

  /* ===== copiar / baixar (export = ação; feedback persistente, com pendências nomeadas) ===== */
  function feedback(msg) { $("copy-feedback").textContent = msg; }
  function resetCopyButtons(copiado) {
    document.querySelectorAll(".btn-copy").forEach(function (b) {
      b.textContent = copiado ? "Copiado — agora cole na conversa" : "Copiar as respostas";
    });
  }
  function pendMsg() {
    var p = counts().pendente;
    if (!p) return "";
    return p === 1 ? " Falta 1 resposta — o conferente vai devolvê-la." : " Faltam " + p + " respostas — o conferente vai devolvê-las.";
  }
  function showPreview(text, title) {
    var panel = $("preview-panel");
    $("preview-title").textContent = title;
    $("preview-pre").textContent = text;
    panel.classList.add("open");
    panel.scrollIntoView({ block: "start" });
  }
  function fallbackExecCopy(text) {
    var ta = document.createElement("textarea");
    ta.value = text; ta.setAttribute("readonly", "");
    ta.style.position = "fixed"; ta.style.left = "-9999px";
    document.body.appendChild(ta); ta.select();
    var ok = false;
    try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
    document.body.removeChild(ta);
    return ok;
  }
  function copiar() {
    flush();
    var text = buildJSON();
    function ok() { resetCopyButtons(true); feedback("Respostas copiadas." + pendMsg()); announce("Respostas copiadas."); }
    function fail() {
      if (fallbackExecCopy(text)) ok();
      else { feedback("Não consegui copiar automaticamente. Use a prévia aberta acima da barra."); showPreview(text, "Prévia das respostas para cópia manual"); }
    }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(ok, fail);
    else fail();
  }
  function baixar() {
    flush();
    var blob = new Blob([buildJSON()], { type: "application/json" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url; a.download = DOWNLOAD_NAME;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 500);
    feedback("Arquivo baixado: " + DOWNLOAD_NAME + "." + pendMsg());
  }

  /* ===== ver como documento + impressão ===== */
  var openSnapshot = null;
  function setDocMode(on) {
    document.body.classList.toggle("doc-mode", on);
    var b = $("btn-docmode");
    b.setAttribute("aria-pressed", on ? "true" : "false");
    b.textContent = on ? "Voltar ao modo compacto" : "Ver como documento";
    if (on && dlg.open) closeWizard();
    document.querySelectorAll("details.q-item").forEach(function (d) { d.open = on; });
    if (on) $("howto").open = true;
  }
  window.addEventListener("beforeprint", function () {
    if (dlg.open) closeWizard();
    openSnapshot = [];
    document.querySelectorAll("details").forEach(function (d) { openSnapshot.push([d, d.open]); d.open = true; });
  });
  window.addEventListener("afterprint", function () {
    if (openSnapshot) { openSnapshot.forEach(function (par) { par[0].open = par[1]; }); openSnapshot = null; }
  });

  /* ===== proteção: seleção sobre uma opção não pode trocar a resposta (B5) ===== */
  document.addEventListener("click", function (e) {
    var sel = window.getSelection();
    if (sel && !sel.isCollapsed && sel.toString().length > 0) {
      var lab = e.target.closest && e.target.closest("label.option");
      if (lab) { e.preventDefault(); e.stopPropagation(); }
    }
  }, true);

  /* ===== contextmenu: atalho condicional, jamais sequestro global ===== */
  document.addEventListener("contextmenu", function (e) {
    if (dentroDeCampo(e.target)) return;                    // Colar/Desfazer intactos
    var sel = window.getSelection();
    if (!sel || sel.isCollapsed || !captured) return;       // sem seleção válida: menu nativo
    if (!blocoDe(e.target)) return;                         // fora de bloco anotável: menu nativo
    e.preventDefault();
    showAnnotBar({ top: e.clientY, bottom: e.clientY, left: e.clientX, width: 0 });
  });

  /* ===== delegação de eventos ===== */
  document.addEventListener("click", function (e) {
    var t = e.target;
    var summary = t.closest && t.closest("summary.q-row");
    if (summary && WIZARD_OK && !document.body.classList.contains("doc-mode")) {
      e.preventDefault();
      var qid = summary.closest("details.q-item").getAttribute("data-pergunta-id");
      openWizard(qid, summary);
      return;
    }
    var stateBtn = t.closest && t.closest(".state-btn");
    if (stateBtn) {
      var card = stateBtn.closest("article.q-card");
      setEstado(card.getAttribute("data-pergunta-id"), BOTAO_ESTADO[stateBtn.getAttribute("data-botao")]);
      return;
    }
    var reset = t.closest && t.closest(".reset-answer");
    if (reset) {
      var card2 = reset.closest("article.q-card");
      setEstado(card2.getAttribute("data-pergunta-id"), "pendente");
      return;
    }
    var confBtn = t.closest && t.closest("#conf-list li button");
    if (confBtn) {
      var qid2 = confBtn.closest("li").getAttribute("data-pergunta-id");
      if (WIZARD_OK && !document.body.classList.contains("doc-mode")) openWizard(qid2);
      else { var it2 = elemPorDado('details.q-item', 'data-pergunta-id', qid2); it2.open = true; it2.scrollIntoView({ block: "start" }); }
      return;
    }
    var dot = t.closest && t.closest(".wz-dot");
    if (dot) { swapTo(dot.getAttribute("data-qid")); return; }
    var badge = t.closest && t.closest(".annot-badge");
    if (badge) { openPanel(); return; }
    var blocoBtn = t.closest && t.closest(".annot-block-btn");
    if (blocoBtn) {
      var bid = blocoBtn.getAttribute("data-bloco-btn");
      var bEl = blocoEl[bid];
      var det = bEl.closest("details.q-item");
      captured = {
        bloco_id: bid,
        item_id: det ? det.getAttribute("data-pergunta-id") : null,
        ancora_tipo: "bloco",
        inicio: 0, fim: 0,
        trecho: (pristine[bid] || "").slice(0, 300),
        prefixo: "", sufixo: "",
        truncada: false
      };
      openPopover(captured, blocoBtn.getBoundingClientRect());
      return;
    }
    if (t.closest && t.closest(".btn-copy")) { copiar(); return; }
    if (t.closest && t.closest(".btn-download")) { baixar(); return; }
  });

  $("btn-comecar").addEventListener("click", function () {
    var p = pendentes();
    if (p.length && WIZARD_OK && !document.body.classList.contains("doc-mode")) openWizard(p[0].id);
    else { $("conf-title").focus(); $("conferencia").scrollIntoView({ block: "start" }); }
  });
  $("wizard-close").addEventListener("click", closeWizard);
  $("wz-prev").addEventListener("click", function () {
    var i = IDX[current];
    if (i > 0) swapTo(PERGUNTAS[i - 1].id);
  });
  $("wz-next").addEventListener("click", function () {
    flush();
    var i = IDX[current];
    var pend = pendentes().filter(function (q) { return q.id !== current; });
    var aFrente = pend.filter(function (q) { return IDX[q.id] > i; })[0];
    if (aFrente) { swapTo(aFrente.id); return; }
    var atras = pend[0];
    if (atras) { swapTo(atras.id, "Voltando para a pergunta " + (IDX[atras.id] + 1) + ", que ficou pendente."); return; }
    closeWizard();
    $("conf-title").focus();
    $("conferencia").scrollIntoView({ block: "start" });
  });
  $("btn-annot-panel").addEventListener("click", openPanel);
  $("ap-close").addEventListener("click", closePanel);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && $("annot-panel").classList.contains("open")) closePanel();
    if (e.key === "Escape" && popoverAberto) hidePopover();
  });
  $("btn-docmode").addEventListener("click", function () {
    setDocMode(this.getAttribute("aria-pressed") !== "true");
  });
  $("dica-dismiss").addEventListener("click", function () {
    interacted = true;
    draft.ui.dica_anotacao_dispensada = true;
    $("dica-anotacao").remove();
    flush();
  });
  /* barra/popover de anotação: agir no pointerdown, antes de a seleção sumir */
  $("annot-bar-btn").addEventListener("pointerdown", function (e) {
    e.preventDefault();
    if (captured) openPopover(captured, capturedRect);
  });
  $("annot-bar-btn").addEventListener("click", function (e) { e.preventDefault(); });
  $("ap-save").addEventListener("click", salvarAnotacao);
  $("ap-cancel").addEventListener("click", function () { hidePopover(); captured = null; });
  $("preview-select").addEventListener("click", function () {
    var pre = $("preview-pre");
    var range = document.createRange();
    range.selectNodeContents(pre);
    var selObj = window.getSelection();
    selObj.removeAllRanges(); selObj.addRange(range);
  });
  $("preview-close").addEventListener("click", function () { $("preview-panel").classList.remove("open"); });

  document.addEventListener("change", function (e) {
    var input = e.target;
    if (input.matches && input.matches('.option input[type="radio"]')) {
      var card = input.closest("article.q-card");
      var qid = card.getAttribute("data-pergunta-id");
      interacted = true;
      draft.respostas[qid].escolha_id = input.value;
      updateRow(qid);
      updateGlobal();
      persist();
    }
  });
  document.addEventListener("input", function (e) {
    var ta = e.target;
    if (!ta.matches || !ta.matches("textarea")) return;
    var card = ta.closest("article.q-card");
    if (card) {
      var qid = card.getAttribute("data-pergunta-id");
      interacted = true;
      if (ta.classList.contains("duvida-texto")) draft.respostas[qid].duvida_texto = ta.value;
      if (ta.classList.contains("question-comment")) draft.respostas[qid].comentario = ta.value;
      persist();
    }
    atualizarTravas();
    autogrow(ta);
  });

  /* ===== boot ===== */
  snapshotBlocks();
  buildDots();
  restore();
  if (draft.ui.dica_anotacao_dispensada) { var dica = $("dica-anotacao"); if (dica) dica.remove(); }
  syncAll();
  paintAll();
  rebuildPanel();
  if (WIZARD_OK) document.documentElement.classList.add("js-wizard");
  BOOT_OK = true;

  } catch (erroBoot) {
    /* degradação declarada: sem wizard, a página vira o documento longo navegável (v1) */
    document.documentElement.classList.remove("js-wizard");
    try {
      document.querySelectorAll("details.q-item").forEach(function (d) { d.open = true; });
      var strip = document.createElement("div");
      strip.className = "notice-strip";
      strip.setAttribute("role", "alert");
      strip.textContent = "Algo falhou ao ligar o modo interativo (" + (erroBoot && erroBoot.message ? erroBoot.message : "erro") + "). O conteúdo completo continua legível abaixo; os botões podem não funcionar.";
      document.body.insertBefore(strip, document.body.firstChild);
    } catch (e2) {}
    throw erroBoot;
  }
})();
</script>
</body>
</html>

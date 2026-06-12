/* =====================================================================
   VECTRA-X dashboard — static client (no backend).
   Fetches precomputed data/dashboard.json + data/patients.json and renders.
   ===================================================================== */
"use strict";

const SECTIONS = [
  { key: "overview",    idx: "01", label: "Executive Overview",      crumb: "Overview",     title: "Executive Overview" },
  { key: "eda",         idx: "02", label: "Dataset & EDA",           crumb: "Data",         title: "Dataset & Exploratory Analysis" },
  { key: "models",      idx: "03", label: "Model Performance",       crumb: "Models",       title: "Model Performance" },
  { key: "explorer",    idx: "04", label: "Prediction Explorer",     crumb: "Cohort",       title: "Disease Prediction Explorer" },
  { key: "triage",      idx: "05", label: "Patient Triage",          crumb: "Triage",       title: "Patient-level Triage Card" },
  { key: "uncertainty", idx: "06", label: "Uncertainty & Conformal", crumb: "Uncertainty",  title: "Uncertainty & Conformal Prediction" },
  { key: "explain",     idx: "07", label: "Explainability",          crumb: "Explainability", title: "Explainability" },
  { key: "fairness",    idx: "08", label: "Fairness & Robustness",   crumb: "Fairness",     title: "Fairness & Robustness" },
  { key: "resource",    idx: "09", label: "Resource Simulation",     crumb: "Resource",     title: "Resource Simulation" },
  { key: "method",      idx: "10", label: "Methodology",             crumb: "Method",       title: "Methodology & Limitations" },
];

const TIER = {
  "Routine Monitoring":        { cls: "routine", col: "#46c46a" },
  "Clinical Review":           { cls: "review",  col: "#e0b341" },
  "Confirmatory Test Priority":{ cls: "confirm", col: "#f08a3e" },
  "Urgent Response Priority":  { cls: "urgent",  col: "#f25c54" },
};
const TEALS = ["#2dd4bf", "#5eead4", "#0ea5a0", "#7defd9", "#0c6b63", "#34d399"];
const FIG = "figures/";

let D = {}, P = [], ACTIVE = [];
const initialized = new Set();

/* ---------------- tiny helpers ---------------- */
const $ = (s, r = document) => r.querySelector(s);
const fmt = (v, d = 3) => (typeof v === "number" ? v.toFixed(d) : (v ?? "—"));
const pct = (v) => (typeof v === "number" ? (v <= 1 ? (v * 100).toFixed(1) : v.toFixed(1)) + "%" : "—");
const titleCase = (s) => String(s).replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

function card(title, inner, extra = "") {
  return `<div class="card ${extra}">${title ? `<h3>${title}</h3>` : ""}${inner}</div>`;
}
function kpi(eyebrow, val, desc = "") {
  return `<div class="card kpi"><div class="eyebrow">${eyebrow}</div>
    <div class="val">${val}</div><div class="desc">${desc}</div></div>`;
}
function fig(name, caption) {
  return `<figure><img loading="lazy" src="${FIG}${name}" alt="${caption}"
    onerror="this.parentNode.innerHTML='<div class=note>figure not found: ${name}</div>'/>
    <figcaption>${caption}</figcaption></figure>`;
}
function tierBadge(t) {
  const m = TIER[t] || { cls: "review" };
  return `<span class="tier ${m.cls}"><span class="dot"></span>${t}</span>`;
}

/** rows: array of objects; cols: [{k,label,num,fmt,bar,max}] */
function table(rows, cols, { maxRows } = {}) {
  if (!rows || !rows.length) return `<div class="note">no data</div>`;
  const data = maxRows ? rows.slice(0, maxRows) : rows;
  const head = cols.map((c) => `<th class="${c.num ? "num" : ""}">${c.label}</th>`).join("");
  const body = data.map((r) => {
    const tds = cols.map((c) => {
      let v = r[c.k];
      if (c.fmt) v = c.fmt(v, r);
      else if (c.num && typeof v === "number") v = fmt(v, c.d ?? 3);
      if (c.bar && typeof r[c.k] === "number") {
        const w = Math.max(0, Math.min(100, (r[c.k] / (c.max || 1)) * 100));
        return `<td class="num bar-cell"><span class="fill" style="width:${w}%"></span><span>${v}</span></td>`;
      }
      return `<td class="${c.num ? "num" : ""}">${v ?? "—"}</td>`;
    }).join("");
    return `<tr>${tds}</tr>`;
  }).join("");
  return `<div class="tbl-wrap"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
}

/* ---------------- chart factory ---------------- */
function chartBase() {
  Chart.defaults.color = "#8ba2ab";
  Chart.defaults.font.family = "'IBM Plex Mono', monospace";
  Chart.defaults.font.size = 11;
  Chart.defaults.borderColor = "rgba(94,234,212,0.10)";
}
function gridOpt() {
  return { grid: { color: "rgba(94,234,212,0.08)" }, ticks: { color: "#8ba2ab" } };
}
function bar(id, labels, data, { horizontal, colors, label, max } = {}) {
  const ctx = $(id); if (!ctx) return;
  new Chart(ctx, {
    type: "bar",
    data: { labels, datasets: [{ label: label || "", data,
      backgroundColor: colors || "rgba(45,212,191,0.55)",
      borderColor: colors || "#2dd4bf", borderWidth: 1, borderRadius: 4, maxBarThickness: 34 }] },
    options: {
      indexAxis: horizontal ? "y" : "x", responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { x: { ...gridOpt(), max: horizontal ? max : undefined, beginAtZero: true },
                y: { ...gridOpt(), max: horizontal ? undefined : max, beginAtZero: true } },
    },
  });
}
function groupBar(id, labels, datasets) {
  const ctx = $(id); if (!ctx) return;
  new Chart(ctx, {
    type: "bar",
    data: { labels, datasets: datasets.map((d, i) => ({
      label: d.label, data: d.data, backgroundColor: d.color, borderColor: d.color,
      borderWidth: 1, borderRadius: 4, maxBarThickness: 22 })) },
    options: { responsive: true, maintainAspectRatio: false,
      plugins: { legend: { labels: { boxWidth: 12, color: "#dbe8ec" } } },
      scales: { x: gridOpt(), y: { ...gridOpt(), beginAtZero: true, max: 1 } } },
  });
}
function donut(id, labels, data, colors) {
  const ctx = $(id); if (!ctx) return;
  new Chart(ctx, {
    type: "doughnut",
    data: { labels, datasets: [{ data, backgroundColor: colors, borderColor: "#0e161b", borderWidth: 2 }] },
    options: { responsive: true, maintainAspectRatio: false, cutout: "62%",
      plugins: { legend: { position: "right", labels: { boxWidth: 12, color: "#dbe8ec", padding: 12 } } } },
  });
}

/* =====================================================================
   Section renderers
   ===================================================================== */
function renderOverview() {
  const s = D.summary, tm = s.test_metrics.PRE_LAB, cf = s.conformal, co = s.coinfection;
  const kpis = [
    kpi("Cohort", `${s.shape[0]}<small> × ${s.shape[1]}</small>`, "patients × variables · 2 health centers"),
    kpi("Active labels", s.active_labels.length, `${s.inactive_labels.length} inactive (0 positives)`),
    kpi("Multi-label", `${s.n_multilabel_patients}<small>/300</small>`, "patients carry >1 diagnosis"),
    kpi("Pre-lab model", `<span style="font-size:22px">${titleCase(s.best_model_per_track.PRE_LAB)}</span>`, "selected by OOF macro-PR-AUC"),
    kpi("Macro-F1", fmt(tm.macro_f1, 3), "pre-lab · held-out test"),
    kpi("Macro-recall", fmt(tm.macro_recall, 3), "averaged across labels"),
    kpi("Conformal coverage", pct(cf.overall_coverage), `avg set size ${fmt(cf.avg_set_size, 2)}`),
    kpi("Co-infection AUC", fmt(co.roc_auc, 2), `recall ${fmt(co.recall, 2)}`),
  ].join("");

  const thesis = card("The thesis", `<ul class="bullets">
    <li><b>Multi-label, not multi-class</b> — over half of patients carry more than one diagnosis.</li>
    <li><b>Leakage-aware staging</b> — separate <em>pre-lab triage</em> from <em>lab-aware confirmation</em>.</li>
    <li><b>Uncertainty-aware</b> — calibrated probabilities + conformal prediction sets that can abstain.</li>
    <li><b>Actionable</b> — four triage tiers, resource simulation, and a fairness audit.</li></ul>`);

  $("#view-overview").innerHTML = `
    <p class="lede">A multi-label, explainable, uncertainty-aware <em>clinical triage intelligence
    system</em> for vector-borne disease response. <em>Prediction is not enough</em> — the model knows
    when it is uncertain, explains why, and helps prioritise action.</p>
    <div class="grid cols-4">${kpis}</div>
    <div class="spacer"></div>
    <div class="grid cols-2">
      ${thesis}
      ${card("Triage tier distribution", `<div class="canvas-box"><canvas id="c-tiers"></canvas></div>`)}
    </div>
    <div class="spacer"></div>
    ${card("Disease prevalence", `<div class="canvas-box"><canvas id="c-prev"></canvas></div>`)}`;

  initialized.add("overview"); chartBase();
  const td = D.summary.triage_distribution;
  const torder = Object.keys(TIER).filter((t) => t in td);
  donut("#c-tiers", torder, torder.map((t) => td[t]), torder.map((t) => TIER[t].col));
  const ld = D.label_distribution.filter((r) => r.status === "active");
  bar("#c-prev", ld.map((r) => titleCase(r.label)), ld.map((r) => r.prevalence_pct),
    { horizontal: true, colors: TEALS, max: 100 });
}

function renderEda() {
  $("#view-eda").innerHTML = `
    <p class="lede">Malaria dominates (90% prevalence) so macro-F1 and per-label recall — not accuracy —
    are primary. Co-diagnosis is central: more than half of patients are multi-label.</p>
    <div class="grid cols-2">
      ${card("Active vs inactive labels", table(D.label_distribution, [
        { k: "label", label: "Disease", fmt: (v) => titleCase(v) },
        { k: "positives", label: "Positives", num: true, d: 0 },
        { k: "prevalence_pct", label: "Prevalence", num: true, fmt: (v) => v + "%" },
        { k: "status", label: "Status", fmt: (v) => `<span class="pill ${v === "active" ? "teal" : ""}">${v}</span>` },
      ]))}
      ${card("Top diagnosis combinations", table(D.top_combinations, [
        { k: "combination", label: "Combination", fmt: (v) => v.replace(/_/g, " ").replace(/\+/g, " + ") },
        { k: "n_patients", label: "Patients", num: true, d: 0, bar: true, max: 120 },
      ], { maxRows: 10 }))}
    </div>
    <div class="section-head">Visual audit</div>
    <div class="grid cols-2">
      ${card("", fig("label_cooccurrence_heatmap.png", "Label co-occurrence"))}
      ${card("", fig("coinfection_profile.png", "Co-infection profile"))}
      ${card("", fig("missingness_by_disease.png", "Missingness by disease"))}
      ${card("", fig("missingness_top_features.png", "Top missingness"))}
      ${card("", fig("demographics.png", "Demographics"))}
      ${card("", fig("feature_projection_pca.png", "PCA projection"))}
      ${card("", fig("association_matrix.png", "Feature association matrix"))}
      ${card("", fig("data_type_summary.png", "Column roles"))}
    </div>`;
}

function renderModels() {
  const lb = [...D.leaderboard].sort((a, b) => b.macro_pr_auc - a.macro_pr_auc);
  const trackCol = { PRE_LAB: "#2dd4bf", LAB_AWARE: "#5ec8ea", FULL: "#ff7a59" };
  const tms = D.summary.test_metrics;
  const tmRows = Object.entries(tms).map(([k, m]) => ({ track: k, ...m }));

  $("#view-models").innerHTML = `
    <p class="lede">Three stage-gated tracks benchmarked across six model families with multi-label
    stratified CV. The large <em>FULL</em> gain is a <b>leakage artefact</b> — the pre-lab model is
    the realistic deployable system.</p>
    <div class="grid cols-2">
      ${card("Leaderboard · macro-F1 (5-fold OOF)", `<div class="canvas-box tall"><canvas id="c-lb"></canvas></div>`)}
      ${card("Pre-lab per-label · F1 vs recall (test)", `<div class="canvas-box tall"><canvas id="c-pl"></canvas></div>`)}
    </div>
    <div class="section-head">Held-out test metrics by track</div>
    ${card("", table(tmRows, [
      { k: "track", label: "Track", fmt: (v) => `<span class="pill teal">${v}</span>` },
      { k: "macro_f1", label: "macro-F1", num: true }, { k: "micro_f1", label: "micro-F1", num: true },
      { k: "macro_pr_auc", label: "macro-PR-AUC", num: true }, { k: "macro_recall", label: "macro-recall", num: true },
      { k: "hamming_loss", label: "Hamming", num: true }, { k: "subset_accuracy", label: "Subset acc", num: true },
    ]))}
    <div class="note warn">FULL includes <b>Dengue (Dengua)</b> (AUC≈0.96, restates the dengue outcome):
    dengue F1 jumps 0.57 → 0.92. This is why a naive model looks excellent yet is clinically worthless.</div>
    <div class="section-head">Per-label metrics — pre-lab (held-out test)</div>
    ${card("", table(D.per_label.filter((r) => r.track === "PRE_LAB"), [
      { k: "label", label: "Disease", fmt: (v) => titleCase(v) },
      { k: "support_pos", label: "Support", num: true, d: 0 },
      { k: "precision", label: "Precision", num: true }, { k: "recall", label: "Recall", num: true },
      { k: "f1", label: "F1", num: true }, { k: "roc_auc", label: "ROC-AUC", num: true },
      { k: "pr_auc", label: "PR-AUC", num: true }, { k: "false_negative_rate", label: "FNR", num: true },
    ]))}
    <div class="section-head">Curves</div>
    <div class="grid cols-2">
      ${card("", fig("model_leaderboard.png", "Leaderboard (macro-F1)"))}
      ${card("", fig("confusion_matrices.png", "Per-label confusion"))}
      ${card("", fig("roc_curves.png", "ROC curves"))}
      ${card("", fig("pr_curves.png", "Precision-recall curves"))}
    </div>`;

  initialized.add("models"); chartBase();
  bar("#c-lb", lb.map((r) => r.model_track), lb.map((r) => r.macro_f1),
    { horizontal: true, max: 1, colors: lb.map((r) => trackCol[r.track] || "#2dd4bf") });
  const pl = D.per_label.filter((r) => r.track === "PRE_LAB");
  groupBar("#c-pl", pl.map((r) => titleCase(r.label)), [
    { label: "F1", data: pl.map((r) => r.f1), color: "#2dd4bf" },
    { label: "Recall", data: pl.map((r) => r.recall), color: "#ff7a59" },
  ]);
}

function cohortMeanProb() {
  const out = {};
  ACTIVE.forEach((l) => {
    const k = "calprob_" + l;
    const vals = P.map((p) => p[k]).filter((v) => typeof v === "number");
    out[l] = vals.reduce((a, b) => a + b, 0) / (vals.length || 1);
  });
  return out;
}

function renderExplorer() {
  const opts = ACTIVE.map((l) => `<option value="${l}">${titleCase(l)}</option>`).join("");
  $("#view-explorer").innerHTML = `
    <p class="lede">Cohort-wide honest predictions: every patient is scored by a model that did not train
    on them (out-of-fold). Filter the cohort by a predicted disease.</p>
    <div class="grid cols-2">
      ${card("Cohort mean calibrated probability", `<div class="canvas-box"><canvas id="c-cohort"></canvas></div>`)}
      ${card("Filter by predicted disease", `
        <label class="fld">Disease</label>
        <select id="sel-disease">${opts}</select>
        <div id="explorer-count" style="margin-top:14px"></div>`)}
    </div>
    <div class="spacer"></div>
    <div id="explorer-table"></div>`;

  initialized.add("explorer"); chartBase();
  const cm = cohortMeanProb();
  bar("#c-cohort", ACTIVE.map(titleCase), ACTIVE.map((l) => cm[l]),
    { horizontal: true, colors: TEALS, max: 1 });

  const sel = $("#sel-disease");
  const update = () => {
    const d = sel.value;
    const rows = P.filter((p) => (p.predicted_labels || "").includes(d));
    $("#explorer-count").innerHTML =
      `<div class="kpi" style="padding:0"><div class="eyebrow">Patients predicted ${titleCase(d)}</div>
       <div class="val">${rows.length}<small> / ${P.length}</small></div></div>`;
    $("#explorer-table").innerHTML = card(`Patients · ${titleCase(d)}`, table(rows, [
      { k: "uuid", label: "UUID", fmt: (v) => `<span class="pill">${String(v).slice(0, 8)}</span>` },
      { k: "predicted_labels", label: "Predicted", fmt: (v) => v.replace(/[{}]/g, "") },
      { k: "conformal_set", label: "Conformal set", fmt: (v) => v.replace(/[{}]/g, "") },
      { k: "triage_category", label: "Triage", fmt: (v) => tierBadge(v) },
    ], { maxRows: 40 }));
  };
  sel.addEventListener("change", update); update();
}

function renderTriage() {
  const opts = P.map((p) => `<option value="${p.uuid}">${String(p.uuid).slice(0, 13)}…</option>`).join("");
  $("#view-triage").innerHTML = `
    <p class="lede">Per-patient triage card: predicted diseases, calibrated probabilities, conformal set,
    uncertainty, and a four-tier priority with a decision-support action.</p>
    <label class="fld">Select patient (UUID)</label>
    <select id="sel-patient" style="max-width:420px">${opts}</select>
    <div class="spacer"></div>
    <div id="triage-card"></div>`;
  initialized.add("triage"); chartBase();
  const sel = $("#sel-patient");
  sel.addEventListener("change", () => drawTriageCard(sel.value));
  drawTriageCard(sel.value);
}

let triageChart = null;
function drawTriageCard(uuid) {
  const p = P.find((x) => String(x.uuid) === String(uuid)); if (!p) return;
  const cal = ACTIVE.map((l) => p["calprob_" + l]);
  $("#triage-card").innerHTML = `
    <div class="grid cols-3">
      ${card("Triage priority", `<div style="font-size:15px;margin-bottom:12px">${tierBadge(p.triage_category)}</div>
        <div class="kpi" style="padding:0;box-shadow:none"><div class="eyebrow">Triage score</div>
        <div class="val">${fmt(p.triage_score, 3)}</div></div>`)}
      ${card("Uncertainty", `<div class="kpi" style="padding:0;box-shadow:none">
        <div class="eyebrow">Level</div><div class="val" style="text-transform:capitalize">${p.uncertainty_level}</div>
        <div class="desc">co-infection P = ${fmt(p.coinfection_prob, 2)} · max prob ${fmt(p.max_prob, 2)}</div></div>`)}
      ${card("Recommended action", `<p style="font-size:14px;color:var(--text)">${p.recommended_action}</p>`)}
    </div>
    <div class="spacer"></div>
    <div class="grid cols-2">
      ${card("Calibrated disease probabilities", `<div class="canvas-box"><canvas id="c-patient"></canvas></div>`)}
      ${card("Label sets", `
        <p style="margin-bottom:10px"><span class="pill teal">predicted</span> ${(p.predicted_labels||"").replace(/[{}]/g,"") || "—"}</p>
        <p style="margin-bottom:10px"><span class="pill">conformal set</span> ${(p.conformal_set||"").replace(/[{}]/g,"") || "—"}</p>
        <p style="margin-bottom:10px"><span class="pill">true labels</span> ${(p.true_labels||"").replace(/[{}]/g,"") || "—"}</p>
        <div class="note">A conformal set with ≥2 labels signals ambiguity → confirmatory testing recommended.</div>`)}
    </div>`;
  chartBase();
  if (triageChart) triageChart.destroy();
  const ctx = $("#c-patient");
  triageChart = new Chart(ctx, {
    type: "bar",
    data: { labels: ACTIVE.map(titleCase), datasets: [{ data: cal,
      backgroundColor: cal.map((v) => v >= 0.5 ? "#f08a3e" : "rgba(45,212,191,0.55)"),
      borderColor: cal.map((v) => v >= 0.5 ? "#f08a3e" : "#2dd4bf"), borderWidth: 1, borderRadius: 4 }] },
    options: { indexAxis: "y", responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { x: { ...gridOpt(), max: 1, beginAtZero: true }, y: gridOpt() } },
  });
}

function renderUncertainty() {
  const cf = D.summary.conformal, uc = D.summary.uncertainty_counts;
  const order = ["low", "moderate", "high"];
  $("#view-uncertainty").innerHTML = `
    <p class="lede">Split-conformal prediction sets give recall-oriented coverage: the model returns a
    <em>set</em> of plausible diseases (and can abstain) instead of forcing one label.</p>
    <div class="grid cols-4">
      ${kpi("Target coverage", "90%", `alpha = ${cf ? 0.1 : "—"}`)}
      ${kpi("Empirical coverage", pct(cf.overall_coverage), "held-out test")}
      ${kpi("Avg set size", fmt(cf.avg_set_size, 2), `of ${ACTIVE.length} labels`)}
      ${kpi("Ambiguous (≥2)", pct(cf.pct_ambiguous_multi), "flag for confirmatory test")}
    </div>
    <div class="spacer"></div>
    <div class="grid cols-2">
      ${card("Patient uncertainty levels", `<div class="canvas-box"><canvas id="c-unc"></canvas></div>`)}
      ${card("", fig("uncertainty_distribution.png", "Uncertainty distribution"))}
    </div>
    <div class="section-head">Per-label conformal coverage (test)</div>
    ${card("", table(D.conformal_per_label, [
      { k: "label", label: "Disease", fmt: (v) => titleCase(v) },
      { k: "prob_threshold", label: "Incl. threshold", num: true },
      { k: "test_positives", label: "Test pos", num: true, d: 0 },
      { k: "covered_positives", label: "Covered", num: true, d: 0 },
      { k: "empirical_coverage", label: "Coverage", num: true, fmt: (v) => v == null ? "—" : pct(v) },
      { k: "predicted_inclusions", label: "Inclusions", num: true, d: 0 },
    ]))}
    <div class="section-head">Example prediction sets</div>
    ${card("", table(D.conformal_examples, [
      { k: "uuid", label: "UUID", fmt: (v) => `<span class="pill">${String(v).slice(0, 8)}</span>` },
      { k: "prediction_set", label: "Prediction set" },
      { k: "set_size", label: "Size", num: true, d: 0 },
      { k: "true_labels", label: "True" },
      { k: "interpretation", label: "Interpretation", fmt: (v) => `<span style="color:var(--text-muted)">${v}</span>` },
    ], { maxRows: 14 }))}`;

  initialized.add("uncertainty"); chartBase();
  donut("#c-unc", order.map(titleCase), order.map((k) => uc[k] || 0),
    ["#46c46a", "#e0b341", "#f25c54"]);
}

function renderExplain() {
  $("#view-explain").innerHTML = `
    <p class="lede">Global + per-label permutation importance with transparent local attributions.
    Features are <b>anonymised model signals, not medical causes</b> — no causal medical claims are made.</p>
    <div class="grid cols-2">
      ${card("Global feature importance (top)", `<div class="canvas-box tall"><canvas id="c-imp"></canvas></div>`)}
      ${card("", fig("feature_importance_per_label.png", "Per-label importance"))}
    </div>
    <div class="spacer"></div>
    <div class="grid cols-2">
      ${card("", fig("local_explanation_examples.png", "Local case studies"))}
      ${card("", fig("shap_summary.png", "SHAP summary (malaria)"))}
    </div>`;
  initialized.add("explain"); chartBase();
  const gi = (D.importance_global || []).slice(0, 12).reverse();
  bar("#c-imp", gi.map((r) => (r.feature || "").slice(0, 26)), gi.map((r) => r.importance_mean),
    { horizontal: true, colors: "#2dd4bf" });
}

function renderFairness() {
  const loco = D.loco || [];
  $("#view-fairness").innerHTML = `
    <p class="lede">Subgroup recall / false-negative audit across health center, gender and age — plus a
    leave-one-center-out stress test. The goal: no systematic under-detection for any subgroup.</p>
    <div class="grid cols-2">
      ${card("", fig("fairness_recall_gap.png", "Recall gap across subgroups"))}
      ${card("Leave-one-center-out", loco.length ? table(loco, [
        { k: "test_on", label: "Test center" }, { k: "n_test", label: "n", num: true, d: 0 },
        { k: "macro_f1", label: "macro-F1", num: true }, { k: "micro_f1", label: "micro-F1", num: true },
      ]) + `<div class="note warn">Macro-F1 drops when transferring across centers — real workflow shift.
        Recommend per-facility recalibration.</div>` : `<div class="note">no center data</div>`)}
    </div>
    <div class="section-head">Subgroup metrics</div>
    ${card("", table(D.fairness, fairnessCols()))}`;
}
function fairnessCols() {
  const base = [{ k: "axis", label: "Axis", fmt: (v) => `<span class="pill teal">${v}</span>` },
    { k: "level", label: "Level" }, { k: "n", label: "n", num: true, d: 0 },
    { k: "macro_f1", label: "macro-F1", num: true }];
  ACTIVE.forEach((l) => base.push({ k: "recall_" + l, label: titleCase(l).slice(0, 8), num: true,
    fmt: (v) => v == null ? "—" : fmt(v, 2) }));
  return base;
}

function renderResource() {
  const res = D.resource || [];
  const tiers = res.filter((r) => r.metric.startsWith("tier_"))
    .map((r) => ({ name: titleCase(r.metric.replace("tier_", "")), count: r.count }));
  $("#view-resource").innerHTML = `
    <p class="lede">Translating predictions into operational load: how many patients need confirmatory
    testing, urgent review, or routine monitoring — and how threshold policies change that burden.</p>
    <div class="grid cols-2">
      ${card("Triage tier distribution", `<div class="canvas-box"><canvas id="c-res"></canvas></div>`)}
      ${card("Resource summary", table(res.filter((r) => !r.metric.startsWith("tier_")), [
        { k: "metric", label: "Metric", fmt: (v) => titleCase(v) },
        { k: "count", label: "Count", num: true, d: 0, bar: true, max: 300 },
        { k: "pct", label: "%", num: true, fmt: (v) => v + "%" },
      ]))}
    </div>
    <div class="spacer"></div>
    <div class="grid cols-2">
      ${card("", fig("resource_priority_distribution.png", "Priority distribution"))}
      ${card("", fig("threshold_policy_resource_tradeoff.png", "Threshold-policy trade-off"))}
    </div>`;
  initialized.add("resource"); chartBase();
  const tierNames = Object.keys(TIER);
  const ordered = tierNames.map((t) => tiers.find((x) => x.name === t) || { name: t, count: 0 });
  bar("#c-res", ordered.map((t) => t.name.split(" ")[0]), ordered.map((t) => t.count),
    { colors: tierNames.map((t) => TIER[t].col) });
}

function renderMethod() {
  $("#view-method").innerHTML = `
    <p class="lede">A stage-aware, leakage-honest methodology. Every feature is screened by name pattern
    <em>and</em> statistics, then routed to a clinical stage.</p>
    <div class="grid cols-3">
      ${kpi("PRE_LAB", D.summary.feature_set_sizes.PRE_LAB_TRIAGE, "demographics · symptoms · vitals")}
      ${kpi("LAB_AWARE", D.summary.feature_set_sizes.LAB_AWARE_CONFIRMATION, "+ ordered lab / rapid tests")}
      ${kpi("FULL", D.summary.feature_set_sizes.FULL_RESEARCH_ONLY, "+ target restatement · research only")}
    </div>
    <div class="section-head">Confirmed leakage / lab-confirmation features</div>
    ${card("", table(D.leakage, [
      { k: "feature", label: "Feature", fmt: (v) => (v || "").slice(0, 42) },
      { k: "decision", label: "Decision", fmt: (v) => `<span class="pill ${v === "research_only" ? "" : "teal"}">${v}</span>` },
      { k: "best_label", label: "Best label", fmt: (v) => titleCase(v) },
      { k: "max_single_feature_auc", label: "Single-feat AUC", num: true },
      { k: "mutual_info", label: "MI", num: true },
    ], { maxRows: 14 }))}
    <div class="section-head">Threshold policies</div>
    ${card("", table(D.threshold_policies, [
      { k: "label", label: "Disease", fmt: (v) => titleCase(v) },
      { k: "performance", label: "Performance", num: true }, { k: "safety", label: "Safety", num: true },
      { k: "operational", label: "Operational", num: true },
    ]))}
    <div class="section-head">Limitations & ethics</div>
    ${card("", `<ul class="bullets">
      <li><b>Small sample (n=300)</b> and severe imbalance — rare-label metrics are estimates.</li>
      <li><b>Three labels have zero positives</b> (chikungunya, zika, option 8) — excluded from scoring.</li>
      <li><b>Center shift</b> — leave-one-center-out macro-F1 ≈ ${(D.summary.loco_macro_f1 || []).map((v) => fmt(v, 2)).join(" / ") || "—"}.</li>
      <li><b>No timestamp/location</b> — external data is supplementary only, never patient-level training.</li>
      <li><b>Decision support, not diagnosis</b> — human-in-the-loop for all Orange/Red tiers and abstentions.</li>
    </ul>`)}`;
}

const RENDER = { overview: renderOverview, eda: renderEda, models: renderModels, explorer: renderExplorer,
  triage: renderTriage, uncertainty: renderUncertainty, explain: renderExplain, fairness: renderFairness,
  resource: renderResource, method: renderMethod };

/* =====================================================================
   Navigation + boot
   ===================================================================== */
function buildNav() {
  const nav = $("#nav");
  SECTIONS.forEach((s) => {
    const a = document.createElement("a");
    a.href = "#" + s.key; a.dataset.key = s.key;
    a.innerHTML = `<span class="idx">${s.idx}</span>${s.label}`;
    a.addEventListener("click", (e) => { e.preventDefault(); show(s.key); });
    nav.appendChild(a);
  });
}
function show(key) {
  const s = SECTIONS.find((x) => x.key === key) || SECTIONS[0];
  document.querySelectorAll(".view").forEach((v) => v.classList.toggle("active", v.id === "view-" + s.key));
  document.querySelectorAll("#nav a").forEach((a) => a.classList.toggle("active", a.dataset.key === s.key));
  $("#crumb").textContent = s.crumb; $("#title").textContent = s.title;
  if (!initialized.has(s.key)) { try { RENDER[s.key](); } catch (e) { console.error(e); } }
  history.replaceState(null, "", "#" + s.key);
  window.scrollTo(0, 0);
}

async function boot() {
  try {
    const [d, p] = await Promise.all([
      fetch("data/dashboard.json").then((r) => r.json()),
      fetch("data/patients.json").then((r) => r.json()),
    ]);
    D = d; P = p; ACTIVE = D.summary.active_labels;
    $("#chip").innerHTML = `Pre-lab model · <b>${titleCase(D.summary.best_model_per_track.PRE_LAB)}</b>`;
    buildNav();
    $("#loader").remove();
    $(".app").hidden = false;
    // Sections render lazily on first show() so Chart.js canvases have real
    // dimensions (a canvas created while display:none would size to 0).
    const start = (location.hash || "#overview").slice(1);
    show(SECTIONS.some((s) => s.key === start) ? start : "overview");
  } catch (e) {
    console.error(e);
    $("#loader").innerHTML = `<div id="err">Could not load data. Run <b>python run_pipeline.py</b> then
      <b>python export_web_data.py</b>, and open via the launcher (a local server) — browsers block
      <code>fetch()</code> over file://.</div>`;
  }
}
boot();

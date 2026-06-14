import { loadBundle } from "./data-client.js";
import { normalizeRoute, routeHref } from "./router.js";
import { dataBars, figure, metric, probabilityBars, table } from "./components.js";
import { listLabels, number, percent, titleCase } from "./formatters.js";
import { simulateResources } from "./resource-simulator.js";

const groups = [
  { label: "Overview", routes: [{ key: "overview", label: "Executive overview" }] },
  { label: "Model evidence", routes: [
    { key: "data", label: "Dataset & EDA" },
    { key: "models", label: "Model performance" },
    { key: "uncertainty", label: "Uncertainty" },
    { key: "explainability", label: "Explainability" },
  ] },
  { label: "Decision support", routes: [
    { key: "cases", label: "Case explorer" },
    { key: "triage", label: "Patient triage" },
    { key: "resources", label: "Resource simulator" },
  ] },
  { label: "Trust & governance", routes: [
    { key: "trust", label: "Fairness & robustness" },
    { key: "methodology", label: "Methodology & limitations" },
  ] },
];

const routes = groups.flatMap((group) => group.routes.map((route) => ({ ...route, group: group.label })));

const ICON_PATHS = {
  overview: '<rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/>',
  data: '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/><path d="M3 12a9 3 0 0 0 18 0"/>',
  models: '<path d="M3 3v18h18"/><path d="M8 17v-5"/><path d="M13 17V8"/><path d="M18 17v-3"/>',
  uncertainty: '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="2.5"/><path d="M12 2v3"/><path d="M12 19v3"/><path d="M2 12h3"/><path d="M19 12h3"/>',
  explainability: '<path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.3 1 2.1v.2h6v-.2c0-.8.4-1.6 1-2.1A7 7 0 0 0 12 2Z"/>',
  cases: '<path d="M8 6h13"/><path d="M8 12h13"/><path d="M8 18h13"/><path d="M3.5 6h.01"/><path d="M3.5 12h.01"/><path d="M3.5 18h.01"/>',
  triage: '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V3a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v1"/><path d="M9 11h6"/><path d="M9 15h4"/>',
  resources: '<path d="M4 21v-7"/><path d="M4 10V3"/><path d="M12 21v-9"/><path d="M12 8V3"/><path d="M20 21v-5"/><path d="M20 12V3"/><path d="M2 14h4"/><path d="M10 8h4"/><path d="M18 16h4"/>',
  trust: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/>',
  methodology: '<path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3Z"/>',
};

const navIcon = (key) =>
  `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICON_PATHS[key] || ""}</svg>`;

let bundle;
let currentRoute = "overview";
let selectedCaseId;

const view = () => document.querySelector("#dashboard-view");

function renderNav() {
  document.querySelector("#dashboard-nav").innerHTML = groups.map((group) =>
    `<section class="nav-group"><h2>${group.label}</h2>${group.routes.map((route) => `<a href="${routeHref(route.key)}" data-route="${route.key}">${navIcon(route.key)}<span>${route.label}</span></a>`).join("")}</section>`,
  ).join("");
  document.querySelectorAll("[data-route]").forEach((link) => link.addEventListener("click", (event) => {
    event.preventDefault();
    navigate(link.dataset.route);
    closeMenu();
  }));
}

function overview() {
  const summary = bundle.dashboard.summary;
  const metrics = summary.test_metrics.PRE_LAB;
  return `<div class="insight-hero"><span>WHAT THE SYSTEM CAN DO</span><h2>Prioritize multi-label disease risk before lab confirmation, while showing when evidence is too uncertain to act alone.</h2><p>The deployable story is PRE_LAB. Lab-aware results provide workflow comparison; FULL demonstrates why leakage control matters.</p></div>
  <div class="metrics">${metric("Macro-F1", metrics.macro_f1.toFixed(2), "held-out test · 5 labels")}${metric("Macro-recall", metrics.macro_recall.toFixed(2), "held-out test · sensitivity")}${metric("Conformal coverage", percent(summary.conformal.overall_coverage), "target 90% · rare-label caveat")}</div>
  <div class="inline-stats"><span><strong>${summary.n_multilabel_patients}/${summary.shape[0]}</strong> multi-label cases</span><span><strong>${summary.coinfection.roc_auc.toFixed(2)}</strong> co-infection ROC-AUC</span><span><strong>${summary.loco_macro_f1.map((value) => value.toFixed(2)).join(" / ")}</strong> LOCO macro-F1</span></div>
  <aside class="callout callout-risk"><strong>Safety boundary:</strong> Yellow fever has only 3 positives in the held-out split, and center-transfer macro-F1 falls near 0.38. These are decision-support estimates, not clinical validation.</aside>
  <div class="workflow"><div><b>01</b><strong>Signal</strong><span>Pre-lab features</span></div><div><b>02</b><strong>Prediction</strong><span>Multi-label probabilities</span></div><div><b>03</b><strong>Uncertainty</strong><span>Conformal set</span></div><div><b>04</b><strong>Action</strong><span>Triage and capacity</span></div></div>
  <div class="grid grid-3"><a class="panel panel-border text-link" href="demo.html">Start guided demo</a><a class="panel panel-border text-link" href="#models">Inspect model evidence</a><a class="panel panel-border text-link" href="#methodology">Read limitations</a></div>`;
}

function dataView() {
  const labels = bundle.dashboard.label_distribution;
  return `<p class="view-lede">The cohort is small, imbalanced, multi-label, and split across two centers. Those properties determine which metrics are credible and where human oversight is essential.</p>
  <div class="grid grid-3"><article class="panel"><h2>300 patients</h2><p>109 source variables, 82 retained in the deployable pre-lab track.</p></article><article class="panel"><h2>158 multi-label</h2><p>More than half the cohort carries multiple recorded diagnoses.</p></article><article class="panel"><h2>2 health centers</h2><p>Enough to expose transfer risk, not enough to establish broad generalization.</p></article></div>
  <h2 class="section-heading">Label prevalence</h2><div class="panel">${dataBars(labels.filter((row) => row.status === "active"), "prevalence_pct", "label", { max: 100 })}</div>
  <aside class="callout callout-warn"><strong>Modeling implication:</strong> Malaria prevalence is 90%, while yellow fever is 4%. Accuracy and micro metrics alone would hide rare-label failure.</aside>
  <div class="grid grid-2">${figure("label_cooccurrence_heatmap.png", "Heatmap showing disease label co-occurrence", "Malaria frequently co-occurs with other recorded labels.")}${figure("missingness_by_disease.png", "Missingness patterns by disease", "Missingness is retained as workflow availability information, not treated as a negative.")}</div>`;
}

function modelView() {
  const mode = document.querySelector("#model-mode").value;
  const summary = bundle.dashboard.summary;
  const metrics = summary.test_metrics[mode];
  const rows = bundle.dashboard.per_label.filter((row) => row.track === mode).sort((a, b) => a.recall - b.recall);
  const warning = mode === "FULL" ? `<aside class="callout callout-risk"><strong>Research-only leakage comparison.</strong> FULL includes post-diagnosis or target-restating information and must not be presented as deployable.</aside>` : "";
  return `${warning}<p class="view-lede">${mode === "PRE_LAB" ? "Default deployable evidence using demographics, symptoms, vitals, and availability signals." : mode === "LAB_AWARE" ? "Comparison after ordered tests become available. This is not the early-triage surface." : "A methodological demonstration of how leakage can inflate apparent performance."}</p>
  <div class="metrics">${metric("Macro-F1", metrics.macro_f1.toFixed(2), "held-out test")}${metric("Macro-recall", metrics.macro_recall.toFixed(2), "held-out test")}${metric("Macro PR-AUC", metrics.macro_pr_auc.toFixed(2), "held-out test")}</div>
  <h2 class="section-heading">Per-label risk, lowest recall first</h2>${table(rows, [
    { key: "label", label: "Label", render: titleCase },
    { key: "support_pos", label: "Support" },
    { key: "f1", label: "F1", render: (value) => number(value) },
    { key: "recall", label: "Recall", render: (value) => number(value) },
    { key: "false_negative_rate", label: "FNR", render: (value) => `<span class="${value > .5 ? "tag tag-risk" : "tag"}">${number(value)}</span>` },
    { key: "pr_auc", label: "PR-AUC", render: (value) => number(value) },
  ])}`;
}

function uncertaintyView() {
  const summary = bundle.dashboard.summary.conformal;
  const rows = bundle.dashboard.conformal_per_label;
  const typhoid = rows.find((row) => row.label === "typhoid");
  return `<p class="view-lede">A conformal set is a set of plausible model labels at a target coverage level. It is not a diagnostic list and it can deliberately remain broad when evidence is ambiguous.</p>
  <div class="metrics">${metric("Coverage", percent(summary.overall_coverage), "target 90%")}${metric("Average set size", number(summary.avg_set_size), `of ${bundle.dashboard.summary.active_labels.length} labels`)}${metric("Ambiguous sets", percent(summary.pct_ambiguous_multi / 100), "set size ≥2")}</div>
  <aside class="callout callout-risk"><strong>Undercoverage risk:</strong> Typhoid coverage is ${typhoid ? percent(typhoid.empirical_coverage) : "not available"} with limited positive support. Yellow fever values must also be read beside its very small support.</aside>
  ${table(rows, [
    { key: "label", label: "Label", render: titleCase },
    { key: "test_positives", label: "Positive support" },
    { key: "empirical_coverage", label: "Coverage", render: (value) => percent(value) },
    { key: "prob_threshold", label: "Inclusion threshold", render: (value) => number(value) },
    { key: "predicted_inclusions", label: "Inclusions" },
  ])}`;
}

function explainabilityView() {
  const rows = bundle.dashboard.importance_global.slice(0, 12);
  return `<p class="view-lede">Explanations describe model associations, not medical causes. Anonymized and engineered feature names require clinician and data-owner interpretation.</p>
  <div class="grid grid-2"><article class="panel"><h2>Global importance</h2>${dataBars(rows, "importance_mean", "feature", { max: Math.max(...rows.map((row) => row.importance_mean)) })}</article>${figure("feature_importance_per_label.png", "Per-label feature importance chart", "Different labels rely on different signal patterns, reinforcing the need for per-label review.")}</div>
  <aside class="callout"><strong>Case-level interpretation:</strong> A local explanation indicates which inputs moved this model output. It does not establish that changing an input would change disease risk.</aside>`;
}

function filteredCases() {
  const disease = document.querySelector("#filter-disease")?.value || "";
  const tier = document.querySelector("#filter-tier")?.value || "";
  const uncertainty = document.querySelector("#filter-uncertainty")?.value || "";
  const query = document.querySelector("#filter-case")?.value.trim().toUpperCase() || "";
  return bundle.cases.filter((item) =>
    (!disease || listLabels(item.predicted_labels).includes(disease)) &&
    (!tier || item.triage_category === tier) &&
    (!uncertainty || item.uncertainty_category === uncertainty) &&
    (!query || item.case_id.includes(query)),
  );
}

function casesView() {
  const labels = bundle.dashboard.summary.active_labels;
  return `<p class="view-lede">Explore the curated public cases by operational attributes. This surface contains no UUID or ground truth.</p>
  <div class="filters"><div class="field"><label for="filter-disease">Predicted disease</label><select id="filter-disease"><option value="">All diseases</option>${labels.map((label) => `<option value="${label}">${titleCase(label)}</option>`).join("")}</select></div><div class="field"><label for="filter-tier">Triage tier</label><select id="filter-tier"><option value="">All tiers</option>${[...new Set(bundle.cases.map((item) => item.triage_category))].map((tier) => `<option>${tier}</option>`).join("")}</select></div><div class="field"><label for="filter-uncertainty">Uncertainty</label><select id="filter-uncertainty"><option value="">All levels</option><option>low</option><option>moderate</option><option>high</option></select></div><div class="field"><label for="filter-case">Case ID</label><input id="filter-case" type="search" placeholder="CASE-001"></div></div>
  <div class="filter-status"><span id="case-count"></span><button class="button button-quiet" id="clear-filters" type="button">Clear filters</button></div><div id="case-results"></div>`;
}

function updateCaseResults() {
  const rows = filteredCases();
  document.querySelector("#case-count").textContent = `${rows.length} curated cases shown`;
  document.querySelector("#case-results").innerHTML = table(rows, [
    { key: "case_id", label: "Case", render: (value) => `<a class="text-link open-case" href="#triage" data-case="${value}">${value}</a>` },
    { key: "scenario", label: "Why interesting" },
    { key: "triage_category", label: "Triage", render: (value) => `<span class="${value.includes("Urgent") ? "tag tag-risk" : "tag"}">${value}</span>` },
    { key: "uncertainty_category", label: "Uncertainty", render: (value) => titleCase(value) },
    { key: "predicted_labels", label: "Predicted labels", render: (value) => listLabels(value).map(titleCase).join(", ") },
  ]);
  document.querySelectorAll(".open-case").forEach((link) => link.addEventListener("click", () => { selectedCaseId = link.dataset.case; }));
}

function triageView() {
  const item = bundle.cases.find((caseItem) => caseItem.case_id === selectedCaseId) || bundle.cases[0];
  selectedCaseId = item.case_id;
  const urgent = item.triage_category.includes("Urgent") || item.triage_category.includes("Confirmatory");
  return `<p class="view-lede">A curated operational case view. Ground truth is intentionally absent; retrospective evaluation remains aggregate-only.</p><div class="case-layout"><aside class="panel case-picker"><div class="field"><label for="case-select">Curated case</label><select id="case-select">${bundle.cases.map((caseItem) => `<option value="${caseItem.case_id}" ${caseItem.case_id === item.case_id ? "selected" : ""}>${caseItem.case_id} · ${caseItem.scenario}</option>`).join("")}</select></div><p><strong>Why this case is interesting</strong><br>${item.scenario}</p><button class="button button-secondary" id="previous-case" type="button">Previous case</button><button class="button button-secondary" id="next-case" type="button">Next case</button></aside>
  <article class="case-summary"><div class="panel"><span class="tag ${urgent ? "tag-risk" : ""}">Action summary</span><h2>${item.triage_category}</h2><div class="tier-line"><span class="tier-dot ${urgent ? "urgent" : "routine"}"></span><strong>Score ${number(item.triage_score)}</strong><span>${urgent ? "Prompt human review required" : "Clinician confirmation before any care decision"}</span></div></div><h2 class="section-heading">Predicted labels against operational thresholds</h2><div class="panel">${probabilityBars(item, bundle.dashboard.summary.active_labels, bundle.dashboard.thresholds)}</div><div class="grid grid-2"><article class="panel"><h3>Conformal set</h3><p>${listLabels(item.conformal_set).map((label) => `<span class="tag">${titleCase(label)}</span>`).join(" ")}</p><p>${titleCase(item.uncertainty_category)} uncertainty. A larger set indicates greater ambiguity.</p></article><article class="panel"><h3>Human next step</h3><p>Review the complete clinical presentation and local protocol. Confirmatory testing is appropriate when ambiguity or escalation burden is high.</p><a class="text-link" href="#methodology">Review threshold methodology</a></article></div></article></div>`;
}

function resourceView() {
  return `<p class="view-lede">Project daily triage demand against confirmatory-test and urgent-review capacity. Results are deterministic scenario projections, not staffing prescriptions.</p><div class="resource-layout"><form class="panel" id="resource-form"><div class="field"><label for="policy">Threshold policy</label><select id="policy"><option value="operational">Operational</option><option value="safety">Safety</option><option value="performance">Performance</option></select></div><div class="field"><label for="cohort-range">Daily cohort size</label><div class="range-pair"><input id="cohort-range" type="range" min="0" max="1000" value="300"><input id="cohort-number" type="number" min="0" max="1000" value="300"></div></div><div class="field"><label for="test-capacity">Confirmatory test capacity</label><input id="test-capacity" type="number" min="0" value="70"></div><div class="field"><label for="urgent-capacity">Urgent review capacity</label><input id="urgent-capacity" type="number" min="0" value="40"></div><button class="button button-quiet" id="reset-resource" type="button">Reset baseline</button></form><div><div class="resource-output" id="resource-output"></div><div class="panel"><h2>Projected tier distribution</h2><div id="tier-output"></div></div></div></div>`;
}

function updateResources() {
  const policy = document.querySelector("#policy").value;
  const cohortSize = Number(document.querySelector("#cohort-number").value);
  const tradeoff = bundle.dashboard.policy_tradeoff.find((row) => row.policy === policy);
  const total = bundle.dashboard.summary.shape[0];
  const distribution = bundle.dashboard.summary.triage_distribution;
  const baselineTests = bundle.dashboard.resource.find((row) => row.metric === "require_confirmatory_test")?.count || 88;
  const operationalTradeoff = bundle.dashboard.policy_tradeoff.find((row) => row.policy === "operational");
  const rates = {
    routine: distribution["Routine Monitoring"] / total,
    review: distribution["Clinical Review"] / total,
    priority: distribution["Confirmatory Test Priority"] / total,
    urgent: distribution["Urgent Response Priority"] / total,
  };
  const policyScale = (tradeoff?.avg_flags_per_patient || 1) / (operationalTradeoff?.avg_flags_per_patient || 1);
  const testRate = Math.min(1, baselineTests / total * policyScale);
  const result = simulateResources({
    cohortSize,
    baseCohortSize: total,
    tierRates: rates,
    testRate,
    testCapacity: Number(document.querySelector("#test-capacity").value),
    urgentCapacity: Number(document.querySelector("#urgent-capacity").value),
  });
  document.querySelector("#resource-output").innerHTML = [
    ["Tests required", result.testsNeeded, false, "Projected demand"],
    ["Unmet test demand", result.unmetTests, result.unmetTests > 0, result.unmetTests > 0 ? "⚠ Capacity exceeded" : "Within entered capacity"],
    ["Urgent reviews", result.urgentNeeded, false, "Projected demand"],
    ["Urgent overload", result.unmetUrgent, result.unmetUrgent > 0, result.unmetUrgent > 0 ? "⚠ Capacity exceeded" : "Within entered capacity"],
  ].map(([label, value, overload, status]) => `<article class="capacity-result ${overload ? "overload" : ""}"><span>${label}</span><strong>${value}</strong><small>${status}</small></article>`).join("");
  document.querySelector("#tier-output").innerHTML = dataBars(Object.entries(result.tierCounts).map(([label, count]) => ({ label, count })), "count", "label", { max: Math.max(1, cohortSize) });
}

function trustView() {
  const loco = bundle.dashboard.loco;
  return `<div class="insight-hero"><span>ROBUSTNESS HEADLINE</span><h2>Center transfer is the largest generalization warning.</h2><p>Leave-one-center-out macro-F1 falls to ${loco.map((row) => row.macro_f1.toFixed(2)).join(" and ")}. Facility-specific recalibration and prospective validation are required.</p></div>
  ${table(loco, [
    { key: "test_on", label: "Held-out center" },
    { key: "n_test", label: "Sample size" },
    { key: "macro_f1", label: "Macro-F1", render: (value) => `<span class="tag tag-risk">${number(value)}</span>` },
    { key: "micro_f1", label: "Micro-F1", render: (value) => number(value) },
  ])}<h2 class="section-heading">Subgroup evidence</h2>${table(bundle.dashboard.fairness, [
    { key: "axis", label: "Subgroup", render: titleCase },
    { key: "level", label: "Level" },
    { key: "n", label: "n" },
    { key: "macro_f1", label: "Macro-F1", render: (value) => number(value) },
    { key: "n", label: "Reliability", render: (value) => `<span class="${value < 15 ? "tag tag-risk" : value < 30 ? "tag tag-warn" : "tag"}">${value < 15 ? "Insufficient evidence" : value < 30 ? "Low support" : "Adequate support"}</span>` },
  ])}`;
}

function methodologyView() {
  return `<p class="view-lede">The public static dashboard presents precomputed evidence and curated cases. It does not run live inference or store patient data.</p>
  <div class="grid grid-3"><article class="panel"><h2>PRE_LAB</h2><p>Deployable evidence from demographics, symptoms, vitals, and signal availability.</p></article><article class="panel"><h2>LAB_AWARE</h2><p>Workflow comparison after ordered tests become available.</p></article><article class="panel"><h2>FULL</h2><p>Research-only leakage demonstration. Never a deployment recommendation.</p></article></div>
  <h2 class="section-heading">Evaluation and threshold policy</h2><div class="grid grid-2"><article class="panel"><h3>Split and sources</h3><p>Primary model metrics come from a held-out test split. Cohort views use honest out-of-fold predictions where specified. Sources are not mixed without labels.</p></article><article class="panel"><h3>Operational thresholds</h3>${table(bundle.dashboard.threshold_policies, [{ key: "label", label: "Label", render: titleCase }, { key: "operational", label: "Operational", render: number }, { key: "safety", label: "Safety", render: number }])}</article></div>
  <h2 class="section-heading">Known limitations</h2><div class="callout callout-risk"><strong>Small and imbalanced cohort:</strong> n=300, yellow fever prevalence 4%, three inactive labels, structured missingness, and only two facilities.</div>
  <h2 class="section-heading">Glossary</h2>${table([
    ["Macro-F1", "Average F1 across labels, giving rare labels equal weight."],
    ["Macro-recall", "Average sensitivity across labels."],
    ["PR-AUC", "Precision-recall area, useful under class imbalance."],
    ["OOF", "Out-of-fold predictions from models that did not train on that row."],
    ["Conformal coverage", "Observed frequency that the prediction set contains the recorded label."],
    ["Set size", "Number of plausible labels retained by conformal prediction."],
    ["FNR", "False-negative rate, the share of positives missed."],
    ["LOCO", "Leave-one-center-out evaluation of facility transfer."],
  ].map(([term, meaning]) => ({ term, meaning })), [{ key: "term", label: "Term" }, { key: "meaning", label: "Plain-language meaning" }])}`;
}

const renderers = {
  overview,
  data: dataView,
  models: modelView,
  uncertainty: uncertaintyView,
  explainability: explainabilityView,
  cases: casesView,
  triage: triageView,
  resources: resourceView,
  trust: trustView,
  methodology: methodologyView,
};

function bindView() {
  if (currentRoute === "cases") {
    ["filter-disease", "filter-tier", "filter-uncertainty", "filter-case"].forEach((id) => document.querySelector(`#${id}`).addEventListener("input", updateCaseResults));
    document.querySelector("#clear-filters").addEventListener("click", () => {
      ["filter-disease", "filter-tier", "filter-uncertainty", "filter-case"].forEach((id) => { document.querySelector(`#${id}`).value = ""; });
      updateCaseResults();
    });
    updateCaseResults();
  }
  if (currentRoute === "triage") {
    const select = document.querySelector("#case-select");
    select.addEventListener("change", () => { selectedCaseId = select.value; renderRoute(false); });
    const move = (offset) => {
      const index = bundle.cases.findIndex((item) => item.case_id === selectedCaseId);
      selectedCaseId = bundle.cases[(index + offset + bundle.cases.length) % bundle.cases.length].case_id;
      renderRoute(false);
    };
    document.querySelector("#previous-case").addEventListener("click", () => move(-1));
    document.querySelector("#next-case").addEventListener("click", () => move(1));
  }
  if (currentRoute === "resources") {
    const range = document.querySelector("#cohort-range");
    const numberInput = document.querySelector("#cohort-number");
    range.addEventListener("input", () => { numberInput.value = range.value; updateResources(); });
    numberInput.addEventListener("input", () => { range.value = numberInput.value; updateResources(); });
    ["policy", "test-capacity", "urgent-capacity"].forEach((id) => document.querySelector(`#${id}`).addEventListener("input", updateResources));
    document.querySelector("#reset-resource").addEventListener("click", () => {
      document.querySelector("#policy").value = "operational";
      range.value = numberInput.value = 300;
      document.querySelector("#test-capacity").value = 70;
      document.querySelector("#urgent-capacity").value = 40;
      updateResources();
    });
    updateResources();
  }
}

function renderRoute(focus = true) {
  const route = routes.find((item) => item.key === currentRoute);
  document.querySelector("#section-group").textContent = route.group;
  const heading = document.querySelector("#section-title");
  heading.textContent = route.label;
  document.querySelectorAll("[data-route]").forEach((link) => link.setAttribute("aria-current", link.dataset.route === currentRoute ? "page" : "false"));
  view().innerHTML = renderers[currentRoute]();
  bindView();
  if (focus) heading.focus({ preventScroll: true });
  window.scrollTo({ top: 0, behavior: "instant" });
}

function navigate(route) {
  currentRoute = normalizeRoute(`#${route}`, routes.map((item) => item.key));
  history.pushState({ route: currentRoute }, "", routeHref(currentRoute));
  renderRoute();
}

function renderCurrentRoute() {
  const normalized = normalizeRoute(location.hash, routes.map((item) => item.key));
  const unknown = location.hash && location.hash !== `#${normalized}`;
  currentRoute = normalized;
  document.querySelector("#route-notice").textContent = unknown ? "Unknown section. Showing Executive overview." : "";
  renderRoute();
}

function openMenu() {
  document.querySelector("#sidebar").classList.add("open");
  document.querySelector("#drawer-backdrop").classList.add("open");
  document.body.classList.add("menu-open");
  document.querySelector("#open-menu").setAttribute("aria-expanded", "true");
  document.querySelector("#close-menu").focus();
}

function closeMenu() {
  document.querySelector("#sidebar").classList.remove("open");
  document.querySelector("#drawer-backdrop").classList.remove("open");
  document.body.classList.remove("menu-open");
  document.querySelector("#open-menu").setAttribute("aria-expanded", "false");
}

function trapDrawerFocus(event) {
  const sidebar = document.querySelector("#sidebar");
  if (event.key !== "Tab" || !sidebar.classList.contains("open")) return;
  const focusable = [...sidebar.querySelectorAll("a[href], button:not([disabled]), select, input")]
    .filter((element) => !element.hidden);
  if (!focusable.length) return;
  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}

async function init() {
  bundle = await loadBundle();
  selectedCaseId = bundle.cases[0].case_id;
  renderNav();
  const { manifest } = bundle;
  document.querySelector("#run-status").textContent = manifest.canonical ? "Canonical run" : "Non-canonical run";
  document.querySelector("#run-meta").textContent = `${manifest.model_track} · ${manifest.evaluation_split} · ${manifest.generated_at.slice(0, 10)}`;
  document.querySelector("#model-mode").addEventListener("change", () => {
    if (currentRoute !== "models") navigate("models");
    else renderRoute(false);
  });
  document.querySelector("#open-menu").addEventListener("click", openMenu);
  document.querySelector("#close-menu").addEventListener("click", closeMenu);
  document.querySelector("#drawer-backdrop").addEventListener("click", closeMenu);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeMenu();
    trapDrawerFocus(event);
  });
  window.addEventListener("hashchange", renderCurrentRoute);
  window.addEventListener("popstate", renderCurrentRoute);
  renderCurrentRoute();
}

init().catch((error) => {
  view().innerHTML = `<div class="callout callout-risk"><strong>Dashboard data unavailable.</strong><br>${error.message}. Serve the web directory over localhost and regenerate the public bundle.</div>`;
});

import {
  DeploymentGate,
  EvidenceScopeBadge,
  EvidenceStatus,
  ScientificCaveat,
  figure,
  metric,
  table,
} from "./components.js";
import { number, percent, titleCase } from "./formatters.js";

const CLASS_ORDER = ["malaria", "other_diseases", "dengue", "typhoid", "yellow_fever"];


export function aggregateMetricRows(bundle, track = "PRE_LAB") {
  const row = bundle.evidence.validation_and_frozen_test.frozen_test.find(
    (item) => item.track === track,
  );
  if (!row) return [];
  return [
    { metric: "Macro-F1", estimate: row.macro_f1, source: `Frozen test · ${track}` },
    { metric: "Micro-F1", estimate: row.micro_f1, source: `Frozen test · ${track}` },
    { metric: "Macro PR-AUC", estimate: row.macro_pr_auc, source: `Frozen test · ${track}` },
    { metric: "Macro recall", estimate: row.macro_recall, source: `Frozen test · ${track}` },
  ];
}


// Short, evidence-bound interpretation under each headline metric.
const METRIC_INTERPRETATION = {
  "Macro-F1": "Unweighted mean across all five labels — rare labels weigh equally with malaria.",
  "Micro-F1": "Pools every label decision — dominated by the high-support labels the prototype handles best.",
  "Macro PR-AUC": "Ranking quality under heavy class imbalance, averaged across labels.",
};

export function executiveEvidence(bundle) {
  const counts = bundle.evidence.cohort_and_partitions.counts;
  const metrics = aggregateMetricRows(bundle).slice(0, 3);
  return `${EvidenceScopeBadge("Frozen test and training-only nested validation")}
    <div class="insight-hero"><h2>Differential-risk review implemented as an auditable operational prototype.</h2><p>${bundle.evidence.narrative.patient_workflow}</p><a class="button button-primary" href="prototype.html">Open operational prototype</a></div>
    <div class="metrics">${metrics.map((row) => metric(row.metric, number(row.estimate, 3), METRIC_INTERPRETATION[row.metric] || row.source)).join("")}</div>
    <div class="inline-stats"><span><strong>${counts.n_supervised}</strong> supervised patients</span><span><strong>${counts.training}</strong> training pool</span><span><strong>${counts.frozen_test}</strong> frozen test</span></div>
    ${ScientificCaveat(bundle.evidence.primary_track_summary.decision)}`;
}


export function governanceEvidence(bundle) {
  const leakage = bundle.evidence.data_quality_and_leakage.leakage;
  return `${EvidenceScopeBadge("Training-pool governance")}
    <p class="view-lede">Raw-source lineage and clinical availability stage determine whether a feature can enter deployable evidence.</p>
    ${table(leakage.slice(0, 40), [
      { key: "feature", label: "Raw feature" },
      { key: "decision", label: "Stage", render: titleCase },
      { key: "best_label", label: "Strongest association", render: titleCase },
      { key: "max_single_feature_auc", label: "Screen AUC", render: number },
      { key: "rationale", label: "Rationale" },
    ])}`;
}


export function evaluationEvidence(bundle, track) {
  const headline = aggregateMetricRows(bundle, track);
  const rows = bundle.evidence.validation_and_frozen_test.per_label
    .filter((row) => row.track === track)
    .slice()
    .sort((a, b) => CLASS_ORDER.indexOf(a.label) - CLASS_ORDER.indexOf(b.label));
  // PR-AUC at three digits so a 0.996 ranking never renders as a misleading 1.00.
  const ratio3 = (value) => number(value, 3);
  const ratio2 = (value) => number(value, 2);
  return `${EvidenceScopeBadge("Frozen test confirmation · single one-shot evaluation")}
    <p class="view-lede">${track === "PRE_LAB"
      ? "Primary deployable research track. Reported once on the 78-patient frozen test, no lab inputs required."
      : "Paired laboratory-aware comparison. Requires confirmatory inputs and does not establish operational superiority."}</p>
    <div class="metrics">${headline.map((row) => metric(row.metric, number(row.estimate, 3), row.source)).join("")}</div>
    <h3 class="section-heading">Per-label scorecard</h3>
    ${table(rows, [
      { key: "label", label: "Label", render: titleCase },
      { key: "support_pos", label: "Positives" },
      { key: "tp", label: "TP" },
      { key: "fp", label: "FP" },
      { key: "fn", label: "FN" },
      { key: "precision", label: "Precision", render: ratio2 },
      { key: "recall", label: "Recall", render: ratio2 },
      { key: "f1", label: "F1", render: ratio2 },
      { key: "pr_auc", label: "PR-AUC", render: ratio3 },
      { key: "support_pos", label: "Evidence status", render: (value) => EvidenceStatus(value) },
    ])}
    <p class="table-note">Recall is consistent with the FN column (recall = TP ÷ (TP + FN)); for malaria FN = 0, so recall = 1.00 on this frozen test. PR-AUC is shown to three digits to distinguish near-perfect ranking from a true 1.0.</p>
    ${ScientificCaveat("Malaria has high support and stable recall; rare labels (typhoid, yellow fever) are evidence-limited and must be routed to confirmatory testing and clinical review rather than read as confident negatives.")}`;
}


const policyCard = (title, lede, summary) => `<article class="panel policy-card">
  <h2>${title}</h2><p>${lede}</p>
  <dl class="policy-facts">
    <div><dt>Overall coverage</dt><dd>${percent(summary.overall_coverage)}</dd></div>
    <div><dt>Average set size</dt><dd>${number(summary.avg_set_size, 2)} labels</dd></div>
    <div><dt>False-negative risk</dt><dd>${percent(summary.false_negative_risk)}</dd></div>
    <div><dt>Ambiguous (multi-label) sets</dt><dd>${percent(summary.pct_ambiguous_multi / 100)}</dd></div>
  </dl>
</article>`;

export function uncertaintyEvidence(bundle) {
  const section = bundle.evidence.calibration_and_prediction_sets;
  const exact = section.prediction_sets.exact_summary;
  const pragmatic = section.prediction_sets.pragmatic_summary;
  return `${EvidenceScopeBadge("Frozen test reliability · conformal prediction sets")}
    <p class="view-lede">Prediction sets express how many labels must stay under review to retain the target coverage. They are a review-routing tool, not a clinical safety guarantee.</p>
    <div class="grid grid-2">
      ${policyCard("Exact empirical policy", "Uncapped: holds empirical coverage at the cost of larger review sets.", exact)}
      ${policyCard("Pragmatic efficiency policy", "Capped for throughput: smaller sets, accepting higher false-negative risk.", pragmatic)}
    </div>
    ${figure("risk-coverage.png", "Risk versus coverage trade-off across uncertainty cut-offs.", "Retaining more cases (higher coverage) lowers selective risk; the curve is the basis for the safe-deferral cut-off.")}
    <p class="table-note">Exact holds ${percent(exact.overall_coverage)} coverage with ${percent(exact.false_negative_risk)} false-negative risk; pragmatic trades down to ${percent(pragmatic.overall_coverage)} coverage but ${percent(pragmatic.false_negative_risk)} false-negative risk. Choosing a policy is an operational decision about review capacity versus missed-label tolerance.</p>
    ${ScientificCaveat("High coverage is reported together with set size, ambiguity, and false-negative risk. It is not described as clinical safety, and large sets indicate the model is deferring rather than discriminating.")}`;
}


// Per-center interpretation derived only from that row's recalls — no
// placeholder values, no implied causation.
function centerInterpretation(row) {
  const collapsed = CLASS_ORDER
    .filter((label) => Number(row[`recall_${label}`]) === 0)
    .map(titleCase);
  if (!collapsed.length) return "Recall retained across labels at this held-out center.";
  return `Malaria recall holds (${percent(row.recall_malaria)}); recall collapses to zero for ${collapsed.join(", ")}.`;
}

export function fairnessEvidence(bundle) {
  const section = bundle.evidence.fairness_and_center_transfer;
  const summary = bundle.evidence.center_transfer_summary;
  return `${EvidenceScopeBadge("Frozen test subgroups and center transfer")}
    <article class="panel highlight-panel">
      <span class="panel-kicker">Principal generalization warning</span>
      <h2>Center transfer is the main barrier to transportability.</h2>
      <p>Holding out an entire treatment center drops macro-F1 to <strong>${number(summary.macro_f1_min, 3)}–${number(summary.macro_f1_max, 3)}</strong> across ${summary.n_centers} centers — far below the ${number(bundle.evidence.primary_track_summary.macro_f1, 3)} pooled frozen-test macro-F1. Local validation is required before any operational use.</p>
    </article>
    <p class="view-lede">Leave-one-center-out (LOCO): the model is trained on the other center(s) and evaluated on the held-out center. Subgroup estimates remain descriptive where positive support is small.</p>
    ${table(section.center_transfer.map((row) => ({ ...row, interpretation: centerInterpretation(row) })), [
      { key: "test_on", label: "Held-out center" },
      { key: "n_test", label: "Patients" },
      { key: "macro_f1", label: "Macro-F1", render: (value) => number(value, 3) },
      { key: "micro_f1", label: "Micro-F1", render: (value) => number(value, 3) },
      { key: "interpretation", label: "Interpretation" },
    ])}
    ${ScientificCaveat("Center identity is descriptive, not causal: it stands in for unmeasured differences in case mix, recording practice, and prevalence between sites. A low off-center score does not attribute risk to the center itself.")}
    <aside class="callout callout-risk"><strong>Local validation gate:</strong> before any operational use, the locked model must be re-validated on local prospective data from the deploying site. Pooled and off-center evidence here does not establish broad transportability.</aside>`;
}


export function limitationsEvidence(bundle) {
  return `${EvidenceScopeBadge("Deployment status")}
    <article class="panel safe-use-panel">
      <span class="panel-kicker">Safe current use</span>
      <h2>What this prototype is cleared for today.</h2>
      <ul class="safe-use-list">
        <li>Retrospective research demonstration on a fixed, anonymized cohort.</li>
        <li>Evidence and figures supporting the technical report.</li>
        <li>No clinical deployment, no patient-facing use, no treatment or discharge decisions.</li>
      </ul>
    </article>
    <h2 class="section-heading">Clinical deployment remains blocked.</h2>
    <p class="view-lede">Each gate below is unmet. All are required before the locked model could be considered for any clinical setting.</p>
    <ul class="deployment-gates">${bundle.evidence.deployment_gates.map(DeploymentGate).join("")}</ul>
    <h2 class="section-heading">Limitations</h2>
    <ul class="limitation-list">${bundle.evidence.limitations.map((item) => `<li>${item}</li>`).join("")}</ul>
    ${ScientificCaveat(bundle.evidence.safe_scope)}`;
}

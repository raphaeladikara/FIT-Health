import {
  DeploymentGate,
  EvidenceScopeBadge,
  IntervalMetric,
  ScientificCaveat,
  SupportStatus,
  table,
} from "./components.js";
import { number, titleCase } from "./formatters.js";


const metricRows = (bundle, track = "PRE_LAB") =>
  bundle.evidence.validation_and_frozen_test.metrics.filter(
    (row) => row.track === track
  );


export function executiveEvidence(bundle) {
  const counts = bundle.evidence.cohort_and_partitions.counts;
  const metrics = metricRows(bundle).slice(0, 3);
  return `${EvidenceScopeBadge("Frozen test and training-only nested validation")}
    <div class="insight-hero"><h2>Differential-risk review with visible uncertainty and provenance.</h2><p>${bundle.evidence.safe_scope}</p></div>
    <div class="metrics">${metrics.map(IntervalMetric).join("")}</div>
    <div class="inline-stats"><span><strong>${counts.n_supervised}</strong> supervised patients</span><span><strong>${counts.training}</strong> training pool</span><span><strong>${counts.frozen_test}</strong> frozen test</span></div>
    ${ScientificCaveat(bundle.evidence.limitations[0])}`;
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
  const metrics = metricRows(bundle, track);
  const rows = bundle.evidence.validation_and_frozen_test.per_label.filter(
    (row) => row.track === track
  );
  return `${EvidenceScopeBadge("Frozen test confirmation")}
    <p class="view-lede">${track === "PRE_LAB" ? "Primary deployable research track." : "Paired laboratory-aware comparison."}</p>
    <div class="metrics">${metrics.slice(0, 4).map(IntervalMetric).join("")}</div>
    ${table(rows, [
      { key: "label", label: "Label", render: titleCase },
      { key: "support_pos", label: "Evidence", render: (value) => SupportStatus(value) },
      { key: "pr_auc", label: "PR-AUC", render: number },
      { key: "f1", label: "F1", render: number },
      { key: "recall", label: "Recall", render: number },
      { key: "fn", label: "False negatives" },
    ])}`;
}


export function uncertaintyEvidence(bundle) {
  const section = bundle.evidence.calibration_and_prediction_sets;
  const exact = section.prediction_sets.exact_summary;
  const pragmatic = section.prediction_sets.pragmatic_summary;
  return `${EvidenceScopeBadge("Frozen test reliability")}
    <div class="grid grid-2"><article class="panel"><h2>Exact empirical policy</h2><p>Coverage ${number(exact.overall_coverage)}; average set size ${number(exact.avg_set_size)}.</p></article><article class="panel"><h2>Pragmatic efficiency policy</h2><p>Coverage ${number(pragmatic.overall_coverage)}; average set size ${number(pragmatic.avg_set_size)}.</p></article></div>
    ${ScientificCaveat("High coverage is reported together with set size, ambiguity, and false-negative risk. It is not described as clinical safety.")}`;
}


export function fairnessEvidence(bundle) {
  const section = bundle.evidence.fairness_and_center_transfer;
  return `${EvidenceScopeBadge("Frozen test subgroups and center transfer")}
    <p class="view-lede">Subgroup estimates remain descriptive where positive support is small. Center identity is not treated as a causal explanation.</p>
    ${table(section.center_transfer, [
      { key: "test_on", label: "Held-out center" },
      { key: "n_test", label: "Patients" },
      { key: "macro_f1", label: "Macro-F1", render: number },
      { key: "micro_f1", label: "Micro-F1", render: number },
    ])}`;
}


export function limitationsEvidence(bundle) {
  return `${EvidenceScopeBadge("Deployment status")}
    <h2>Clinical deployment remains blocked.</h2>
    <ul class="deployment-gates">${bundle.evidence.deployment_gates.map(DeploymentGate).join("")}</ul>
    <h2 class="section-heading">Limitations</h2><ul>${bundle.evidence.limitations.map((item) => `<li>${item}</li>`).join("")}</ul>`;
}

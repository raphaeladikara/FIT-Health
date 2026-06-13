import type { DashboardData, EvaluationMode, EvidenceRecord } from "@/lib/types";

export type MetricWithInterval = {
  value: number;
  interval: [number, number];
};

export type LandingSnapshot = {
  patientCount: number;
  multiLabelCount: number;
  multiLabelShare: number;
  activeLabelCount: number;
  macroF1: MetricWithInterval;
  macroRecall: MetricWithInterval;
  canonical: boolean;
  evaluationMode: EvaluationMode;
  runId: string;
};

/**
 * Confidence interval for a named headline metric. Throws when the canonical
 * bootstrap interval is absent, so the landing page can never silently invent or
 * omit the uncertainty band beside a headline number.
 */
export function intervalForMetric(
  rows: EvidenceRecord[],
  metric: string,
): MetricWithInterval {
  const row = rows.find((entry) => entry.metric === metric);
  if (!row) {
    throw new Error(
      `Missing confidence interval for "${metric}" in headline_metric_bootstrap_ci.`,
    );
  }
  const value = Number(row.estimate);
  const low = Number(row.ci_low);
  const high = Number(row.ci_high);
  if ([value, low, high].some(Number.isNaN)) {
    throw new Error(`Confidence interval for "${metric}" has non-numeric bounds.`);
  }
  return { value, interval: [low, high] };
}

export function buildLandingSnapshot(data: DashboardData): LandingSnapshot {
  const { manifest, summary, evidence } = data;
  const patientCount = manifest.patient_count;
  const multiLabelCount = Number(summary.n_multilabel_patients ?? 0);
  return {
    patientCount,
    multiLabelCount,
    multiLabelShare: patientCount > 0 ? multiLabelCount / patientCount : 0,
    activeLabelCount: manifest.active_labels.length,
    macroF1: intervalForMetric(evidence.confidence_intervals, "macro_f1"),
    macroRecall: intervalForMetric(evidence.confidence_intervals, "macro_recall"),
    canonical: manifest.canonical,
    evaluationMode: manifest.evaluation_mode,
    runId: manifest.run_id,
  };
}

import { describe, expect, it } from "vitest";

import { buildLandingSnapshot, intervalForMetric } from "@/lib/landing-content";
import type { DashboardData } from "@/lib/types";

const data = {
  manifest: {
    schema_version: 2,
    run_id: "20260614-abcd1234-deadbeef-cafebabe",
    git_commit: "abcd1234",
    data_checksum: "deadbeef",
    config_checksum: "cafebabe",
    generated_at: "2026-06-14T00:00:00Z",
    execution_profile: "full",
    canonical: true,
    evaluation_mode: "held_out",
    threshold_policy: "operational",
    model_versions: { PRE_LAB: "extra_trees" },
    patient_count: 300,
    active_labels: ["malaria", "other_diseases", "dengue", "typhoid", "yellow_fever"],
    available_evidence: [],
    warnings: [],
  },
  summary: {
    project: "VECTRA-X",
    shape: [300, 40],
    active_labels: ["malaria", "other_diseases", "dengue", "typhoid", "yellow_fever"],
    n_multilabel_patients: 158,
    test_metrics: { PRE_LAB: { macro_f1: 0.6095 } },
  },
  patients: [],
  evidence: {
    model_leaderboard: [],
    per_label_metrics: [],
    calibration_metrics: [],
    conformal_metrics: [],
    fairness_metrics: [],
    fairness_recall_gaps: [],
    center_transfer: [],
    feature_importance_global: [],
    leakage_candidates: [],
    confidence_intervals: [
      { metric: "macro_f1", estimate: 0.6095, ci_low: 0.5021, ci_high: 0.7013 },
      { metric: "macro_recall", estimate: 0.6968, ci_low: 0.5269, ci_high: 0.845 },
    ],
    label_prevalence_intervals: [],
    threshold_policy_tradeoff: [],
  },
} as unknown as DashboardData;

describe("buildLandingSnapshot", () => {
  it("builds the landing evidence snapshot from canonical artifacts", () => {
    const snapshot = buildLandingSnapshot(data);
    expect(snapshot.patientCount).toBe(300);
    expect(snapshot.multiLabelCount).toBe(158);
    expect(snapshot.macroF1.interval).toEqual([0.5021, 0.7013]);
    expect(snapshot.activeLabelCount).toBe(5);
    expect(snapshot.canonical).toBe(true);
  });

  it("derives the multi-label share of the cohort", () => {
    expect(buildLandingSnapshot(data).multiLabelShare).toBeCloseTo(158 / 300, 5);
  });
});

describe("intervalForMetric", () => {
  it("throws a useful error when the headline interval is absent", () => {
    expect(() =>
      intervalForMetric(data.evidence.confidence_intervals, "nonexistent"),
    ).toThrow(/Missing confidence interval/);
  });
});

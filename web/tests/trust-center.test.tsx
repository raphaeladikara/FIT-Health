import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { EvidenceWorkspace } from "@/components/evidence/evidence-workspace";
import {
  EVIDENCE_SECTIONS,
  resolveEvidenceSection,
  type EvidenceSectionSlug,
} from "@/lib/evidence-sections";
import type { Evidence, Manifest, Summary } from "@/lib/types";

vi.mock("next/navigation", () => ({ usePathname: () => "/evidence" }));

const manifest = {
  run_id: "20260614-run",
  generated_at: "2026-06-14T00:00:00Z",
  execution_profile: "quick_smoke",
  canonical: false,
  evaluation_mode: "held_out",
  threshold_policy: "operational",
  git_commit: "abcd1234",
} as Manifest;

const summary = {
  test_metrics: { PRE_LAB: { macro_f1: 0.61 }, FULL: { macro_f1: 0.708 } },
} as unknown as Summary;

const evidence = {
  model_leaderboard: [{ track: "PRE_LAB", model: "extra_trees", macro_f1: 0.61 }],
  per_label_metrics: [
    { track: "PRE_LAB", label: "malaria", support_pos: 67, recall: 1, precision: 0.87, false_negative_rate: 0, fn: 0 },
    { track: "PRE_LAB", label: "typhoid", support_pos: 7, recall: 0.3, precision: 0.4, false_negative_rate: 0.7, fn: 5 },
  ],
  calibration_metrics: [{ label: "malaria", base_rate: 0.87, brier: 0.11, ece: 0.08, variant: "uncalibrated" }],
  conformal_metrics: [
    { label: "malaria", test_positives: 67, covered_positives: 66, empirical_coverage: 0.985, predicted_inclusions: 75 },
    { label: "typhoid", test_positives: 7, covered_positives: 4, empirical_coverage: 0.5714, predicted_inclusions: 29 },
  ],
  fairness_metrics: [],
  fairness_recall_gaps: [],
  center_transfer: [
    { test_on: "CMA de DO", n_test: 147, macro_f1: 0.3555, recall_malaria: 0.98, recall_dengue: 0, recall_typhoid: 0, recall_yellow_fever: 0 },
    { test_on: "CMA de DAFRA", n_test: 153, macro_f1: 0.3652, recall_malaria: 1, recall_dengue: 0, recall_typhoid: 0, recall_yellow_fever: 0 },
  ],
  feature_importance_global: [],
  leakage_candidates: [{ feature: "rdt_result", stage: "post_lab", reason: "restates outcome", decision: "excluded" }],
  confidence_intervals: [
    { metric: "macro_f1", estimate: 0.61, ci_low: 0.5021, ci_high: 0.7013 },
    { metric: "micro_f1", estimate: 0.824, ci_low: 0.7619, ci_high: 0.8797 },
    { metric: "macro_recall", estimate: 0.697, ci_low: 0.5269, ci_high: 0.845 },
    { metric: "macro_pr_auc", estimate: 0.606, ci_low: 0.5318, ci_high: 0.7721 },
  ],
  label_prevalence_intervals: [],
  threshold_policy_tradeoff: [],
} as unknown as Evidence;

function renderSection(section: EvidenceSectionSlug) {
  return render(
    <EvidenceWorkspace summary={summary} evidence={evidence} manifest={manifest} section={section} />,
  );
}

describe("trust center", () => {
  it("falls back to performance for an invalid section", () => {
    expect(resolveEvidenceSection("bogus").slug).toBe("performance");
    expect(resolveEvidenceSection(undefined).slug).toBe("performance");
  });

  it("shows confidence intervals beside headline metrics", () => {
    renderSection("performance");
    expect(screen.getAllByText(/95% CI/).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/0\.50–0\.70/).length).toBeGreaterThan(0);
  });

  it("keeps support counts beside rare-label metrics", () => {
    renderSection("missed-cases");
    expect(screen.getByText(/Support Pos/i)).toBeVisible();
    expect(screen.getByText("7")).toBeVisible(); // typhoid support, low-support flagged
  });

  it("makes typhoid conformal undercoverage prominent", () => {
    renderSection("abstention");
    expect(screen.getByText(/57\.1%/)).toBeVisible();
  });

  it("makes center-transfer zero recall visible", () => {
    renderSection("generalization");
    expect(
      screen.getByText(/Rare-label recall is zero in both held-out centers/i),
    ).toBeVisible();
  });

  it("labels the FULL track as research only", () => {
    renderSection("leakage");
    expect(screen.getAllByText(/Research only/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Deployable/i).length).toBeGreaterThan(0);
  });

  it("includes a claim boundary in every section", () => {
    for (const section of EVIDENCE_SECTIONS) {
      const { unmount } = renderSection(section.slug);
      expect(screen.getByText("What we cannot claim")).toBeVisible();
      unmount();
    }
  });
});

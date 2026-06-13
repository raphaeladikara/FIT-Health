import { render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { GuidedDemo } from "@/components/demo/guided-demo";
import { resolveDemoStep } from "@/lib/demo-steps";
import type { DashboardData, Patient } from "@/lib/types";

vi.mock("next/navigation", () => ({ usePathname: () => "/demo" }));

function patient(overrides: Partial<Patient> & { case_id: string }): Patient {
  return {
    predicted_labels: "{malaria}",
    conformal_set: "{malaria}",
    coinfection_prob: 0.1,
    uncertainty_level: "low",
    triage_score: 0.5,
    triage_category: "Clinical Review",
    recommended_action: "Review.",
    label_decisions: {
      malaria: { probability: 0.95, threshold: 0.05, predicted: true },
      dengue: { probability: 0.2, threshold: 0.5, predicted: false },
    },
    model_track: "PRE_LAB",
    threshold_policy: "operational",
    record_source: "full_cohort_oof",
    ...overrides,
  };
}

const data = {
  manifest: { patient_count: 4, active_labels: ["malaria", "dengue"] },
  summary: {
    n_multilabel_patients: 2,
    triage_distribution: {
      "Urgent Response Priority": 1,
      "Confirmatory Test Priority": 1,
      "Clinical Review": 1,
      "Routine Monitoring": 1,
    },
    test_metrics: {
      PRE_LAB: { macro_f1: 0.61 },
      FULL: { macro_f1: 0.708 },
    },
  },
  patients: [
    patient({ case_id: "Case 001", triage_score: 0.95, triage_category: "Urgent Response Priority" }),
    patient({
      case_id: "Case 002",
      triage_score: 0.7,
      triage_category: "Confirmatory Test Priority",
      uncertainty_level: "high",
      conformal_set: "{malaria, dengue, typhoid}",
    }),
    patient({ case_id: "Case 003", triage_score: 0.2, triage_category: "Routine Monitoring" }),
  ],
  evidence: {},
} as unknown as DashboardData;

describe("guided demo", () => {
  it("cohort: shows the multi-label count and an imbalance reading", () => {
    render(<GuidedDemo step={resolveDemoStep("cohort")} data={data} />);
    expect(document.querySelector(".demo-bigstat strong")?.textContent).toBe("2");
    expect(screen.getByText(/more than one disease signal/i)).toBeVisible();
  });

  it("leakage: labels FULL as research only", () => {
    render(<GuidedDemo step={resolveDemoStep("leakage")} data={data} />);
    expect(screen.getByText(/Research only/i)).toBeVisible();
    expect(screen.getByText(/Deployable/i)).toBeVisible();
  });

  it("patient: shows the urgent case with exported per-label thresholds", () => {
    render(<GuidedDemo step={resolveDemoStep("patient")} data={data} />);
    expect(screen.getByText("Case 001")).toBeVisible();
    // The malaria threshold (0.05) is rendered, not a fixed 0.50.
    expect(screen.getByText(/thr 0\.05/)).toBeVisible();
  });

  it("uncertainty: shows the high-uncertainty case and caution set", () => {
    render(<GuidedDemo step={resolveDemoStep("uncertainty")} data={data} />);
    expect(screen.getByText("Case 002")).toBeVisible();
    expect(screen.getByText(/high uncertainty/i)).toBeVisible();
    expect(screen.getByText("Conformal caution set")).toBeVisible();
  });

  it("resources: shows allocated, waitlisted, and not-eligible counts", () => {
    render(<GuidedDemo step={resolveDemoStep("resources")} data={data} />);
    for (const label of ["Allocated", "Waitlisted", "Not eligible"]) {
      expect(screen.getByText(label)).toBeVisible();
    }
  });

  it("navigation: step links use ?step=<slug>", () => {
    render(<GuidedDemo step={resolveDemoStep("patient")} data={data} />);
    const rail = screen.getByRole("navigation", { name: /guided demo steps/i });
    expect(within(rail).getByRole("link", { name: /Leakage trap/i })).toHaveAttribute(
      "href",
      "/demo?step=leakage",
    );
  });
});

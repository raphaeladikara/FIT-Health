import { render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { PatientIntelligence } from "@/components/patients/patient-intelligence";
import type { Manifest, Patient } from "@/lib/types";

vi.mock("next/navigation", () => ({ usePathname: () => "/patients" }));

function patient(overrides: Partial<Patient> & { case_id: string }): Patient {
  return {
    predicted_labels: "{malaria}",
    conformal_set: "{malaria}",
    coinfection_prob: 0.1,
    uncertainty_level: "low",
    triage_score: 0.5,
    triage_category: "Routine Monitoring",
    recommended_action: "Continue routine monitoring.",
    label_decisions: {
      malaria: { probability: 0.95, threshold: 0.05, predicted: true },
      dengue: { probability: 0.3, threshold: 0.5, predicted: false },
    },
    model_track: "PRE_LAB",
    threshold_policy: "operational",
    record_source: "full_cohort_oof",
    ...overrides,
  };
}

const manifest = { run_id: "20260614-run", patient_count: 3 } as Manifest;

const patients: Patient[] = [
  patient({ case_id: "Case 001", triage_score: 0.9, triage_category: "Routine Monitoring" }),
  patient({
    case_id: "Case 002",
    triage_score: 0.6,
    triage_category: "Confirmatory Test Priority",
    coinfection_prob: 0.4,
    uncertainty_level: "high",
  }),
  patient({ case_id: "Case 003", triage_score: 0.5, coinfection_prob: 0.92 }),
];

function renderReview(props: Partial<Parameters<typeof PatientIntelligence>[0]> = {}) {
  return render(
    <PatientIntelligence
      patients={patients}
      labels={["malaria", "dengue"]}
      manifest={manifest}
      {...props}
    />,
  );
}

describe("patient review", () => {
  it("uses a routine (not urgent) tone for a routine case", () => {
    renderReview();
    const summary = document.querySelector(".decision-summary") as HTMLElement;
    expect(summary).toHaveAttribute("data-tone", "routine");
  });

  it("renders each label against its exported threshold, matching predicted", () => {
    renderReview();
    const list = document.querySelector(".label-decision-list") as HTMLElement;
    // malaria: 0.95 >= 0.05 -> Flagged; dengue: 0.30 < 0.50 -> Below.
    expect(within(list).getByText(/thr 0\.05/)).toBeVisible();
    expect(within(list).getByText(/thr 0\.50/)).toBeVisible();
    const flags = list.querySelectorAll(".label-decision-flag");
    expect(flags[0].textContent).toBe("Flagged"); // malaria sorts first (higher prob)
    expect(flags[1].textContent).toBe("Below");
  });

  it("selects the strongest co-infection detector, not the most labels", () => {
    renderReview({ initialScenario: "co-infection" });
    const select = screen.getByLabelText("Anonymous case") as HTMLSelectElement;
    expect(select.value).toBe("Case 003");
  });

  it("shows a recovery state for an unknown case id", () => {
    renderReview({ initialCaseId: "Case 999" });
    expect(screen.getByText("Case not found")).toBeVisible();
    expect(
      screen.getByRole("link", { name: /Open highest-priority case/i }),
    ).toHaveAttribute("href", "/patients?scenario=highest-priority");
  });

  it("emits a privacy-safe printable report without identifiers or diagnosis claims", () => {
    renderReview({ initialCaseId: "Case 002" });
    const report = document.querySelector(".case-report") as HTMLElement;
    expect(report).toBeTruthy();
    expect(report.textContent).toMatch(/NOT a diagnosis/i);
    expect(report.textContent).toMatch(/No patient identifiers/i);
    expect(report.textContent).not.toMatch(/uuid|true_label/i);
  });
});

import { describe, expect, it } from "vitest";

import { parseLabelSet, selectRepresentativePatient } from "@/lib/patient-selection";
import type { Patient } from "@/lib/types";

function patient(overrides: Partial<Patient> & { case_id: string }): Patient {
  return {
    predicted_labels: "{malaria}",
    conformal_set: "{malaria}",
    coinfection_prob: 0.1,
    uncertainty_level: "low",
    triage_score: 0.5,
    triage_category: "Clinical Review",
    recommended_action: "Review.",
    label_decisions: {},
    model_track: "PRE_LAB",
    threshold_policy: "operational",
    record_source: "full_cohort_oof",
    ...overrides,
  };
}

const patients: Patient[] = [
  // Highest triage score and two predicted labels, but only moderate co-infection risk.
  patient({
    case_id: "Case 001",
    predicted_labels: "{malaria, dengue}",
    coinfection_prob: 0.45,
    triage_score: 0.92,
    triage_category: "Confirmatory Test Priority",
  }),
  patient({
    case_id: "Case 002",
    coinfection_prob: 0.2,
    uncertainty_level: "high",
    triage_score: 0.6,
  }),
  // Single predicted label, but the strongest separate co-infection detector score.
  patient({
    case_id: "Case 003",
    coinfection_prob: 0.88,
    triage_score: 0.55,
  }),
  patient({
    case_id: "Case 004",
    triage_score: 0.1,
    triage_category: "Routine Monitoring",
  }),
];

describe("patient selection", () => {
  it("parses serialized multi-label values", () => {
    expect(parseLabelSet("{malaria, dengue}")).toEqual(["malaria", "dengue"]);
    expect(parseLabelSet("{none}")).toEqual([]);
  });

  it("selects the highest-priority and high-uncertainty cases", () => {
    expect(selectRepresentativePatient(patients, "highest-priority")?.case_id).toBe(
      "Case 001",
    );
    expect(selectRepresentativePatient(patients, "high-uncertainty")?.case_id).toBe(
      "Case 002",
    );
    expect(selectRepresentativePatient(patients, "routine")?.case_id).toBe("Case 004");
  });

  it("selects the strongest separate co-infection risk, not the most labels", () => {
    expect(selectRepresentativePatient(patients, "co-infection")?.case_id).toBe(
      "Case 003",
    );
  });
});

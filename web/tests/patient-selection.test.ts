import { describe, expect, it } from "vitest";

import { parseLabelSet, selectRepresentativePatient } from "@/lib/patient-selection";
import type { Patient } from "@/lib/types";

const patients = [
  {
    case_id: "Case 001",
    predicted_labels: "{malaria, dengue}",
    conformal_set: "{malaria, dengue}",
    coinfection_prob: 0.9,
    uncertainty_level: "moderate",
    triage_score: 0.8,
    triage_category: "Confirmatory Test Priority",
    recommended_action: "Test.",
  },
  {
    case_id: "Case 002",
    predicted_labels: "{malaria}",
    conformal_set: "{malaria, typhoid}",
    coinfection_prob: 0.2,
    uncertainty_level: "high",
    triage_score: 0.6,
    triage_category: "Clinical Review",
    recommended_action: "Review.",
  },
] satisfies Patient[];

describe("patient selection", () => {
  it("parses serialized multi-label values", () => {
    expect(parseLabelSet("{malaria, dengue}")).toEqual(["malaria", "dengue"]);
    expect(parseLabelSet("{none}")).toEqual([]);
  });

  it("selects representative high-uncertainty and co-infection cases", () => {
    expect(selectRepresentativePatient(patients, "high-uncertainty")?.case_id).toBe(
      "Case 002",
    );
    expect(selectRepresentativePatient(patients, "co-infection")?.case_id).toBe(
      "Case 001",
    );
  });
});

import { describe, expect, it } from "vitest";

import { allocateRapidTests, calculateCapacity } from "@/lib/resource-allocation";
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
  patient({
    case_id: "Case 001",
    coinfection_prob: 0.4,
    uncertainty_level: "high",
    triage_score: 0.9,
    triage_category: "Urgent Response Priority",
  }),
  patient({
    case_id: "Case 002",
    coinfection_prob: 0.8,
    uncertainty_level: "moderate",
    triage_score: 0.7,
    triage_category: "Confirmatory Test Priority",
  }),
  patient({
    case_id: "Case 003",
    triage_score: 0.2,
    triage_category: "Routine Monitoring",
  }),
];

describe("resource allocation", () => {
  it("reports a non-negative shortfall and a matching surplus", () => {
    const rows = calculateCapacity(patients, {
      rapidTests: 1,
      beds: 0,
      monitoringSlots: 0,
      staffReviews: 1,
    });

    const tests = rows.find((row) => row.resource === "Rapid tests")!;
    expect(tests).toMatchObject({ demand: 2, capacity: 1, shortfall: 1, status: "Insufficient" });
    expect(tests.shortfall).toBe(Math.max(tests.demand - tests.capacity, 0));
    expect(tests.surplus).toBe(0);

    const beds = rows.find((row) => row.resource === "Beds")!;
    expect(beds.shortfall).toBe(1);
    expect(beds.surplus).toBe(0);
    expect(beds.assumption).toMatch(/urgent/i);
  });

  it("distinguishes allocated, waitlisted, and ineligible cases", () => {
    const result = allocateRapidTests(patients, 1);
    const byId = (id: string) => result.find((row) => row.case_id === id)?.test_allocation;
    expect(byId("Case 001")).toBe("Allocated");
    expect(byId("Case 002")).toBe("Waitlisted");
    expect(byId("Case 003")).toBe("Not eligible");
  });
});

import { describe, expect, it } from "vitest";

import { allocateRapidTests, calculateCapacity } from "@/lib/resource-allocation";
import type { Patient } from "@/lib/types";

const patients = [
  {
    case_id: "Case 002",
    predicted_labels: "{malaria}",
    conformal_set: "{malaria}",
    coinfection_prob: 0.4,
    uncertainty_level: "high",
    triage_score: 0.9,
    triage_category: "Urgent Response Priority",
    recommended_action: "Escalate.",
  },
  {
    case_id: "Case 001",
    predicted_labels: "{dengue}",
    conformal_set: "{dengue}",
    coinfection_prob: 0.8,
    uncertainty_level: "moderate",
    triage_score: 0.7,
    triage_category: "Confirmatory Test Priority",
    recommended_action: "Test.",
  },
  {
    case_id: "Case 003",
    predicted_labels: "{malaria}",
    conformal_set: "{malaria}",
    coinfection_prob: 0.1,
    uncertainty_level: "low",
    triage_score: 0.2,
    triage_category: "Routine Monitoring",
    recommended_action: "Monitor.",
  },
] satisfies Patient[];

describe("resource allocation", () => {
  it("calculates operational demand and shortages", () => {
    const rows = calculateCapacity(patients, {
      rapidTests: 1,
      beds: 0,
      monitoringSlots: 0,
      staffReviews: 1,
    });

    expect(rows.find((row) => row.resource === "Rapid tests")).toMatchObject({
      demand: 2,
      capacity: 1,
      gap: -1,
      status: "Insufficient",
    });
    expect(rows.find((row) => row.resource === "Beds")?.demand).toBe(1);
  });

  it("allocates rapid tests by score, co-infection risk, then case id", () => {
    const allocated = allocateRapidTests(patients, 1);
    expect(allocated.map((row) => [row.case_id, row.test_allocation])).toEqual([
      ["Case 002", "Allocated"],
      ["Case 001", "Waiting"],
      ["Case 003", "Waiting"],
    ]);
  });
});

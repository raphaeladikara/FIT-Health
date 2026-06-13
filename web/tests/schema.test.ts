import { describe, expect, it } from "vitest";

import { manifestSchema, patientSchema } from "@/lib/schema";

describe("public data schema", () => {
  it("accepts the supported manifest version", () => {
    expect(
      manifestSchema.parse({
        schema_version: 1,
        generated_at: "2026-06-13T00:00:00Z",
        execution_profile: "full",
        patient_count: 300,
        active_labels: ["malaria"],
        available_evidence: [],
        warnings: [],
      }).schema_version,
    ).toBe(1);
  });

  it("rejects unsupported schema versions and private patient fields", () => {
    expect(() =>
      manifestSchema.parse({
        schema_version: 2,
        generated_at: "2026-06-13T00:00:00Z",
        execution_profile: "full",
        patient_count: 1,
        active_labels: [],
        available_evidence: [],
        warnings: [],
      }),
    ).toThrow();
    expect(() =>
      patientSchema.parse({
        case_id: "Case 001",
        uuid: "private",
        predicted_labels: "{malaria}",
        conformal_set: "{malaria}",
        coinfection_prob: 0.1,
        uncertainty_level: "low",
        triage_score: 0.2,
        triage_category: "Routine Monitoring",
        recommended_action: "Monitor.",
      }),
    ).toThrow();
  });
});

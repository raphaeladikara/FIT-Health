import { describe, expect, it } from "vitest";

import { manifestSchema, patientSchema } from "@/lib/schema";

const validManifest = {
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
  active_labels: ["malaria"],
  available_evidence: [],
  warnings: [],
};

describe("public data schema", () => {
  it("accepts the supported schema-v2 manifest", () => {
    expect(manifestSchema.parse(validManifest).schema_version).toBe(2);
  });

  it("rejects the retired schema v1", () => {
    expect(() =>
      manifestSchema.parse({ ...validManifest, schema_version: 1 }),
    ).toThrow();
  });

  it("rejects an invalid evaluation mode", () => {
    expect(() =>
      manifestSchema.parse({ ...validManifest, evaluation_mode: "guess" }),
    ).toThrow();
  });

  it("rejects private patient fields", () => {
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

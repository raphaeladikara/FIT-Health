import { describe, expect, it } from "vitest";

import {
  assertOfficialArtifact,
  officialArtifactWarning,
  provenanceStatus,
} from "@/lib/provenance";
import type { Manifest } from "@/lib/types";

const baseManifest: Manifest = {
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

describe("officialArtifactWarning", () => {
  it("returns null for a canonical held-out artifact", () => {
    expect(officialArtifactWarning(baseManifest)).toBeNull();
  });

  it("flags non-canonical artifacts with the execution profile", () => {
    expect(
      officialArtifactWarning({
        ...baseManifest,
        canonical: false,
        execution_profile: "quick_smoke",
      }),
    ).toBe("Development artifact: quick_smoke");
  });

  it("flags non-held-out evaluation modes on canonical artifacts", () => {
    expect(
      officialArtifactWarning({ ...baseManifest, evaluation_mode: "oof" }),
    ).toBe("Headline metrics are out-of-fold, not held-out");
  });
});

describe("provenanceStatus", () => {
  it("is ok for a canonical held-out artifact", () => {
    expect(provenanceStatus(baseManifest).severity).toBe("ok");
  });

  it("is critical for a development artifact", () => {
    expect(
      provenanceStatus({ ...baseManifest, canonical: false }).severity,
    ).toBe("critical");
  });

  it("is warning for a canonical but non-held-out artifact", () => {
    expect(
      provenanceStatus({ ...baseManifest, evaluation_mode: "simulated" }).severity,
    ).toBe("warning");
  });
});

describe("assertOfficialArtifact", () => {
  it("throws for non-canonical artifacts", () => {
    expect(() =>
      assertOfficialArtifact({ ...baseManifest, canonical: false }),
    ).toThrow(/not canonical/);
  });

  it("passes for canonical artifacts", () => {
    expect(() => assertOfficialArtifact(baseManifest)).not.toThrow();
  });
});

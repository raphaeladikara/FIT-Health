import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ArtifactStatus } from "@/components/ui/artifact-status";
import type { Manifest } from "@/lib/types";

const base = {
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
} as Manifest;

describe("artifact status", () => {
  it("opens visible content (not just a title) with the run identity", () => {
    render(<ArtifactStatus manifest={base} />);
    // The disclosure content is in the DOM and announces the run id.
    expect(screen.getByText("Canonical held-out artifact")).toBeInTheDocument();
    expect(screen.getByText(base.run_id)).toBeInTheDocument();
    expect(screen.getByText(/PRE_LAB: extra_trees/)).toBeInTheDocument();
  });

  it("reports a development artifact and its warnings", () => {
    render(
      <ArtifactStatus
        manifest={{
          ...base,
          canonical: false,
          execution_profile: "quick_smoke",
          warnings: ["Development artifact: execution_profile='quick_smoke' is not canonical."],
        }}
      />,
    );
    expect(screen.getByText("Development artifact: quick_smoke")).toBeInTheDocument();
    expect(screen.getByText(/is not canonical/)).toBeInTheDocument();
  });

  it("surfaces a non-held-out evaluation warning on a canonical run", () => {
    render(<ArtifactStatus manifest={{ ...base, evaluation_mode: "oof" }} />);
    expect(
      screen.getByText("Headline metrics are out-of-fold, not held-out"),
    ).toBeInTheDocument();
  });
});

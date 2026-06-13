import type { Manifest } from "@/lib/types";

/** Severity of an artifact's trust state, used to drive UI tone. */
export type ProvenanceSeverity = "ok" | "warning" | "critical";

export type ProvenanceStatus = {
  severity: ProvenanceSeverity;
  /** Short human-readable headline, or null when the artifact is fully canonical. */
  warning: string | null;
  canonical: boolean;
  runId: string;
  evaluationMode: Manifest["evaluation_mode"];
};

const EVALUATION_LABELS: Record<Manifest["evaluation_mode"], string> = {
  held_out: "held-out",
  oof: "out-of-fold",
  simulated: "simulated",
};

export function evaluationModeLabel(mode: Manifest["evaluation_mode"]): string {
  return EVALUATION_LABELS[mode];
}

/**
 * Returns a single, honest warning string when the artifact should not be read as a
 * canonical held-out competition result, or `null` when it is safe to headline.
 */
export function officialArtifactWarning(manifest: Manifest): string | null {
  if (!manifest.canonical) {
    return `Development artifact: ${manifest.execution_profile}`;
  }
  if (manifest.evaluation_mode !== "held_out") {
    return `Headline metrics are ${evaluationModeLabel(manifest.evaluation_mode)}, not held-out`;
  }
  return null;
}

/** Structured trust state for status surfaces (top bar, landing, trust center). */
export function provenanceStatus(manifest: Manifest): ProvenanceStatus {
  const warning = officialArtifactWarning(manifest);
  return {
    severity: !manifest.canonical ? "critical" : warning ? "warning" : "ok",
    warning,
    canonical: manifest.canonical,
    runId: manifest.run_id,
    evaluationMode: manifest.evaluation_mode,
  };
}

/** Throws when an artifact must be canonical (e.g. a release gate) but is not. */
export function assertOfficialArtifact(manifest: Manifest): void {
  if (!manifest.canonical) {
    throw new Error(
      `Artifact is not canonical (execution_profile=${manifest.execution_profile}).`,
    );
  }
}

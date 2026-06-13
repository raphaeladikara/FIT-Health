import { CircleCheck, TriangleAlert } from "lucide-react";

import { evaluationModeLabel, provenanceStatus } from "@/lib/provenance";
import type { Manifest } from "@/lib/types";

function formatGenerated(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return new Intl.DateTimeFormat("en-GB", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "UTC",
  }).format(date);
}

/** Inline trust panel summarising the artifact a page is reading from. */
export function ProvenancePanel({ manifest }: { manifest: Manifest }) {
  const status = provenanceStatus(manifest);
  const rows: Array<[string, string]> = [
    ["Run", manifest.run_id],
    ["Generated", `${formatGenerated(manifest.generated_at)} UTC`],
    ["Profile", manifest.execution_profile],
    ["Evaluation", evaluationModeLabel(manifest.evaluation_mode)],
    ["Threshold policy", manifest.threshold_policy],
    ["Commit", manifest.git_commit.slice(0, 8)],
  ];
  return (
    <div className="provenance-panel" data-severity={status.severity}>
      <p className="provenance-headline">
        {status.warning ? (
          <TriangleAlert aria-hidden="true" size={16} />
        ) : (
          <CircleCheck aria-hidden="true" size={16} />
        )}
        {status.warning ?? "Canonical held-out artifact"}
      </p>
      <dl className="provenance-grid">
        {rows.map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}

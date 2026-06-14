import { Bell } from "lucide-react";

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

/**
 * Native <details> disclosure replacing the old inert bell. Opens visible,
 * keyboard-reachable content describing the artifact rather than hiding it in a title.
 */
export function ArtifactStatus({ manifest }: { manifest: Manifest }) {
  const status = provenanceStatus(manifest);
  const warnings = manifest.warnings.length;
  const rows: Array<[string, string]> = [
    ["Run", manifest.run_id],
    ["Generated", `${formatGenerated(manifest.generated_at)} UTC`],
    ["Profile", manifest.execution_profile],
    ["Canonical", manifest.canonical ? "Yes" : "No (development)"],
    ["Evaluation", evaluationModeLabel(manifest.evaluation_mode)],
    ["Models", Object.entries(manifest.model_versions).map(([t, m]) => `${t}: ${m}`).join(" · ") || "—"],
  ];
  return (
    <details className="artifact-status">
      <summary
        className="icon-button"
        aria-label={
          status.warning
            ? `Artifact status: ${status.warning}`
            : "Artifact status: canonical, no warnings"
        }
      >
        <Bell aria-hidden="true" size={19} />
        <span className="status-pip" data-severity={status.severity} aria-hidden="true" />
        {warnings > 0 ? <span className="badge">{warnings}</span> : null}
      </summary>
      <div className="artifact-status-panel" role="group" aria-label="Artifact provenance">
        <p className="artifact-status-head" data-severity={status.severity}>
          {status.warning ?? "Canonical held-out artifact"}
        </p>
        <dl className="artifact-status-grid">
          {rows.map(([label, value]) => (
            <div key={label}>
              <dt>{label}</dt>
              <dd>{value}</dd>
            </div>
          ))}
        </dl>
        {warnings > 0 ? (
          <ul className="artifact-status-warnings">
            {manifest.warnings.map((warning) => (
              <li key={warning}>{warning}</li>
            ))}
          </ul>
        ) : null}
      </div>
    </details>
  );
}

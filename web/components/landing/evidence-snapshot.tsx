import Link from "next/link";

import type { LandingSnapshot } from "@/lib/landing-content";
import { evaluationModeLabel } from "@/lib/provenance";

function pct(value: number): string {
  return value.toFixed(2);
}

export function EvidenceSnapshot({ snapshot }: { snapshot: LandingSnapshot }) {
  const [low, high] = snapshot.macroF1.interval;
  return (
    <section className="landing-section landing-evidence" aria-labelledby="evidence-heading">
      <div className="landing-evidence-head">
        <h2 id="evidence-heading" className="landing-section-title">
          Evidence, with its uncertainty attached
        </h2>
        <Link href="/evidence" className="landing-link">
          Open the trust center →
        </Link>
      </div>
      <dl className="evidence-band">
        <div className="evidence-stat">
          <dt>Macro F1 ({evaluationModeLabel(snapshot.evaluationMode)})</dt>
          <dd>
            {pct(snapshot.macroF1.value)}
            <span className="evidence-interval">
              95% CI {pct(low)}–{pct(high)}
            </span>
          </dd>
        </div>
        <div className="evidence-stat">
          <dt>Multi-label patients</dt>
          <dd>
            {snapshot.multiLabelCount}
            <span className="evidence-interval">
              of {snapshot.patientCount} ({Math.round(snapshot.multiLabelShare * 100)}%)
            </span>
          </dd>
        </div>
        <div className="evidence-stat">
          <dt>Active disease labels</dt>
          <dd>{snapshot.activeLabelCount}</dd>
        </div>
        <div className="evidence-stat">
          <dt>Artifact status</dt>
          <dd className="evidence-status" data-canonical={snapshot.canonical}>
            {snapshot.canonical ? "Canonical" : "Development"}
          </dd>
        </div>
      </dl>
    </section>
  );
}

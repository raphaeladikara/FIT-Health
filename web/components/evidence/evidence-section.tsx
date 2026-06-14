import type { ReactNode } from "react";

import { ClaimBoundary } from "@/components/evidence/claim-boundary";
import type { EvidenceInsight } from "@/lib/types";

function InsightCard({ insight }: { insight: EvidenceInsight }) {
  return (
    <div className="evidence-insight" data-severity={insight.severity}>
      <strong>{insight.title}</strong>
      <p className="evidence-insight-summary">{insight.summary}</p>
      <p className="evidence-insight-implication">{insight.implication}</p>
    </div>
  );
}

export function EvidenceSection({
  question,
  insight,
  children,
}: {
  question: string;
  insight: EvidenceInsight;
  children: ReactNode;
}) {
  return (
    <section className="evidence-section" aria-label={question}>
      <h2 className="evidence-question">{question}</h2>
      <InsightCard insight={insight} />
      <div className="evidence-body">{children}</div>
      <ClaimBoundary text={insight.cannotClaim} />
      <p className="evidence-source">Source artifact: {insight.source}</p>
    </section>
  );
}

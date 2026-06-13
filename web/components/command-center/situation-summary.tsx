import { ArrowUpRight } from "lucide-react";
import Link from "next/link";

import type { Patient } from "@/lib/types";

export function SituationSummary({ patients }: { patients: Patient[] }) {
  const total = patients.length;
  const urgent = patients.filter(
    (p) => p.triage_category === "Urgent Response Priority",
  ).length;
  const confirmatory = patients.filter(
    (p) => p.triage_category === "Confirmatory Test Priority",
  ).length;
  const uncertain = patients.filter((p) => p.uncertainty_level === "high").length;
  const testCompeting = urgent + confirmatory;

  return (
    <section className="situation" aria-labelledby="situation-heading">
      <div className="situation-main">
        <p className="situation-eyebrow" id="situation-heading">
          Situation now · {total} anonymous cases scored
        </p>
        <p className="situation-sentence">
          <strong>{urgent}</strong> cases require urgent response.{" "}
          <strong>{testCompeting}</strong> compete for confirmatory tests, and{" "}
          <strong>{uncertain}</strong> add human-review demand.
        </p>
        <Link href="/resources?preset=current" className="situation-link">
          Review current capacity
          <ArrowUpRight aria-hidden="true" size={15} />
        </Link>
      </div>
    </section>
  );
}

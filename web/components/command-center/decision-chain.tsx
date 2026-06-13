import { Activity, ChevronRight, HelpCircle, SlidersHorizontal, Stethoscope } from "lucide-react";
import Link from "next/link";

import type { Patient } from "@/lib/types";

export function DecisionChain({ patients }: { patients: Patient[] }) {
  const total = patients.length;
  const flagged = patients.filter((p) => p.uncertainty_level !== "low").length;
  const urgent = patients.filter(
    (p) => p.triage_category === "Urgent Response Priority",
  ).length;
  const eligible = patients.filter((p) =>
    ["Confirmatory Test Priority", "Urgent Response Priority"].includes(p.triage_category),
  ).length;

  const stages = [
    { icon: Activity, label: "Patient signals", value: total, detail: "cases scored" },
    { icon: HelpCircle, label: "Uncertainty gate", value: flagged, detail: "flagged for review" },
    { icon: Stethoscope, label: "Triage priority", value: urgent, detail: "urgent tier" },
  ];

  return (
    <section className="decision-chain" aria-label="Decision pipeline">
      {stages.map((stage, index) => (
        <div className="chain-node" key={stage.label}>
          <span className="chain-icon" aria-hidden="true">
            <stage.icon size={18} strokeWidth={1.9} />
          </span>
          <span className="chain-value">{stage.value}</span>
          <span className="chain-label">{stage.label}</span>
          <span className="chain-detail">{stage.detail}</span>
          {index < stages.length - 1 ? (
            <ChevronRight className="chain-arrow" aria-hidden="true" size={18} />
          ) : null}
        </div>
      ))}
      <Link href="/resources?preset=current" className="chain-node chain-node-link">
        <span className="chain-icon" aria-hidden="true">
          <SlidersHorizontal size={18} strokeWidth={1.9} />
        </span>
        <span className="chain-value">{eligible}</span>
        <span className="chain-label">Resource allocation</span>
        <span className="chain-detail">compete for tests →</span>
      </Link>
    </section>
  );
}

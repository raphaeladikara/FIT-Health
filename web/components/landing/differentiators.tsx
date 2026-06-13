import { Boxes, ShieldAlert, SplitSquareVertical, Telescope } from "lucide-react";
import type { LucideIcon } from "lucide-react";

const ITEMS: Array<{ icon: LucideIcon; title: string; body: string }> = [
  {
    icon: ShieldAlert,
    title: "Leakage-controlled by construction",
    body: "The deployable PRE_LAB track only uses information available before lab results. A FULL track is kept strictly to demonstrate how leakage inflates scores — it is never offered for real decisions.",
  },
  {
    icon: SplitSquareVertical,
    title: "Multi-label, not a forced class",
    body: "Patients can carry more than one febrile disease. VECTRA-X predicts each disease independently and reports co-infection risk instead of collapsing everyone into a single diagnosis.",
  },
  {
    icon: Boxes,
    title: "Uncertainty you can act on",
    body: "Calibrated probabilities, entropy, and conformal caution sets surface ambiguous cases. A wide caution set is an explicit request for human review, not a hidden failure.",
  },
  {
    icon: Telescope,
    title: "Generalization limits stated up front",
    body: "Leave-one-center-out testing shows where performance drops on unseen sites. Those limits are shown beside the headline numbers, not buried.",
  },
];

export function Differentiators() {
  return (
    <section className="landing-section" aria-labelledby="diff-heading">
      <h2 id="diff-heading" className="landing-section-title">
        Why this is different from a single score
      </h2>
      <div className="landing-diff">
        {ITEMS.map(({ icon: Icon, title, body }) => (
          <article className="diff-card" key={title}>
            <span className="diff-icon" aria-hidden="true">
              <Icon size={20} strokeWidth={1.9} />
            </span>
            <h3>{title}</h3>
            <p>{body}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

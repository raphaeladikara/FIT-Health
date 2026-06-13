import { ArrowRight } from "lucide-react";

const STEPS: Array<{ title: string; detail: string }> = [
  { title: "Patient signals", detail: "Demographics, symptoms, exposures, and vitals available before lab confirmation." },
  { title: "Calibrated risk", detail: "A per-disease probability for each active label, not a single forced class." },
  { title: "Uncertainty gate", detail: "Entropy and conformal caution sets flag ambiguous cases for human review." },
  { title: "Triage priority", detail: "Risk and uncertainty combine into a routine-to-urgent priority tier." },
  { title: "Resource allocation", detail: "Scarce tests and beds are assigned, with shortfalls made explicit." },
];

export function OperationalFlow() {
  return (
    <section className="landing-section landing-flow-section" aria-labelledby="flow-heading">
      <h2 id="flow-heading" className="landing-section-title">
        One decision pipeline, end to end
      </h2>
      <ol className="landing-flow">
        {STEPS.map((step, index) => (
          <li className="flow-step" key={step.title}>
            <span className="flow-index">{index + 1}</span>
            <div className="flow-body">
              <strong>{step.title}</strong>
              <p>{step.detail}</p>
            </div>
            {index < STEPS.length - 1 ? (
              <ArrowRight className="flow-arrow" aria-hidden="true" size={18} />
            ) : null}
          </li>
        ))}
      </ol>
    </section>
  );
}

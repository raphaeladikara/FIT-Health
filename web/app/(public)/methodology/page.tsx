import { PageHeader } from "@/components/ui/page-header";
import { SafetyNote } from "@/components/ui/safety-note";

const sections = [
  ["framing", "Multi-label framing"],
  ["staging", "Clinical-stage controls"],
  ["validation", "Validation strategy"],
  ["uncertainty", "Uncertainty and abstention"],
  ["limitations", "Limitations and ethics"],
] as const;

export default function MethodologyPage() {
  return (
    <>
      <PageHeader
        title="Methodology & Limitations"
        description="The operational claims, safeguards, and constraints behind the PRE_LAB decision-support system."
        aside={<SafetyNote compact />}
      />
      <div className="method-grid">
        <nav className="method-nav" aria-label="Methodology sections">
          {sections.map(([id, label]) => <a href={`#${id}`} key={id}>{label}</a>)}
        </nav>
        <article>
          <MethodSection id="framing" title="Multi-label framing">
            Patients can carry more than one vector-borne or febrile disease signal.
            The system therefore predicts each active label independently and reports
            co-infection risk instead of forcing every patient into one class.
          </MethodSection>
          <MethodSection id="staging" title="Clinical-stage controls">
            The deployable PRE_LAB track uses demographics, symptoms, exposures, and
            vitals available before laboratory confirmation. LAB_AWARE is separate,
            while FULL is retained only to demonstrate how leakage inflates performance.
          </MethodSection>
          <MethodSection id="validation" title="Validation strategy">
            Model selection uses multi-label stratified cross-validation and
            imbalance-aware metrics. Final claims come from a held-out test split,
            with per-label support, bootstrap uncertainty, and leave-one-center-out
            stress testing exposed alongside aggregate metrics.
          </MethodSection>
          <MethodSection id="uncertainty" title="Uncertainty and abstention">
            Calibrated probabilities, entropy-derived uncertainty, and conformal
            caution sets help identify ambiguous cases. A large caution set is a
            request for human review, not a failure to be hidden.
          </MethodSection>
          <MethodSection id="limitations" title="Limitations and ethics">
            The cohort is small, rare labels have limited support, and center transfer
            performance is materially lower than random held-out performance. The
            prototype has not undergone prospective clinical validation, workflow
            safety testing, or regulatory review. It must not be used as a diagnostic
            authority.
          </MethodSection>
        </article>
      </div>
    </>
  );
}

function MethodSection({
  id,
  title,
  children,
}: {
  id: string;
  title: string;
  children: string;
}) {
  return (
    <section className="prose-section" id={id}>
      <h2>{title}</h2>
      <p>{children}</p>
    </section>
  );
}

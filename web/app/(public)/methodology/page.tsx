import type { ReactNode } from "react";

import { Glossary } from "@/components/methodology/glossary";
import { MethodologyNavigation } from "@/components/methodology/methodology-navigation";
import { TermHelp } from "@/components/ui/term-help";

export const metadata = {
  title: "VECTRA-X methodology & limitations",
};

export default function MethodologyPage() {
  return (
    <div className="methodology">
      <header className="methodology-header">
        <h1>Methodology &amp; limitations</h1>
        <p>
          The operational claims, safeguards, and constraints behind the PRE_LAB
          decision-support system — written to be read at the moment of a decision.
        </p>
      </header>
      <div className="method-grid">
        <MethodologyNavigation />
        <article>
          <MethodSection id="framing" title="Multi-label framing">
            Patients can carry more than one vector-borne or febrile disease signal.
            VECTRA-X predicts each active label independently and reports co-infection
            risk instead of forcing every patient into a single class.
          </MethodSection>
          <MethodSection id="staging" title="Feature stages">
            The deployable PRE_LAB track uses only demographics, symptoms, exposures, and
            vitals available before laboratory confirmation. LAB_AWARE adds confirmatory
            inputs for a separate confirmation step; the FULL track exists{" "}
            <strong>only</strong> to demonstrate how <TermHelp slug="leakage" /> inflates
            performance and is never deployed.
          </MethodSection>
          <MethodSection id="validation" title="Validation strategy">
            Model selection uses multi-label stratified cross-validation with
            imbalance-aware metrics (<TermHelp slug="macro-f1" /> and{" "}
            <TermHelp slug="pr-auc" />). Headline claims come from a held-out test split;
            patient records shown in the workspace are{" "}
            <TermHelp slug="out-of-fold" /> predictions over the full cohort. Bootstrap
            confidence intervals and leave-one-center-out stress tests accompany every
            aggregate number.
          </MethodSection>
          <MethodSection id="thresholds" title="Per-label thresholds">
            Each disease is flagged using its own tuned decision threshold, not a single
            fixed 0.50 cutoff. The dashboard shows each threshold beside the calibrated
            probability, and the displayed prediction is regenerated from those thresholds
            so the chip, the bar, and the marker always agree. The operational policy is
            the default; safety and performance policies trade sensitivity for test load.
          </MethodSection>
          <MethodSection id="calibration" title="Calibration & conformal abstention">
            Probabilities are <TermHelp slug="calibration" />-checked with Brier score and
            expected calibration error. <TermHelp slug="entropy" />-derived uncertainty and
            a <TermHelp slug="conformal-set" /> identify ambiguous cases. A wide caution set
            is a request for human review, not a hidden failure — and conformal coverage is
            not guaranteed equally across labels.
          </MethodSection>
          <MethodSection id="coinfection" title="Co-infection detection">
            A separate detector estimates the probability that a patient carries more than
            one disease. This is distinct from how many labels happen to clear their
            thresholds, so co-infection examples are chosen by the detector score.
          </MethodSection>
          <MethodSection id="triage" title="Triage formula">
            Triage priority combines calibrated risk and uncertainty into a routine →
            clinical-review → confirmatory → urgent ranking. The score orders the queue; it
            does not authorise any action on its own.
          </MethodSection>
          <MethodSection id="resources" title="Resource assumptions">
            Resource scenarios are a transparent simulator. Demand figures (one test per
            confirmatory/urgent case, one bed per urgent case, and so on) are clinically
            unvalidated heuristics, shown in full on the resources page. Shortfalls are
            reported as non-negative unmet demand.
          </MethodSection>
          <MethodSection id="privacy" title="Privacy">
            Every record is de-identified before display or export. UUIDs, ground-truth
            labels, and raw identifiers are dropped at export time; the dashboard shows only
            anonymous case IDs.
          </MethodSection>
          <MethodSection id="provenance" title="Artifact provenance">
            Each export carries a run identity (run ID, git commit, data and config
            checksums), execution profile, evaluation mode, and per-track model versions.
            Non-canonical (development) runs are labelled as such everywhere they appear.
          </MethodSection>
          <MethodSection id="limitations" title="Limitations & ethics">
            The cohort is small, rare labels have limited support, and{" "}
            <TermHelp slug="center-transfer" /> performance is materially lower than random
            held-out performance. The prototype has not undergone prospective clinical
            validation, workflow safety testing, or regulatory review. It must never be used
            as a diagnostic authority.
          </MethodSection>
          <Glossary />
        </article>
      </div>
    </div>
  );
}

function MethodSection({
  id,
  title,
  children,
}: {
  id: string;
  title: string;
  children: ReactNode;
}) {
  return (
    <section className="prose-section" id={id}>
      <h2>{title}</h2>
      <p>{children}</p>
    </section>
  );
}

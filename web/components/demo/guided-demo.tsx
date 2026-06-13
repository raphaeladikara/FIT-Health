import { ArrowLeft, ArrowRight, ExternalLink } from "lucide-react";
import Link from "next/link";

import { CohortStep } from "@/components/demo/cohort-step";
import { DemoNavigation } from "@/components/demo/demo-navigation";
import { LeakageStep } from "@/components/demo/leakage-step";
import { PatientStep } from "@/components/demo/patient-step";
import { ResourcesStep } from "@/components/demo/resources-step";
import { UncertaintyStep } from "@/components/demo/uncertainty-step";
import { adjacentDemoSteps, demoStepHref, type DemoStep } from "@/lib/demo-steps";
import type { DashboardData } from "@/lib/types";

function StepBody({ step, data }: { step: DemoStep; data: DashboardData }) {
  switch (step.slug) {
    case "cohort":
      return <CohortStep data={data} />;
    case "leakage":
      return <LeakageStep data={data} />;
    case "patient":
      return <PatientStep data={data} />;
    case "uncertainty":
      return <UncertaintyStep data={data} />;
    case "resources":
      return <ResourcesStep data={data} />;
  }
}

export function GuidedDemo({ step, data }: { step: DemoStep; data: DashboardData }) {
  const { index, prev, next } = adjacentDemoSteps(step.slug);
  return (
    <div className="demo">
      <DemoNavigation current={step.slug} />
      <article className="demo-stage" aria-live="polite">
        <header className="demo-stage-head">
          <p className="demo-step-count">
            Step {index + 1} of 5 · {step.label}
          </p>
          <h1 className="demo-thesis">{step.thesis}</h1>
        </header>

        <StepBody step={step} data={data} />

        <Link href={step.workspaceHref} className="demo-workspace-link">
          <ExternalLink aria-hidden="true" size={15} />
          {step.workspaceLabel}
        </Link>
      </article>

      <footer className="demo-foot">
        {prev ? (
          <Link href={demoStepHref(prev.slug)} className="demo-prev">
            <ArrowLeft aria-hidden="true" size={16} />
            <span>
              <small>Previous</small>
              {prev.label}
            </span>
          </Link>
        ) : (
          <span />
        )}
        {next ? (
          <Link href={demoStepHref(next.slug)} className="demo-next">
            <span>
              <small>Next</small>
              {next.label}
            </span>
            <ArrowRight aria-hidden="true" size={16} />
          </Link>
        ) : (
          <Link href="/command-center" className="demo-next">
            <span>
              <small>Finish</small>
              Open command center
            </span>
            <ArrowRight aria-hidden="true" size={16} />
          </Link>
        )}
      </footer>
    </div>
  );
}

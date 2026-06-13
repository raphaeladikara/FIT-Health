import { Check } from "lucide-react";
import Link from "next/link";

import { DEMO_STEPS, demoStepHref, type DemoStepSlug } from "@/lib/demo-steps";

/** Top progress rail — every step is a shareable link, so browser history works. */
export function DemoNavigation({ current }: { current: DemoStepSlug }) {
  const currentIndex = DEMO_STEPS.findIndex((step) => step.slug === current);
  return (
    <nav className="demo-rail" aria-label="Guided demo steps">
      <ol className="demo-rail-list">
        {DEMO_STEPS.map((step, index) => {
          const state =
            index === currentIndex ? "current" : index < currentIndex ? "done" : "todo";
          return (
            <li key={step.slug} className="demo-rail-item" data-state={state}>
              <Link
                href={demoStepHref(step.slug)}
                aria-current={state === "current" ? "step" : undefined}
                className="demo-rail-link"
              >
                <span className="demo-rail-index" aria-hidden="true">
                  {state === "done" ? <Check size={13} strokeWidth={3} /> : index + 1}
                </span>
                <span className="demo-rail-label">{step.label}</span>
              </Link>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

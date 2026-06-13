export const DEMO_STEPS = [
  {
    slug: "cohort",
    label: "Cohort reality",
    thesis: "Most patients are not a single clean disease.",
    workspaceHref: "/command-center",
    workspaceLabel: "Open the live command center",
  },
  {
    slug: "leakage",
    label: "Leakage trap",
    thesis: "A leaked feature makes a useless model look excellent.",
    workspaceHref: "/evidence?section=leakage",
    workspaceLabel: "See the leakage evidence",
  },
  {
    slug: "patient",
    label: "Patient decision",
    thesis: "Each disease is judged against its own tuned threshold.",
    workspaceHref: "/patients",
    workspaceLabel: "Open patient review",
  },
  {
    slug: "uncertainty",
    label: "Ambiguous case",
    thesis: "When the model is unsure, it asks for a human — loudly.",
    workspaceHref: "/patients?scenario=high-uncertainty",
    workspaceLabel: "Open an ambiguous case",
  },
  {
    slug: "resources",
    label: "Resource consequence",
    thesis: "A risk score only matters once it meets scarce capacity.",
    workspaceHref: "/resources?preset=current",
    workspaceLabel: "Open resource scenarios",
  },
] as const;

export type DemoStep = (typeof DEMO_STEPS)[number];
export type DemoStepSlug = DemoStep["slug"];

export function resolveDemoStep(slug: string | undefined | null): DemoStep {
  return DEMO_STEPS.find((step) => step.slug === slug) ?? DEMO_STEPS[0];
}

export function adjacentDemoSteps(slug: string): {
  index: number;
  prev: DemoStep | null;
  next: DemoStep | null;
} {
  const found = DEMO_STEPS.findIndex((step) => step.slug === slug);
  const index = found < 0 ? 0 : found;
  return {
    index,
    prev: index > 0 ? DEMO_STEPS[index - 1] : null,
    next: index < DEMO_STEPS.length - 1 ? DEMO_STEPS[index + 1] : null,
  };
}

export function demoStepHref(slug: string): string {
  return `/demo?step=${slug}`;
}

import { describe, expect, it } from "vitest";

import {
  adjacentDemoSteps,
  demoStepHref,
  DEMO_STEPS,
  resolveDemoStep,
} from "@/lib/demo-steps";

describe("demo steps", () => {
  it("has the five judge-demo steps in order", () => {
    expect(DEMO_STEPS.map((step) => step.slug)).toEqual([
      "cohort",
      "leakage",
      "patient",
      "uncertainty",
      "resources",
    ]);
  });

  it("falls back to cohort when the step is invalid", () => {
    expect(resolveDemoStep("unknown").slug).toBe("cohort");
    expect(resolveDemoStep(undefined).slug).toBe("cohort");
  });

  it("returns adjacent steps", () => {
    const around = adjacentDemoSteps("patient");
    expect(around.prev?.slug).toBe("leakage");
    expect(around.next?.slug).toBe("uncertainty");
    expect(adjacentDemoSteps("cohort").prev).toBeNull();
    expect(adjacentDemoSteps("resources").next).toBeNull();
  });

  it("builds shareable step hrefs", () => {
    expect(demoStepHref("uncertainty")).toBe("/demo?step=uncertainty");
  });
});

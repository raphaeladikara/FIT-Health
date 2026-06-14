import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ResourceWorkspace } from "@/components/resources/resource-workspace";
import { RESOURCE_PRESETS } from "@/lib/resource-presets";
import type { Patient, TriageCategory } from "@/lib/types";

function patient(i: number, category: TriageCategory): Patient {
  return {
    case_id: `Case ${String(i).padStart(3, "0")}`,
    predicted_labels: "{malaria}",
    conformal_set: "{malaria}",
    coinfection_prob: 0.3,
    uncertainty_level: "low",
    triage_score: 1 - i / 1000,
    triage_category: category,
    recommended_action: "Review.",
    label_decisions: {},
    model_track: "PRE_LAB",
    threshold_policy: "operational",
    record_source: "full_cohort_oof",
  };
}

// 60 confirmatory + 20 urgent + 20 routine = 100 cases.
const patients: Patient[] = [
  ...Array.from({ length: 60 }, (_, i) => patient(i + 1, "Confirmatory Test Priority")),
  ...Array.from({ length: 20 }, (_, i) => patient(i + 61, "Urgent Response Priority")),
  ...Array.from({ length: 20 }, (_, i) => patient(i + 81, "Routine Monitoring")),
];

function renderWorkspace(preset?: string) {
  return render(
    <ResourceWorkspace patients={patients} policyTradeoff={[]} initialPreset={preset} />,
  );
}

describe("resource workspace", () => {
  it("loads the safety-first preset when selected", () => {
    renderWorkspace();
    fireEvent.click(screen.getByRole("button", { name: "Safety-first", pressed: false }));
    const testsNumber = screen.getByLabelText(/^Rapid tests \(tests\)$/) as HTMLInputElement;
    expect(Number(testsNumber.value)).toBe(RESOURCE_PRESETS.safety.capacity.rapidTests);
  });

  it("keeps the number field and slider synchronized", () => {
    renderWorkspace();
    const number = screen.getByLabelText(/^Rapid tests \(tests\)$/) as HTMLInputElement;
    const slider = screen.getByLabelText("Rapid tests slider") as HTMLInputElement;
    fireEvent.change(number, { target: { value: "12" } });
    expect(slider.value).toBe("12");
    fireEvent.change(slider, { target: { value: "34" } });
    expect(number.value).toBe("34");
  });

  it("reset restores the active preset", () => {
    renderWorkspace();
    const number = screen.getByLabelText(/^Rapid tests \(tests\)$/) as HTMLInputElement;
    fireEvent.change(number, { target: { value: "5" } });
    fireEvent.click(screen.getByRole("button", { name: /Reset to/i }));
    expect(Number(number.value)).toBe(RESOURCE_PRESETS.current.capacity.rapidTests);
  });

  it("never shows a negative shortfall and labels ineligible cases", () => {
    renderWorkspace("severeShortage");
    const ledger = screen.getByText("Capacity ledger").closest("section") as HTMLElement;
    const shortfalls = within(ledger)
      .getAllByRole("cell")
      .map((cell) => Number(cell.textContent))
      .filter((n) => Number.isFinite(n));
    expect(shortfalls.every((n) => n >= 0)).toBe(true);
    // Routine cases are not eligible for a test.
    expect(screen.getAllByText("Not eligible").length).toBeGreaterThan(0);
  });

  it("compares allocated and waitlisted against the current baseline", () => {
    renderWorkspace("safety");
    const compare = screen.getByText("Scenario vs current capacity").closest("section") as HTMLElement;
    expect(within(compare).getByText("Tests allocated")).toBeVisible();
    expect(within(compare).getByText("Eligible waitlisted")).toBeVisible();
  });

  it("shows demand assumptions without hover", () => {
    renderWorkspace();
    expect(screen.getByText(/One rapid test per confirmatory/i)).toBeVisible();
  });
});

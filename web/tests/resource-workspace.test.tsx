import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ResourceWorkspace } from "@/components/resources/resource-workspace";
import type { Patient } from "@/lib/types";

const patients = [
  {
    case_id: "Case 001",
    predicted_labels: "{malaria}",
    conformal_set: "{malaria}",
    coinfection_prob: 0.4,
    uncertainty_level: "high",
    triage_score: 0.9,
    triage_category: "Urgent Response Priority",
    recommended_action: "Escalate.",
  },
  {
    case_id: "Case 002",
    predicted_labels: "{dengue}",
    conformal_set: "{dengue}",
    coinfection_prob: 0.7,
    uncertainty_level: "moderate",
    triage_score: 0.7,
    triage_category: "Confirmatory Test Priority",
    recommended_action: "Test.",
  },
] satisfies Patient[];

describe("resource workspace", () => {
  it("updates rapid-test capacity and eligible waiting count", () => {
    render(<ResourceWorkspace patients={patients} policyTradeoff={[]} />);

    fireEvent.change(screen.getByLabelText("Rapid tests"), {
      target: { value: "0" },
    });

    expect(screen.getByText("0 available")).toBeVisible();
    expect(
      screen.getByText(/2 eligible cases remain outside the current rapid-test allocation/),
    ).toBeVisible();
  });
});

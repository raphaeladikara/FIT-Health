import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { CommandCenter } from "@/components/command-center/command-center";
import { TriageQueue } from "@/components/command-center/triage-queue";
import type { Manifest, Patient, TriageCategory } from "@/lib/types";

function patient(i: number, category: TriageCategory): Patient {
  return {
    case_id: `Case ${String(i).padStart(3, "0")}`,
    predicted_labels: "{malaria}",
    conformal_set: "{malaria}",
    coinfection_prob: 0.1,
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

// 40 urgent + 10 routine = 50 cases (forces pagination at size 25).
const patients: Patient[] = [
  ...Array.from({ length: 40 }, (_, i) => patient(i + 1, "Urgent Response Priority")),
  ...Array.from({ length: 10 }, (_, i) => patient(i + 41, "Routine Monitoring")),
];

const manifest = {
  schema_version: 2,
  run_id: "20260614-abcd1234-deadbeef-cafebabe",
  git_commit: "abcd1234",
  data_checksum: "deadbeef",
  config_checksum: "cafebabe",
  generated_at: "2026-06-14T00:00:00Z",
  execution_profile: "quick_smoke",
  canonical: false,
  evaluation_mode: "held_out",
  threshold_policy: "operational",
  model_versions: { PRE_LAB: "extra_trees" },
  patient_count: 50,
  active_labels: ["malaria"],
  available_evidence: [],
  warnings: [],
} as Manifest;

describe("triage queue", () => {
  it("paginates at 25 per page and keeps filters across pages", () => {
    render(<TriageQueue patients={patients} />);
    // 50 cases -> page 1 shows 25 rows.
    expect(document.querySelectorAll("tbody tr")).toHaveLength(25);
    expect(screen.getByText(/Showing 1–25 of 50 cases/)).toBeVisible();

    // Filter to routine (10 cases) -> single page, count reflects filter.
    fireEvent.change(screen.getByLabelText("Priority tier"), {
      target: { value: "Routine Monitoring" },
    });
    expect(document.querySelectorAll("tbody tr")).toHaveLength(10);
    expect(screen.getByText(/of 10 cases/)).toBeVisible();
  });

  it("shows an empty state and restores results on clear filters", () => {
    render(<TriageQueue patients={patients} />);
    fireEvent.change(screen.getByLabelText("Search cases"), {
      target: { value: "no-such-case-xyz" },
    });
    expect(screen.getByText("No matching cases")).toBeVisible();

    fireEvent.click(screen.getAllByRole("button", { name: /Clear filters/i })[0]);
    expect(document.querySelectorAll("tbody tr")).toHaveLength(25);
  });
});

describe("command center", () => {
  it("surfaces a data-generated situation sentence and provenance warning", () => {
    render(<CommandCenter patients={patients} manifest={manifest} />);
    expect(screen.getByText(/cases require urgent response/i)).toBeVisible();
    // Non-canonical artifact warning is shown in the provenance panel.
    expect(screen.getByText(/Development artifact: quick_smoke/i)).toBeVisible();
  });

  it("links the situation summary to current resource capacity", () => {
    render(<CommandCenter patients={patients} manifest={manifest} />);
    expect(
      within(document.querySelector(".situation") as HTMLElement).getByRole("link", {
        name: /Review current capacity/i,
      }),
    ).toHaveAttribute("href", "/resources?preset=current");
  });
});

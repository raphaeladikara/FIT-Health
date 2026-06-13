import type { Patient } from "@/lib/types";

export type RepresentativeScenario =
  | "highest-priority"
  | "high-uncertainty"
  | "co-infection"
  | "routine";

export function parseLabelSet(value: string): string[] {
  const content = value.trim().replace(/^\{|\}$/g, "");
  if (!content || content.toLowerCase() === "none") return [];
  return content
    .split(",")
    .map((label) => label.trim())
    .filter(Boolean);
}

export function selectRepresentativePatient(
  patients: Patient[],
  scenario: RepresentativeScenario,
): Patient | undefined {
  const sorted = [...patients].sort((a, b) => b.triage_score - a.triage_score);
  if (scenario === "high-uncertainty") {
    return sorted.find((patient) => patient.uncertainty_level === "high");
  }
  if (scenario === "co-infection") {
    // The co-infection detector is a separate risk signal, distinct from how many
    // labels happen to clear their thresholds. Pick the strongest detector score.
    return [...patients].sort(
      (a, b) =>
        b.coinfection_prob - a.coinfection_prob ||
        b.triage_score - a.triage_score,
    )[0];
  }
  if (scenario === "routine") {
    return sorted.find((patient) => patient.triage_category === "Routine Monitoring");
  }
  return sorted[0];
}

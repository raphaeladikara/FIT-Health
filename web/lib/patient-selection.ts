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
    return sorted.find((patient) => parseLabelSet(patient.predicted_labels).length > 1);
  }
  if (scenario === "routine") {
    return sorted.find((patient) => patient.triage_category === "Routine Monitoring");
  }
  return sorted[0];
}

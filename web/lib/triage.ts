import type { TriageCategory } from "@/lib/types";

/** Severity tone per triage tier — mirrors the CSS severity ramp. */
export const TRIAGE_TONE: Record<TriageCategory, string> = {
  "Urgent Response Priority": "urgent",
  "Confirmatory Test Priority": "confirm",
  "Clinical Review": "review",
  "Routine Monitoring": "routine",
};

/** Severity-descending order for charts and ledgers. */
export const TRIAGE_ORDER: TriageCategory[] = [
  "Urgent Response Priority",
  "Confirmatory Test Priority",
  "Clinical Review",
  "Routine Monitoring",
];

/** Short tier label for compact chart axes. */
export const TRIAGE_SHORT: Record<TriageCategory, string> = {
  "Urgent Response Priority": "Urgent",
  "Confirmatory Test Priority": "Test",
  "Clinical Review": "Review",
  "Routine Monitoring": "Routine",
};

export function triageTone(category: string): string {
  return TRIAGE_TONE[category as TriageCategory] ?? "neutral";
}

/** Anonymous, non-identifying token from a generated case id (e.g. "Case 042" → "042"). */
export function caseToken(caseId: string): string {
  const digits = caseId.match(/\d+/)?.[0];
  if (digits) return digits;
  return caseId.replace(/[^A-Za-z0-9]/g, "").slice(-3).toUpperCase() || "—";
}

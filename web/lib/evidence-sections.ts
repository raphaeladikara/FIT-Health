export const EVIDENCE_SECTIONS = [
  { slug: "performance", label: "Discrimination", question: "How well does it discriminate?" },
  { slug: "missed-cases", label: "Missed cases", question: "Which cases does it miss?" },
  { slug: "calibration", label: "Calibration", question: "Can I trust the probabilities?" },
  { slug: "abstention", label: "Abstention", question: "When does it ask for help?" },
  { slug: "generalization", label: "Generalization", question: "Does it transfer to new centers?" },
  { slug: "leakage", label: "Leakage control", question: "Is the score honest?" },
] as const;

export type EvidenceSectionSlug = (typeof EVIDENCE_SECTIONS)[number]["slug"];

export function resolveEvidenceSection(slug: string | undefined | null) {
  return (
    EVIDENCE_SECTIONS.find((section) => section.slug === slug) ?? EVIDENCE_SECTIONS[0]
  );
}

export function evidenceSectionHref(slug: string): string {
  return `/evidence?section=${slug}`;
}

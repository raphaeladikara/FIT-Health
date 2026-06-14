export const GLOSSARY = {
  "macro-f1": {
    term: "Macro F1",
    definition:
      "The average F1 score across diseases, giving each disease equal weight regardless of how common it is.",
  },
  "pr-auc": {
    term: "PR-AUC",
    definition:
      "Area under the precision–recall curve — a ranking quality measure that stays meaningful when positive cases are rare.",
  },
  calibration: {
    term: "Calibration",
    definition:
      "How closely predicted probabilities match real-world frequencies, so a 70% prediction is right about 70% of the time.",
  },
  entropy: {
    term: "Entropy",
    definition:
      "A measure of how spread out the predicted probabilities are; higher entropy means the model is more uncertain.",
  },
  "conformal-set": {
    term: "Conformal caution set",
    definition:
      "The set of diseases kept in play with a statistical coverage guarantee; a wider set signals more uncertainty and a request for human review.",
  },
  leakage: {
    term: "Diagnostic leakage",
    definition:
      "Information unavailable at the intended decision time that reveals or restates the outcome, inflating apparent performance.",
  },
  "center-transfer": {
    term: "Center transfer",
    definition:
      "How well a model trained on some health centers performs on a different, unseen center — a test of real generalization.",
  },
  "out-of-fold": {
    term: "Out-of-fold prediction",
    definition:
      "A prediction made for a record by a model that never trained on it, produced during cross-validation to avoid optimistic bias.",
  },
} as const;

export type GlossarySlug = keyof typeof GLOSSARY;

export function glossaryEntry(slug: string) {
  return (GLOSSARY as Record<string, { term: string; definition: string }>)[slug];
}

export function glossaryAnchor(slug: string): string {
  return `/methodology#glossary-${slug}`;
}

import { titleCase } from "@/lib/format";
import type { EvidenceInsight, EvidenceRecord } from "@/lib/types";

const RARE_LABELS = ["dengue", "typhoid", "yellow_fever"];

function pct(value: number, digits = 1): string {
  return `${(value * 100).toFixed(digits)}%`;
}

/** Headline discrimination, framed with its bootstrap confidence interval. */
export function performanceInsight(
  macroF1: number,
  interval: [number, number],
): EvidenceInsight {
  return {
    title: "Discrimination is moderate, with wide uncertainty",
    summary: `Held-out macro F1 is ${macroF1.toFixed(2)} (95% CI ${interval[0].toFixed(
      2,
    )}–${interval[1].toFixed(2)}).`,
    implication:
      "The interval is wide because the cohort is small, so the headline number should be read as a range, not a point.",
    cannotClaim:
      "We cannot claim a precise macro F1 — only that it plausibly falls inside this interval.",
    severity: "neutral",
    source: "headline_metric_bootstrap_ci",
  };
}

/** Missed-case safety: the rare label with the weakest support / recall. */
export function missedCaseInsight(perLabel: EvidenceRecord[]): EvidenceInsight {
  const preLab = perLabel.filter((row) => row.track === "PRE_LAB");
  const weakest = [...preLab].sort(
    (a, b) => Number(a.support_pos ?? 0) - Number(b.support_pos ?? 0),
  )[0];
  const label = weakest ? titleCase(String(weakest.label)) : "the rarest label";
  const support = weakest ? Number(weakest.support_pos ?? 0) : 0;
  return {
    title: "Missed cases concentrate in rare diseases",
    summary: `${label} has only ${support} positive cases in the held-out split, so its recall estimate is unstable.`,
    implication:
      "A high recall on a handful of positives is not yet evidence of safety for that disease.",
    cannotClaim:
      "We cannot claim reliable sensitivity for low-support diseases from this cohort.",
    severity: support <= 5 ? "warning" : "neutral",
    source: "per_label_metrics",
  };
}

/** Per-label conformal coverage against the intended guarantee. */
export function conformalInsight(
  row: EvidenceRecord,
  target = 0.9,
): EvidenceInsight {
  const coverage = Number(row.empirical_coverage);
  const label = String(row.label ?? "label");
  const under = coverage < target;
  return {
    title: `${titleCase(label)} conformal coverage`,
    summary: `Empirical coverage for ${label} is ${pct(coverage)} against a ${(
      target * 100
    ).toFixed(0)}% target${under ? " — below target." : "."}`,
    implication: under
      ? "The caution set misses the true label more often than the conformal guarantee promises."
      : "Coverage meets the intended guarantee on the held-out split.",
    cannotClaim: under
      ? `We cannot claim calibrated ${(target * 100).toFixed(0)}% coverage for ${label}.`
      : `Coverage is only validated on this small held-out split.`,
    severity: under ? "warning" : "neutral",
    source: "conformal_metrics",
  };
}

/** Generalization stress test: recall that collapses on unseen centers. */
export function centerTransferInsight(rows: EvidenceRecord[]): EvidenceInsight {
  const allRareZero = RARE_LABELS.every((label) =>
    rows.every((row) => Number(row[`recall_${label}`]) === 0),
  );
  const centerWord = rows.length === 2 ? "both" : `all ${rows.length}`;
  const macroF1s = rows.map((row) => Number(row.macro_f1)).filter(Number.isFinite);
  const worst = macroF1s.length ? Math.min(...macroF1s) : 0;
  const limitations: string[] = [];
  if (allRareZero) {
    limitations.push(`Rare-label recall is zero in ${centerWord} held-out centers`);
  }
  return {
    title: "Performance drops sharply on unseen centers",
    summary: `Leave-one-center-out macro F1 falls to ${worst.toFixed(
      2,
    )}, far below random held-out performance.`,
    implication:
      "The model has partly learned center-specific patterns; it does not yet transfer to new sites.",
    cannotClaim:
      "We cannot claim the model generalizes to centers it was not trained on.",
    severity: allRareZero ? "critical" : "warning",
    source: "center_transfer",
    limitations,
  };
}

/** Leakage demonstration: how much the research-only FULL track inflates results. */
export function leakageInsight(preLab: number, full: number): EvidenceInsight {
  const gap = full - preLab;
  return {
    title: "Leakage would inflate the score, so it is excluded",
    summary: `The research-only FULL track scores ${full.toFixed(
      2,
    )} macro F1 vs ${preLab.toFixed(2)} for the deployable PRE_LAB track (+${gap.toFixed(2)}).`,
    implication:
      "The gain comes from features unavailable at decision time. Only PRE_LAB is deployable.",
    cannotClaim:
      "We cannot present FULL-track numbers as achievable triage performance.",
    severity: "warning",
    source: "model_leaderboard",
  };
}

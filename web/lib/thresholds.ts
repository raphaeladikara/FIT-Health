/** A single disease detector's calibrated decision against its tuned threshold. */
export type LabelDecision = {
  probability: number;
  threshold: number;
  predicted: boolean;
};

/**
 * The deployment decision rule: a label is flagged when its calibrated probability
 * reaches its tuned threshold. There is no fixed 0.50 cutoff — each disease uses its
 * own exported threshold.
 */
export function decisionForProbability({
  probability,
  threshold,
}: Pick<LabelDecision, "probability" | "threshold">): boolean {
  return probability >= threshold;
}

/** Position (0–100%) of the threshold marker on a probability track. */
export function thresholdMarkerPercent(threshold: number): number {
  return Math.min(100, Math.max(0, threshold * 100));
}

/** Labels a patient is flagged for, ordered by how far each clears its threshold. */
export function flaggedLabels(
  decisions: Record<string, LabelDecision>,
): string[] {
  return Object.entries(decisions)
    .filter(([, decision]) => decision.predicted)
    .sort(
      (a, b) =>
        b[1].probability - b[1].threshold - (a[1].probability - a[1].threshold),
    )
    .map(([label]) => label);
}

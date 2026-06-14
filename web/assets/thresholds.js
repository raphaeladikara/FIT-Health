export function isPositive(probability, label, thresholds) {
  const threshold = thresholds?.values?.[label];
  if (!Number.isFinite(threshold)) {
    throw new Error(`Missing operational threshold for ${label}`);
  }
  return Number(probability) >= threshold;
}

export function decisionLabel(probability, label, thresholds) {
  return isPositive(probability, label, thresholds)
    ? "Above decision threshold"
    : "Below decision threshold";
}

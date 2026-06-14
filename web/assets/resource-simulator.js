function requireNonNegative(name, value) {
  if (!Number.isFinite(value) || value < 0) {
    throw new Error(`${name} must be a non-negative number`);
  }
}

export function simulateResources({
  cohortSize,
  baseCohortSize,
  tierRates,
  testRate,
  testCapacity,
  urgentCapacity,
}) {
  [
    ["cohortSize", cohortSize],
    ["baseCohortSize", baseCohortSize],
    ["testRate", testRate],
    ["testCapacity", testCapacity],
    ["urgentCapacity", urgentCapacity],
  ].forEach(([name, value]) => requireNonNegative(name, value));

  if (baseCohortSize === 0) {
    throw new Error("baseCohortSize must be greater than zero");
  }

  const rates = ["routine", "review", "priority", "urgent"];
  rates.forEach((name) => requireNonNegative(`tierRates.${name}`, tierRates?.[name]));

  const tierCounts = Object.fromEntries(
    rates.map((name) => [name, Math.round(tierRates[name] * cohortSize)]),
  );
  const testsNeeded = Math.round(testRate * cohortSize);
  const urgentNeeded = Math.round(tierRates.urgent * cohortSize);

  return {
    tierCounts,
    testsNeeded,
    unmetTests: Math.max(0, testsNeeded - testCapacity),
    urgentNeeded,
    unmetUrgent: Math.max(0, urgentNeeded - urgentCapacity),
    scale: cohortSize / baseCohortSize,
  };
}

import test from "node:test";
import assert from "node:assert/strict";

import { simulateResources } from "../assets/resource-simulator.js";

const baseline = {
  cohortSize: 300,
  baseCohortSize: 300,
  tierRates: { routine: 0.22, review: 0.29, priority: 0.2933, urgent: 0.1967 },
  testRate: 0.2933,
  testCapacity: 70,
  urgentCapacity: 40,
};

test("calculates unmet demand at constrained capacity", () => {
  assert.deepEqual(simulateResources(baseline), {
    tierCounts: { routine: 66, review: 87, priority: 88, urgent: 59 },
    testsNeeded: 88,
    unmetTests: 18,
    urgentNeeded: 59,
    unmetUrgent: 19,
    scale: 1,
  });
});

test("never reports negative unmet demand", () => {
  const result = simulateResources({
    ...baseline,
    testCapacity: 100,
    urgentCapacity: 100,
  });
  assert.equal(result.unmetTests, 0);
  assert.equal(result.unmetUrgent, 0);
});

test("scales deterministically and rejects negative input", () => {
  assert.equal(simulateResources({ ...baseline, cohortSize: 150 }).testsNeeded, 44);
  assert.throws(
    () => simulateResources({ ...baseline, cohortSize: -1 }),
    /non-negative/,
  );
});

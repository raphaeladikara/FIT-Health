import test from "node:test";
import assert from "node:assert/strict";

import { isPositive } from "../assets/thresholds.js";

const thresholds = {
  policy: "operational",
  values: {
    malaria: 0.05,
    other_diseases: 0.5,
    dengue: 0.35,
    typhoid: 0.5,
    yellow_fever: 0.1,
  },
};

test("operational threshold policy matches the published clinical policy", () => {
  assert.equal(thresholds.values.malaria, 0.05);
  assert.equal(thresholds.values.dengue, 0.35);
  assert.equal(thresholds.values.typhoid, 0.5);
  assert.equal(thresholds.values.yellow_fever, 0.1);
});

test("prediction state uses the label-specific threshold", () => {
  assert.equal(isPositive(0.2, "malaria", thresholds), true);
  assert.equal(isPositive(0.2, "dengue", thresholds), false);
  assert.equal(isPositive(0.1, "yellow_fever", thresholds), true);
});

test("missing thresholds fail loudly", () => {
  assert.throws(
    () => isPositive(0.8, "unknown", thresholds),
    /Missing operational threshold/,
  );
});

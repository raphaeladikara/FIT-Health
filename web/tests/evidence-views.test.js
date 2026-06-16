import assert from "node:assert/strict";
import test from "node:test";

import { aggregateMetricRows } from "../assets/evidence-views.js";


test("executive metrics come from aggregate frozen-test results", () => {
  const bundle = {
    evidence: {
      validation_and_frozen_test: {
        frozen_test: [{
          track: "PRE_LAB",
          macro_f1: 0.476,
          micro_f1: 0.756,
          macro_pr_auc: 0.539,
          macro_recall: 0.506,
        }],
      },
    },
  };
  assert.deepEqual(aggregateMetricRows(bundle), [
    { metric: "Macro-F1", estimate: 0.476, source: "Frozen test · PRE_LAB" },
    { metric: "Micro-F1", estimate: 0.756, source: "Frozen test · PRE_LAB" },
    { metric: "Macro PR-AUC", estimate: 0.539, source: "Frozen test · PRE_LAB" },
    { metric: "Macro recall", estimate: 0.506, source: "Frozen test · PRE_LAB" },
  ]);
});

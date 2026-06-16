import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync } from "node:fs";

import {
  aggregateMetricRows,
  evaluationEvidence,
  executiveEvidence,
  fairnessEvidence,
  governanceEvidence,
  limitationsEvidence,
  uncertaintyEvidence,
} from "../assets/evidence-views.js";

const here = new URL(".", import.meta.url);
const loadJson = (name) =>
  JSON.parse(readFileSync(new URL(`../data/${name}`, here), "utf8"));
const realBundle = () => ({
  manifest: loadJson("manifest.json"),
  evidence: loadJson("evidence.json"),
});


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


test("every evidence view renders from the real bundle without throwing", () => {
  const bundle = realBundle();
  for (const render of [
    () => executiveEvidence(bundle),
    () => governanceEvidence(bundle),
    () => evaluationEvidence(bundle, "PRE_LAB"),
    () => evaluationEvidence(bundle, "LAB_AWARE"),
    () => uncertaintyEvidence(bundle),
    () => fairnessEvidence(bundle),
    () => limitationsEvidence(bundle),
  ]) {
    const html = render();
    assert.equal(typeof html, "string");
    assert.ok(html.length > 0);
    assert.ok(!html.includes("undefined"), "view must not leak undefined into markup");
    assert.ok(!html.includes("NaN"), "view must not leak NaN into markup");
  }
});


test("per-label scorecard is internally consistent and flags evidence-limited labels", () => {
  const bundle = realBundle();
  const html = evaluationEvidence(bundle, "PRE_LAB");
  // Full scorecard columns are present.
  for (const heading of ["Positives", "TP", "FP", "FN", "Precision", "Recall", "F1", "PR-AUC", "Evidence status"]) {
    assert.ok(html.includes(`<th>${heading}</th>`), `missing column: ${heading}`);
  }
  // Rare labels are explicitly flagged rather than read as confident.
  assert.ok(html.includes("Insufficient support"), "yellow fever (3 positives) must be flagged");
  assert.ok(html.includes("Evidence-limited"), "typhoid (7 positives) must be flagged");
});


test("center-transfer view shows real LOCO macro-F1, never a zero placeholder", () => {
  const bundle = realBundle();
  const html = fairnessEvidence(bundle);
  const summary = bundle.evidence.center_transfer_summary;
  // The headline range is the real evidence, not 0.
  assert.ok(html.includes(summary.macro_f1_min.toFixed(3)));
  assert.ok(html.includes(summary.macro_f1_max.toFixed(3)));
  assert.ok(html.includes("descriptive, not causal"));
  assert.ok(html.includes("Local validation gate"));
  // No center row renders a 0.000 macro-F1 (the old confusing state).
  assert.ok(!html.includes("<td>0.000</td>"));
});


test("deployment gates render a spaced 'Pending' badge, not a run-together label", () => {
  const bundle = realBundle();
  const html = limitationsEvidence(bundle);
  assert.ok(html.includes("Safe current use"));
  assert.ok(/<span class="tag tag-warn">Pending<\/span><strong>/.test(html));
  assert.ok(!html.includes("PendingExternal"));
});

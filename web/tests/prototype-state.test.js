import assert from "node:assert/strict";
import test from "node:test";

import {
  assessmentToProjection,
  capacityStatus,
  evidenceLimitedWarnings,
  inputCompleteness,
  parsePrototypeState,
  serializePrototypeState,
} from "../assets/prototype-state.js";


test("prototype URL state is deterministic and rejects unknown stages", () => {
  assert.deepEqual(
    parsePrototypeState("?case=SYNTH-MISSING&stage=decision"),
    { caseId: "SYNTH-MISSING", stage: "decision" },
  );
  assert.deepEqual(
    parsePrototypeState("?case=SYNTH-OOD&stage=unknown"),
    { caseId: "SYNTH-OOD", stage: "intake" },
  );
  assert.equal(
    serializePrototypeState({ caseId: "SYNTH-LOW-UNCERTAINTY", stage: "assessment" }),
    "?case=SYNTH-LOW-UNCERTAINTY&stage=assessment",
  );
});


test("response projection scales a cohort by demonstration-state rates, not one case's 0/1 outcome", () => {
  const projection = assessmentToProjection(
    {
      decisions: {
        malaria: true,
        other_diseases: false,
        dengue: true,
        typhoid: false,
        yellow_fever: false,
      },
      abstention: { required: true },
      triage_category: "Clinical review required",
      uncertainty: { category: "high" },
    },
    {
      cohortSize: 100,
      reviewCapacity: 40,
      testCapacity: 20,
      urgentCapacity: 10,
    },
  );

  assert.equal(projection.interpretation, "scenario projection; not measured clinical impact");
  // A 100-patient cohort must NOT report 100 of everything — demand is a fraction of the cohort.
  assert.equal(projection.reviewNeeded, 46);
  assert.equal(projection.testsNeeded, 24);
  assert.equal(projection.urgentNeeded, 22);
  assert.equal(projection.uncertaintyNeeded, 31);

  const [review, test, urgent] = projection.categories;
  assert.equal(review.demand, 46);
  assert.equal(review.capacity, 40);
  assert.equal(review.gap, 6);
  assert.equal(review.status, "over-capacity");

  assert.equal(test.gap, 4);
  assert.equal(test.status, "over-capacity");

  assert.equal(urgent.status, "over-capacity");
  assert.equal(projection.highUncertainty.demand, 31);
});


test("capacity status reports headroom, near-limit, and over-capacity", () => {
  assert.equal(capacityStatus(46, 40).status, "over-capacity");
  assert.equal(capacityStatus(38, 40).status, "near-limit");
  assert.equal(capacityStatus(20, 40).status, "within-capacity");
  // Zero capacity is always over-capacity, with the full demand as the gap.
  assert.deepEqual(capacityStatus(46, 0), { capacity: 0, gap: 46, status: "over-capacity" });
});


test("input completeness counts only fields available in the selected mode", () => {
  const schema = {
    fields: [
      { field_id: "age", stage: "PRE_LAB" },
      { field_id: "fever", stage: "PRE_LAB" },
      { field_id: "platelets", stage: "LAB_AWARE" },
    ],
  };
  assert.deepEqual(
    inputCompleteness(schema, "PRE_LAB", { age: 12, fever: "", platelets: 99 }),
    { completed: 1, total: 2, fraction: 0.5 },
  );
});


test("rare-label warnings remain visible even below the released threshold", () => {
  const warnings = evidenceLimitedWarnings({
    typhoid: { frozen_support: 7, recall: 0.43 },
    yellow_fever: { frozen_support: 3, recall: 0 },
  });
  assert.deepEqual(warnings.map((item) => item.label), ["typhoid", "yellow_fever"]);
  assert.match(warnings[1].message, /cannot rule out/i);
});

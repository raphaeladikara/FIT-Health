import assert from "node:assert/strict";
import test from "node:test";

import {
  assessmentToProjection,
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


test("assessment output becomes an assumption-bound response projection", () => {
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
      testCapacity: 20,
      urgentCapacity: 10,
    },
  );

  assert.equal(projection.interpretation, "scenario projection; not measured clinical impact");
  assert.equal(projection.testsNeeded, 100);
  assert.equal(projection.unmetTests, 80);
  assert.equal(projection.reviewNeeded, 100);
  assert.equal(projection.urgentNeeded, 100);
  assert.equal(projection.unmetUrgent, 90);
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

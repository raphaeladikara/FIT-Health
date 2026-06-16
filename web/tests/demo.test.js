import assert from "node:assert/strict";
import test from "node:test";

import { prototypeAssessmentHref } from "../assets/demo.js";


test("guided demo opens the selected case in the live prototype assessment stage", () => {
  assert.equal(
    prototypeAssessmentHref("SYNTH-MISSING"),
    "prototype.html?case=SYNTH-MISSING&stage=assessment",
  );
});

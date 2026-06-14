import assert from "node:assert/strict";
import test from "node:test";

import {
  fieldsForMode,
  serializeAssessment,
  validateFormValues,
} from "../assets/schema-form.js";


const schema = {
  fields: [
    { field_id: "age", type: "number", stage: "PRE_LAB", required: true },
    { field_id: "platelets", type: "number", stage: "LAB_AWARE", required: false },
  ],
};


test("LAB_AWARE intentionally reveals laboratory fields", () => {
  assert.deepEqual(fieldsForMode(schema, "PRE_LAB").map((field) => field.field_id), ["age"]);
  assert.deepEqual(
    fieldsForMode(schema, "LAB_AWARE").map((field) => field.field_id),
    ["age", "platelets"]
  );
});


test("serialization includes no unknown keys", () => {
  assert.deepEqual(
    serializeAssessment(schema, "PRE_LAB", { age: "12", unknown: "x" }),
    { mode: "PRE_LAB", values: { age: 12 } }
  );
});


test("required numeric validation is explicit", () => {
  assert.equal(validateFormValues(schema, "PRE_LAB", {}).age, "Required");
  assert.equal(validateFormValues(schema, "PRE_LAB", { age: "abc" }).age, "Enter a number");
});

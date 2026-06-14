import assert from "node:assert/strict";
import test from "node:test";

import { validateManifest, validateRequiredFields } from "../assets/data-client.js";


test("rejects unsupported public schema versions", () => {
  assert.throws(
    () => validateManifest({ schema_version: "99.0.0" }),
    /Unsupported/
  );
});


test("rejects missing manifest fields", () => {
  assert.throws(
    () => validateManifest({ schema_version: "3.0.0" }),
    /missing/
  );
});


test("required-field validator reports absent keys", () => {
  assert.throws(
    () => validateRequiredFields({}, ["run_id"], "evidence"),
    /run_id/
  );
});

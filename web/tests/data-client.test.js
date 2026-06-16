import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import test from "node:test";

import {
  sha256Text,
  validateManifest,
  validateRequiredFields,
} from "../assets/data-client.js";


test("rejects unsupported public schema versions", () => {
  assert.throws(
    () => validateManifest({ schema_version: "99.0.0" }),
    /Unsupported/
  );
});

test("accepts the report-ready public contract", () => {
  const manifest = validateManifest({
    schema_version: "3.1.0",
    notebook_run_id: "run",
    notebook_sha256: "a".repeat(64),
    analysis_policy_id: "policy",
    scientific_schema_version: "1.1.0",
    source_commit: "commit",
    documents: {},
    models: {},
    policy_ids: {},
    class_order: [],
    safe_scope: "scope",
  });
  assert.equal(manifest.analysis_policy_id, "policy");
});


test("rejects missing manifest fields", () => {
  assert.throws(
    () => validateManifest({ schema_version: "3.1.0" }),
    /missing/
  );
});


test("required-field validator reports absent keys", () => {
  assert.throws(
    () => validateRequiredFields({}, ["run_id"], "evidence"),
    /run_id/
  );
});


test("hashes exact JSON response bytes without numeric reserialization", async () => {
  const raw = '{"estimate":0.0,"support":3}';
  const expected = createHash("sha256").update(raw, "utf8").digest("hex");
  assert.equal(await sha256Text(raw), expected);
});

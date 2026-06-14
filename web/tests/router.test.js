import test from "node:test";
import assert from "node:assert/strict";

import { normalizeRoute } from "../assets/router.js";

const routes = ["overview", "models", "fairness"];

test("normalizes valid hash routes", () => {
  assert.equal(normalizeRoute("#models", routes), "models");
});

test("falls back for missing and unknown routes", () => {
  assert.equal(normalizeRoute("", routes), "overview");
  assert.equal(normalizeRoute("#not-a-route", routes), "overview");
});

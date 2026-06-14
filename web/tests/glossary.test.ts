import { describe, expect, it } from "vitest";

import { GLOSSARY, glossaryAnchor, glossaryEntry } from "@/lib/glossary";

const REQUIRED = [
  "macro-f1",
  "pr-auc",
  "calibration",
  "entropy",
  "conformal-set",
  "leakage",
  "center-transfer",
  "out-of-fold",
] as const;

describe("glossary", () => {
  it("defines every required term with a non-trivial definition", () => {
    for (const slug of REQUIRED) {
      const entry = GLOSSARY[slug];
      expect(entry, slug).toBeTruthy();
      expect(entry.term.length).toBeGreaterThan(0);
      expect(entry.definition.length).toBeGreaterThan(20);
    }
  });

  it("builds deep-link anchors and looks up entries by slug", () => {
    expect(glossaryAnchor("leakage")).toBe("/methodology#glossary-leakage");
    expect(glossaryEntry("entropy")?.term).toBe("Entropy");
    expect(glossaryEntry("nonexistent")).toBeUndefined();
  });
});

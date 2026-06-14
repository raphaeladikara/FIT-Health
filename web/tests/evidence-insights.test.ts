import { describe, expect, it } from "vitest";

import {
  centerTransferInsight,
  conformalInsight,
  leakageInsight,
} from "@/lib/evidence-insights";
import type { EvidenceRecord } from "@/lib/types";

const typhoidRow: EvidenceRecord = {
  label: "typhoid",
  empirical_coverage: 0.5714,
  test_positives: 7,
  covered_positives: 4,
};

const centerRows: EvidenceRecord[] = [
  { test_on: "CMA de DO", macro_f1: 0.3555, recall_dengue: 0, recall_typhoid: 0, recall_yellow_fever: 0 },
  { test_on: "CMA de DAFRA", macro_f1: 0.3652, recall_dengue: 0, recall_typhoid: 0, recall_yellow_fever: 0 },
];

describe("conformalInsight", () => {
  it("flags typhoid conformal undercoverage", () => {
    const insight = conformalInsight(typhoidRow, 0.9);
    expect(insight.severity).toBe("warning");
    expect(insight.summary).toMatch(/57\.1%/);
    expect(insight.cannotClaim).toMatch(/coverage/i);
  });

  it("is neutral when coverage meets the target", () => {
    expect(
      conformalInsight({ label: "malaria", empirical_coverage: 0.985 }, 0.9).severity,
    ).toBe("neutral");
  });
});

describe("centerTransferInsight", () => {
  it("flags zero rare-label transfer recall as critical", () => {
    const insight = centerTransferInsight(centerRows);
    expect(insight.severity).toBe("critical");
    expect(insight.limitations).toContain(
      "Rare-label recall is zero in both held-out centers",
    );
  });
});

describe("leakageInsight", () => {
  it("quantifies the FULL-track inflation", () => {
    const insight = leakageInsight(0.61, 0.708);
    expect(insight.summary).toMatch(/0\.10/);
    expect(insight.severity).toBe("warning");
  });
});

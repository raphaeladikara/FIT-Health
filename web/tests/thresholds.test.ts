import { describe, expect, it } from "vitest";

import {
  decisionForProbability,
  flaggedLabels,
  thresholdMarkerPercent,
} from "@/lib/thresholds";

describe("decisionForProbability", () => {
  it("flags a label when probability reaches its own threshold", () => {
    expect(decisionForProbability({ probability: 0.2, threshold: 0.18 })).toBe(true);
  });

  it("does not flag a label below its threshold (no fixed 0.50 cutoff)", () => {
    expect(decisionForProbability({ probability: 0.487, threshold: 0.5 })).toBe(false);
  });

  it("treats reaching the threshold exactly as a positive decision", () => {
    expect(decisionForProbability({ probability: 0.05, threshold: 0.05 })).toBe(true);
  });
});

describe("thresholdMarkerPercent", () => {
  it("maps a threshold to its track position", () => {
    expect(thresholdMarkerPercent(0.18)).toBe(18);
  });

  it("clamps out-of-range thresholds", () => {
    expect(thresholdMarkerPercent(1.4)).toBe(100);
    expect(thresholdMarkerPercent(-0.2)).toBe(0);
  });
});

describe("flaggedLabels", () => {
  it("returns predicted labels ordered by margin over threshold", () => {
    expect(
      flaggedLabels({
        malaria: { probability: 0.95, threshold: 0.05, predicted: true },
        dengue: { probability: 0.49, threshold: 0.5, predicted: false },
        typhoid: { probability: 0.6, threshold: 0.55, predicted: true },
      }),
    ).toEqual(["malaria", "typhoid"]);
  });
});

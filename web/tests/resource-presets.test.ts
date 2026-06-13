import { describe, expect, it } from "vitest";

import {
  RESOURCE_PRESETS,
  RESOURCE_PRESET_ORDER,
  resolveResourcePreset,
} from "@/lib/resource-presets";

describe("resource presets", () => {
  it("exposes deterministic named scenarios", () => {
    expect(RESOURCE_PRESETS.safety.capacity).toEqual({
      rapidTests: 160,
      beds: 50,
      monitoringSlots: 180,
      staffReviews: 220,
    });
    expect(RESOURCE_PRESET_ORDER).toHaveLength(4);
  });

  it("resolves a preset key from a query value", () => {
    expect(resolveResourcePreset("safety").key).toBe("safety");
  });

  it("falls back to the current baseline for unknown keys", () => {
    expect(resolveResourcePreset("nonsense").key).toBe("current");
    expect(resolveResourcePreset(null).key).toBe("current");
  });
});

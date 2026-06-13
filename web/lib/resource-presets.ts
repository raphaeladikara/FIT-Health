import type { CapacityInput } from "@/lib/types";

export type ResourcePresetKey =
  | "current"
  | "operational"
  | "safety"
  | "severeShortage";

export type ResourcePreset = {
  key: ResourcePresetKey;
  label: string;
  description: string;
  capacity: CapacityInput;
};

/**
 * Named capacity scenarios. Deterministic by design so a scenario link
 * (?preset=safety) always loads the same starting point for a judge demo.
 */
export const RESOURCE_PRESETS: Record<ResourcePresetKey, ResourcePreset> = {
  current: {
    key: "current",
    label: "Current capacity",
    description: "Today's constrained baseline.",
    capacity: { rapidTests: 50, beds: 12, monitoringSlots: 80, staffReviews: 80 },
  },
  operational: {
    key: "operational",
    label: "Operational target",
    description: "Capacity that clears most confirmatory demand.",
    capacity: { rapidTests: 100, beds: 35, monitoringSlots: 120, staffReviews: 150 },
  },
  safety: {
    key: "safety",
    label: "Safety-first",
    description: "Headroom that absorbs surges and uncertainty.",
    capacity: { rapidTests: 160, beds: 50, monitoringSlots: 180, staffReviews: 220 },
  },
  severeShortage: {
    key: "severeShortage",
    label: "Severe shortage",
    description: "A stress test of a depleted outbreak response.",
    capacity: { rapidTests: 20, beds: 5, monitoringSlots: 30, staffReviews: 40 },
  },
};

export const RESOURCE_PRESET_ORDER: ResourcePresetKey[] = [
  "current",
  "operational",
  "safety",
  "severeShortage",
];

export function resolveResourcePreset(value: string | null | undefined): ResourcePreset {
  if (value && value in RESOURCE_PRESETS) {
    return RESOURCE_PRESETS[value as ResourcePresetKey];
  }
  return RESOURCE_PRESETS.current;
}

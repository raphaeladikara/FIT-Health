import type {
  AllocatedPatient,
  CapacityInput,
  CapacityRow,
  Patient,
  ResourceName,
  ScenarioImpact,
} from "@/lib/types";

/** Categories eligible for a confirmatory rapid test under the simulator's rule. */
const TEST_ELIGIBLE = ["Confirmatory Test Priority", "Urgent Response Priority"];

/**
 * Plain-language, clinically unvalidated demand assumptions. These make the simulator's
 * heuristics inspectable rather than presenting them as validated clinical thresholds.
 */
export const DEMAND_ASSUMPTIONS: Record<ResourceName, string> = {
  "Rapid tests":
    "One rapid test per confirmatory-test-priority or urgent case (heuristic, not a clinical protocol).",
  Beds: "One inpatient bed per urgent-response case (heuristic).",
  "Monitoring slots":
    "One monitoring slot per clinical-review or confirmatory-test case (heuristic).",
  "Staff review slots":
    "One review per non-routine case plus one extra review per high-uncertainty case (heuristic).",
};

export function calculateCapacity(
  patients: Patient[],
  input: CapacityInput,
): CapacityRow[] {
  const urgent = patients.filter(
    (patient) => patient.triage_category === "Urgent Response Priority",
  ).length;
  const confirmatory = patients.filter((patient) =>
    TEST_ELIGIBLE.includes(patient.triage_category),
  ).length;
  const monitoring = patients.filter((patient) =>
    ["Clinical Review", "Confirmatory Test Priority"].includes(
      patient.triage_category,
    ),
  ).length;
  const staff =
    patients.filter((patient) =>
      [
        "Clinical Review",
        "Confirmatory Test Priority",
        "Urgent Response Priority",
      ].includes(patient.triage_category),
    ).length +
    patients.filter((patient) => patient.uncertainty_level === "high").length;

  const rows: Array<[ResourceName, number, number]> = [
    ["Rapid tests", confirmatory, input.rapidTests],
    ["Beds", urgent, input.beds],
    ["Monitoring slots", monitoring, input.monitoringSlots],
    ["Staff review slots", staff, input.staffReviews],
  ];

  return rows.map(([resource, demand, capacity]) => ({
    resource,
    demand,
    capacity,
    shortfall: Math.max(demand - capacity, 0),
    surplus: Math.max(capacity - demand, 0),
    status: capacity >= demand ? "Sufficient" : "Insufficient",
    assumption: DEMAND_ASSUMPTIONS[resource],
  }));
}

export function allocateRapidTests(
  patients: Patient[],
  available: number,
): AllocatedPatient[] {
  let allocated = 0;
  return [...patients]
    .sort(
      (left, right) =>
        right.triage_score - left.triage_score ||
        right.coinfection_prob - left.coinfection_prob ||
        left.case_id.localeCompare(right.case_id),
    )
    .map((patient) => {
      const eligible = TEST_ELIGIBLE.includes(patient.triage_category);
      const receivesTest = eligible && allocated < available;
      if (receivesTest) allocated += 1;
      const test_allocation = !eligible
        ? "Not eligible"
        : receivesTest
          ? "Allocated"
          : "Waitlisted";
      return { ...patient, test_allocation };
    });
}

/** Summarise the operational consequence of one capacity scenario. */
export function scenarioImpact(
  patients: Patient[],
  capacity: CapacityInput,
): ScenarioImpact {
  const queue = allocateRapidTests(patients, capacity.rapidTests);
  const rows = calculateCapacity(patients, capacity);
  const shortfall = (resource: ResourceName) =>
    rows.find((row) => row.resource === resource)?.shortfall ?? 0;
  return {
    allocatedTests: queue.filter((p) => p.test_allocation === "Allocated").length,
    waitlistedTests: queue.filter((p) => p.test_allocation === "Waitlisted").length,
    urgentBedShortfall: shortfall("Beds"),
    monitoringShortfall: shortfall("Monitoring slots"),
    reviewShortfall: shortfall("Staff review slots"),
  };
}

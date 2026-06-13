import type {
  AllocatedPatient,
  CapacityInput,
  CapacityRow,
  Patient,
} from "@/lib/types";

export function calculateCapacity(
  patients: Patient[],
  input: CapacityInput,
): CapacityRow[] {
  const urgent = patients.filter(
    (patient) => patient.triage_category === "Urgent Response Priority",
  ).length;
  const confirmatory = patients.filter((patient) =>
    ["Confirmatory Test Priority", "Urgent Response Priority"].includes(
      patient.triage_category,
    ),
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

  const rows: Array<[CapacityRow["resource"], number, number]> = [
    ["Rapid tests", confirmatory, input.rapidTests],
    ["Beds", urgent, input.beds],
    ["Monitoring slots", monitoring, input.monitoringSlots],
    ["Staff review slots", staff, input.staffReviews],
  ];

  return rows.map(([resource, demand, capacity]) => ({
    resource,
    demand,
    capacity,
    gap: capacity - demand,
    status: capacity >= demand ? "Sufficient" : "Insufficient",
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
      const eligible = [
        "Confirmatory Test Priority",
        "Urgent Response Priority",
      ].includes(patient.triage_category);
      const receivesTest = eligible && allocated < available;
      if (receivesTest) allocated += 1;
      return {
        ...patient,
        test_allocation: receivesTest ? "Allocated" : "Waiting",
      };
    });
}

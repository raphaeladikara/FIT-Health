const STAGES = new Set(["intake", "assessment", "decision", "response"]);
const STAGE_ORDER = {
  PRE_LAB: new Set(["PRE_LAB"]),
  LAB_AWARE: new Set(["PRE_LAB", "LAB_AWARE"]),
};


export function parsePrototypeState(search = "") {
  const params = new URLSearchParams(search);
  const requestedStage = params.get("stage") || "intake";
  return {
    caseId: params.get("case") || "",
    stage: STAGES.has(requestedStage) ? requestedStage : "intake",
  };
}


export function serializePrototypeState({ caseId = "", stage = "intake" }) {
  const params = new URLSearchParams();
  if (caseId) params.set("case", caseId);
  params.set("stage", STAGES.has(stage) ? stage : "intake");
  return `?${params.toString()}`;
}


// Scenario-assumption operational rates from the frozen-test demonstration
// state (n=78). These are illustrative planning assumptions — NOT measured
// clinical impact and NOT population prevalence. A cohort is a population, so
// it is scaled by these fractional rates rather than by one case's 0/1 outcome.
export const FROZEN_TEST_OPERATIONAL_RATES = {
  review: 0.4615, // high-priority cases routed to clinician review (≈36/78)
  test: 0.2436, // cases flagged for confirmatory-testing support (≈19/78)
  urgent: 0.2179, // cases routed to urgent response priority (≈17/78)
  uncertainty: 0.3077, // high-uncertainty cases needing enhanced scrutiny (≈24/78)
};

// Compare projected demand against entered capacity for one resource lane.
export function capacityStatus(demand, capacity) {
  if (!Number.isFinite(capacity) || capacity <= 0) {
    return { capacity: 0, gap: demand, status: "over-capacity" };
  }
  const gap = demand - capacity;
  if (gap > 0) return { capacity, gap, status: "over-capacity" };
  if (demand >= capacity * 0.9) return { capacity, gap, status: "near-limit" };
  return { capacity, gap, status: "within-capacity" };
}

export function assessmentToProjection(
  assessment,
  {
    cohortSize,
    reviewCapacity = 0,
    testCapacity,
    urgentCapacity,
    rates = FROZEN_TEST_OPERATIONAL_RATES,
  },
) {
  const n = Math.max(0, Math.round(Number(cohortSize)) || 0);
  const demand = (rate) => Math.round(rate * n);
  const reviewNeeded = demand(rates.review);
  const testsNeeded = demand(rates.test);
  const urgentNeeded = demand(rates.urgent);
  const uncertaintyNeeded = demand(rates.uncertainty);
  return {
    interpretation: "scenario projection; not measured clinical impact",
    cohortSize: n,
    rates,
    // Flat fields retained for back-compatibility with existing callers/tests.
    reviewNeeded,
    testsNeeded,
    urgentNeeded,
    uncertaintyNeeded,
    unmetTests: Math.max(0, testsNeeded - (testCapacity || 0)),
    unmetUrgent: Math.max(0, urgentNeeded - (urgentCapacity || 0)),
    categories: [
      {
        key: "review",
        label: "Clinical reviews",
        demand: reviewNeeded,
        note: "High-priority cases routed to clinician review",
        ...capacityStatus(reviewNeeded, Number(reviewCapacity)),
      },
      {
        key: "test",
        label: "Confirmatory tests",
        demand: testsNeeded,
        note: "Cases flagged for confirmatory-testing support",
        ...capacityStatus(testsNeeded, Number(testCapacity)),
      },
      {
        key: "urgent",
        label: "Urgent reviews",
        demand: urgentNeeded,
        note: "Cases routed to urgent response priority",
        ...capacityStatus(urgentNeeded, Number(urgentCapacity)),
      },
    ],
    highUncertainty: {
      label: "High-uncertainty cases",
      demand: uncertaintyNeeded,
      fraction: rates.uncertainty,
      note: "Subset requiring enhanced review scrutiny (overlaps the lanes above)",
    },
  };
}


export function inputCompleteness(schema, mode, values) {
  const available = schema.fields.filter((field) =>
    (STAGE_ORDER[mode] || STAGE_ORDER.PRE_LAB).has(field.stage),
  );
  const completed = available.filter((field) => {
    const value = values[field.field_id];
    return value !== "" && value !== null && value !== undefined;
  }).length;
  return {
    completed,
    total: available.length,
    fraction: available.length ? completed / available.length : 0,
  };
}


export function evidenceLimitedWarnings(summary = {}) {
  return ["typhoid", "yellow_fever"]
    .filter((label) => summary[label])
    .map((label) => ({
      label,
      frozenSupport: summary[label].frozen_support,
      recall: summary[label].recall,
      message: label === "yellow_fever"
        ? "Very limited frozen-test evidence. A low score cannot rule out yellow fever."
        : "Limited frozen-test evidence. Route concerning cases to confirmatory testing and clinical review.",
    }));
}

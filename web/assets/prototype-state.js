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


export function assessmentToProjection(
  assessment,
  {
    cohortSize,
    testCapacity,
    urgentCapacity,
  },
) {
  const decisions = Object.values(assessment.decisions || {});
  const testRate = decisions.some(Boolean) || assessment.abstention?.required ? 1 : 0;
  const reviewRate = assessment.abstention?.required
    || assessment.triage_category === "Clinical review required" ? 1 : 0;
  const urgentRate = assessment.uncertainty?.category === "high"
    || assessment.abstention?.required ? 1 : 0;
  const testsNeeded = Math.round(testRate * cohortSize);
  const reviewNeeded = Math.round(reviewRate * cohortSize);
  const urgentNeeded = Math.round(urgentRate * cohortSize);
  return {
    interpretation: "scenario projection; not measured clinical impact",
    cohortSize,
    testsNeeded,
    unmetTests: Math.max(0, testsNeeded - testCapacity),
    reviewNeeded,
    urgentNeeded,
    unmetUrgent: Math.max(0, urgentNeeded - urgentCapacity),
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

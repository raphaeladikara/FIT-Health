import { loadWebBundle } from "./data-client.js";
import { percent, titleCase } from "./formatters.js";
import {
  assessmentToProjection,
  evidenceLimitedWarnings,
  inputCompleteness,
  parsePrototypeState,
  serializePrototypeState,
} from "./prototype-state.js";
import { fieldsForMode, serializeAssessment, validateFormValues } from "./schema-form.js";


const STAGES = ["intake", "assessment", "decision", "response"];
const STAGE_COPY = {
  intake: ["Prototype figure 1", "Case intake", "What this demonstrates: schema-governed anonymous intake before model execution."],
  assessment: ["Prototype figure 2", "Locked model assessment", "What this demonstrates: released preprocessing, calibration, thresholds, and uncertainty applied to one anonymous case."],
  decision: ["Prototype figure 3", "Operational review routing", "What this demonstrates: model output translated into review and confirmatory-testing states with explicit limits."],
  response: ["Prototype figure 4", "Response-capacity projection", "What this demonstrates: patient-level routing scaled into an assumption-bound planning scenario."],
};

let bundle;
let assessment = null;
let current = parsePrototypeState(location.search);
const form = document.querySelector("#prototype-form");
const fields = document.querySelector("#prototype-fields");
const mode = document.querySelector("#prototype-mode");
const caseSelect = document.querySelector("#prototype-case");
const alertId = "prototype-alert";


function formValues() {
  return Object.fromEntries(new FormData(form).entries());
}


function setUrl() {
  history.replaceState({}, "", `${location.pathname}${serializePrototypeState(current)}`);
}


function showIntakeAlert(message) {
  let alert = document.querySelector(`#${alertId}`);
  if (!alert) {
    alert = document.createElement("div");
    alert.id = alertId;
    alert.className = "callout callout-risk prototype-alert";
    document.querySelector("#input-completeness").after(alert);
  }
  alert.innerHTML = `<strong>Assessment unavailable.</strong><p>${message}</p>`;
}


function clearIntakeAlert() {
  document.querySelector(`#${alertId}`)?.remove();
}


function renderStages() {
  document.querySelector("#prototype-stages").innerHTML = STAGES.map((stage, index) =>
    `<button type="button" data-stage="${stage}" class="${stage === current.stage ? "active" : ""}">
      <span>${index + 1}</span><strong>${STAGE_COPY[stage][1]}</strong>
    </button>`
  ).join("");
  document.querySelectorAll("[data-stage]").forEach((button) => {
    button.addEventListener("click", () => {
      const requested = button.dataset.stage;
      if (!assessment && requested !== "intake") return;
      current.stage = requested;
      setUrl();
      renderStage();
    });
  });
}


function renderStage() {
  const index = STAGES.indexOf(current.stage);
  document.querySelectorAll("[data-stage-panel]").forEach((panel) => {
    panel.hidden = panel.dataset.stagePanel !== current.stage;
  });
  const [number, title, caption] = STAGE_COPY[current.stage];
  document.querySelector("#figure-number").textContent = number;
  document.querySelector("#stage-title").textContent = title;
  document.querySelector("#stage-caption").textContent = caption;
  document.querySelector("#prototype-back").disabled = index === 0;
  document.querySelector("#prototype-next").textContent = current.stage === "intake"
    ? "Run locked assessment"
    : current.stage === "response" ? "Recalculate projection" : "Continue";
  renderStages();
}


function renderFields() {
  fields.innerHTML = fieldsForMode(bundle.inputSchema, mode.value).map((field) =>
    `<div class="field assessment-field">
      <label for="prototype-${field.field_id}">${field.display_label}${field.required ? " *" : ""}</label>
      ${field.type === "category" && field.allowed_values
        ? `<select id="prototype-${field.field_id}" name="${field.field_id}"><option value="">Not available</option>${field.allowed_values.map((value) => `<option>${value}</option>`).join("")}</select>`
        : `<input id="prototype-${field.field_id}" name="${field.field_id}" type="${field.type === "number" ? "number" : "text"}" step="any">`}
      <small>${field.unit ? `${field.unit}. ` : ""}${field.clinical_help}</small>
      <span class="field-error" id="prototype-error-${field.field_id}"></span>
    </div>`
  ).join("");
  updateCompleteness();
}


function updateCompleteness() {
  const status = inputCompleteness(bundle.inputSchema, mode.value, formValues());
  const percentage = Math.round(status.fraction * 100);
  document.querySelector("#input-completeness").innerHTML =
    `<div><span>Optional model fields populated</span><strong>${status.completed} of ${status.total}</strong></div>
     <div class="completeness-track" aria-label="${percentage}% of model fields populated"><span style="width:${percentage}%"></span></div>
     <small>All fields are optional — none are required to run the locked pipeline, which imputes missing values. Extensive missingness can route the case to mandatory review.</small>`;
}


function loadCase(caseId) {
  const selected = bundle.cases.find((item) => item.case_id === caseId);
  if (!selected) return;
  current.caseId = selected.case_id;
  mode.value = selected.mode;
  renderFields();
  for (const [key, value] of Object.entries(selected.values)) {
    const control = form.elements.namedItem(key);
    if (control && value !== null) control.value = value;
  }
  updateCompleteness();
  setUrl();
}


function renderAssessment(response) {
  const support = Object.fromEntries(
    bundle.evidence.validation_and_frozen_test.per_label
      .filter((row) => row.track === response.mode)
      .map((row) => [row.label, row.support_pos]),
  );
  const predictionSet = new Set(response.prediction_set || []);
  document.querySelector("#assessment-status").innerHTML =
    `<div class="assessment-outcome ${response.abstention.required ? "requires-review" : ""}">
      <span>${response.abstention.required ? "Mandatory review state" : "Model assessment complete"}</span>
      <h3>${response.abstention.required ? "Clinical review required" : response.triage_category}</h3>
      <p>${response.abstention.required
        ? `Model output is generated below, but mandatory review is required: ${response.abstention.reasons.map(titleCase).join(", ")}.`
        : "No automatic review rule fired. Calibrated probabilities and the prediction set are shown below as decision support only."}</p>
    </div>`;
  document.querySelector("#prototype-probabilities").innerHTML =
    `<div class="probability-list">${Object.entries(response.probabilities).map(([label, probability]) => {
      const above = response.decisions[label];
      const inSet = predictionSet.has(label);
      const statusTag = above
        ? `<em class="prob-flag above">Above threshold</em>`
        : inSet
          ? `<em class="prob-flag inset">In prediction set</em>`
          : `<em class="prob-flag below">Below threshold</em>`;
      return `<div class="prototype-probability">
        <div><strong>${titleCase(label)}</strong><small>${support[label]} frozen-test positives</small></div>
        <div class="probability-track"><span class="probability-fill ${above ? "positive" : ""}" style="width:${probability * 100}%"></span><i class="threshold-marker" style="left:${response.thresholds[label] * 100}%"></i></div>
        <b>${percent(probability)}${statusTag}</b>
      </div>`;
    }).join("")}</div>
    <div class="assessment-foot"><span>Prediction set: <strong>${response.prediction_set.map(titleCase).join(", ") || "No informative set"}</strong></span><span>Uncertainty: <strong>${titleCase(response.uncertainty.category)}</strong></span></div>
    <p class="decision-boundary">${bundle.evidence.safe_scope}</p>`;
}


function renderDecision(response) {
  const warnings = evidenceLimitedWarnings(bundle.evidence.rare_label_summary);
  const elevated = Object.entries(response.decisions).filter(([, value]) => value).map(([label]) => titleCase(label));
  document.querySelector("#prototype-decision").innerHTML =
    `<div class="decision-summary">
      <div><span>Routing outcome</span><h3>${response.abstention.required ? "Clinical review required" : response.triage_category}</h3><p>${elevated.length ? `Elevated modeled risk: ${elevated.join(", ")}.` : "No label exceeds its released threshold."}</p></div>
      <dl><div><dt>Confirmatory testing</dt><dd>${elevated.length || response.abstention.required ? "Prioritize under local protocol" : "Use clinical judgment"}</dd></div><div><dt>Human control</dt><dd>Required for escalation and exclusion decisions</dd></div><div><dt>Diagnostic claim</dt><dd>Not provided</dd></div></dl>
    </div>
    <div class="rare-warning-list">${warnings.map((warning) =>
      `<article><span>${titleCase(warning.label)} · ${warning.frozenSupport} positives</span><strong>${warning.message}</strong><small>Frozen-test recall ${percent(warning.recall)}</small></article>`
    ).join("")}</div>
    <p class="decision-boundary">${response.safe_scope}</p>`;
}


const CAPACITY_STATUS_COPY = {
  "within-capacity": "Within capacity",
  "near-limit": "Near limit",
  "over-capacity": "Over capacity",
};


function renderProjection() {
  if (!assessment) return;
  const projection = assessmentToProjection(assessment, {
    cohortSize: Number(document.querySelector("#cohort-size").value),
    reviewCapacity: Number(document.querySelector("#review-capacity").value),
    testCapacity: Number(document.querySelector("#test-capacity").value),
    urgentCapacity: Number(document.querySelector("#urgent-capacity").value),
  });
  const cards = projection.categories.map((category) => {
    const gapText = category.gap > 0
      ? `${category.gap} beyond capacity`
      : `${Math.abs(category.gap)} headroom`;
    return `<article class="capacity-card status-${category.status}">
      <span>${category.label}</span>
      <strong>${category.demand}</strong>
      <p class="capacity-status">${CAPACITY_STATUS_COPY[category.status]}</p>
      <dl class="capacity-ledger"><div><dt>Demand</dt><dd>${category.demand}</dd></div><div><dt>Capacity</dt><dd>${category.capacity || "—"}</dd></div><div><dt>Gap</dt><dd>${gapText}</dd></div></dl>
      <small>${category.note}</small>
    </article>`;
  }).join("");
  const uncertainty = projection.highUncertainty;
  const uncertaintyCard = `<article class="capacity-card status-context">
    <span>${uncertainty.label}</span>
    <strong>${uncertainty.demand}</strong>
    <p class="capacity-status">${percent(uncertainty.fraction)} of cohort</p>
    <small>${uncertainty.note}</small>
  </article>`;
  document.querySelector("#prototype-response").innerHTML =
    `<div class="response-metrics quad">${cards}${uncertaintyCard}</div>
    <div class="callout callout-warn"><strong>Scenario projection:</strong> ${projection.interpretation}. Rates are derived from this demonstration state (n=78) and are illustrative planning assumptions — not measured clinical impact and not population prevalence estimates.</div>`;
}


async function runAssessment() {
  clearIntakeAlert();
  document.querySelectorAll(".field-error").forEach((node) => { node.textContent = ""; });
  const errors = validateFormValues(bundle.inputSchema, mode.value, formValues());
  if (Object.keys(errors).length) {
    for (const [fieldId, message] of Object.entries(errors)) {
      document.querySelector(`#prototype-error-${CSS.escape(fieldId)}`).textContent = message;
    }
    current.stage = "intake";
    renderStage();
    document.querySelector(`#prototype-${CSS.escape(Object.keys(errors)[0])}`).focus();
    return false;
  }
  document.querySelector("#assessment-status").innerHTML = `<div class="loading-state"><span></span><strong>Running the locked release...</strong></div>`;
  const response = await fetch("/api/assess", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(serializeAssessment(bundle.inputSchema, mode.value, formValues())),
  });
  if ([404, 405, 501].includes(response.status)) {
    throw new Error("The live assessment API is not available from the current static server. Serve with python web/serve_live.py --port 4173 so /api/assess can run the locked model locally.");
  }
  const isJson = response.headers.get("content-type")?.includes("application/json");
  const payload = isJson ? await response.json() : { error: await response.text() };
  if (!response.ok) throw new Error(payload.error || "Assessment failed");
  assessment = payload;
  renderAssessment(payload);
  renderDecision(payload);
  renderProjection();
  return true;
}


function renderEvidence() {
  const primary = bundle.evidence.primary_track_summary;
  const center = bundle.evidence.center_transfer_summary;
  document.querySelector("#prototype-run").innerHTML =
    `<span>Locked release</span><strong>${bundle.manifest.notebook_run_id}</strong><small>Policy ${bundle.manifest.analysis_policy_id}</small>`;
  document.querySelector("#prototype-positioning").textContent =
    bundle.evidence.narrative.prototype_positioning;
  document.querySelector("#prototype-evidence").innerHTML =
    `<dl class="evidence-facts">
      <div><dt>Primary track</dt><dd>${primary.track} · ${titleCase(primary.model)}</dd></div>
      <div><dt>Frozen-test macro-F1</dt><dd>${primary.macro_f1.toFixed(3)}</dd></div>
      <div><dt>Frozen-test micro-F1</dt><dd>${primary.micro_f1.toFixed(3)}</dd></div>
      <div><dt>Macro PR-AUC</dt><dd>${primary.macro_pr_auc.toFixed(3)}</dd></div>
      <div><dt>Center-transfer warning</dt><dd>${center.macro_f1_min.toFixed(3)}–${center.macro_f1_max.toFixed(3)} macro-F1</dd></div>
      <div><dt>Notebook fingerprint</dt><dd class="hash">${bundle.manifest.notebook_sha256.slice(0, 16)}…</dd></div>
    </dl>
    <p>${primary.decision}</p>
    <div class="callout callout-warn"><strong>Generalization boundary:</strong> ${center.interpretation}</div>`;
}


async function advance() {
  const index = STAGES.indexOf(current.stage);
  if (current.stage === "intake") {
    if (!await runAssessment()) return;
    current.stage = "assessment";
  } else if (current.stage === "response") {
    renderProjection();
  } else {
    current.stage = STAGES[Math.min(index + 1, STAGES.length - 1)];
  }
  setUrl();
  renderStage();
}


async function init() {
  bundle = await loadWebBundle();
  caseSelect.innerHTML = `<option value="">Manual anonymous intake</option>${bundle.cases.map((item) => `<option value="${item.case_id}">${item.label}</option>`).join("")}`;
  renderFields();
  renderEvidence();
  renderStage();
  if (current.caseId) {
    caseSelect.value = current.caseId;
    loadCase(current.caseId);
    if (current.stage !== "intake") {
      await runAssessment();
      renderStage();
    }
  }
  caseSelect.addEventListener("change", () => loadCase(caseSelect.value));
  mode.addEventListener("change", renderFields);
  form.addEventListener("input", updateCompleteness);
  document.querySelector("#prototype-next").addEventListener("click", () => advance().catch(showError));
  document.querySelector("#prototype-back").addEventListener("click", () => {
    current.stage = STAGES[Math.max(0, STAGES.indexOf(current.stage) - 1)];
    setUrl();
    renderStage();
  });
  ["cohort-size", "review-capacity", "test-capacity", "urgent-capacity"].forEach((id) =>
    document.querySelector(`#${id}`).addEventListener("input", renderProjection)
  );
}


function showError(error) {
  if (current.stage === "intake") {
    const unavailable = error.message.includes("404") || error.message.includes("501") || error.message.includes("Unsupported method") || error.message.includes("Not Found")
      ? "The live assessment API is not available from the current static server. Serve with python web/serve_live.py --port 4173 so /api/assess can run the locked model locally."
      : error.message;
    showIntakeAlert(unavailable);
    return;
  }
  document.querySelector("#assessment-status").innerHTML =
    `<div class="callout callout-risk"><strong>Assessment unavailable.</strong><p>${error.message}</p></div>`;
}


init().catch(showError);

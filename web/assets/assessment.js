import { loadWebBundle } from "./data-client.js";
import { fieldsForMode, serializeAssessment, validateFormValues } from "./schema-form.js";
import { provenanceText } from "./provenance.js";
import { percent, titleCase } from "./formatters.js";


let bundle;
const form = document.querySelector("#assessment-form");
const fields = document.querySelector("#assessment-fields");
const result = document.querySelector("#assessment-result");
const mode = document.querySelector("#assessment-mode");


function values() {
  return Object.fromEntries(new FormData(form).entries());
}


function renderFields() {
  fields.innerHTML = fieldsForMode(bundle.inputSchema, mode.value).map((field) =>
    `<div class="field assessment-field">
      <label for="field-${field.field_id}">${field.display_label}${field.required ? " *" : ""}</label>
      ${field.type === "category" && field.allowed_values
        ? `<select id="field-${field.field_id}" name="${field.field_id}"><option value="">Not available</option>${field.allowed_values.map((value) => `<option>${value}</option>`).join("")}</select>`
        : `<input id="field-${field.field_id}" name="${field.field_id}" type="${field.type === "number" ? "number" : "text"}" step="any">`}
      <small>${field.unit ? `${field.unit}. ` : ""}${field.clinical_help}</small>
      <span class="field-error" id="error-${field.field_id}"></span>
    </div>`
  ).join("");
}


function renderResult(response) {
  const probabilityRows = Object.entries(response.probabilities).map(([label, probability]) =>
    `<tr><th>${titleCase(label)}</th><td>${percent(probability)}</td><td>${percent(response.thresholds[label])}</td><td>${response.decisions[label] ? "Elevated modeled risk" : "Below released threshold"}</td></tr>`
  ).join("");
  result.innerHTML = `<div class="result-scope">${response.safe_scope}</div>
    <h2>${response.abstention.required ? "Clinical review required" : response.triage_category}</h2>
    ${response.abstention.required ? `<div class="callout callout-risk"><strong>Assessment abstained.</strong><p>${response.abstention.reasons.join(", ")}</p></div>` : ""}
    <div class="table-wrap"><table><thead><tr><th>Label</th><th>Calibrated risk</th><th>Threshold</th><th>Decision state</th></tr></thead><tbody>${probabilityRows}</tbody></table></div>
    <p><strong>Prediction set:</strong> ${response.prediction_set.map(titleCase).join(", ") || "No informative set"}</p>
    <p><strong>Uncertainty:</strong> ${titleCase(response.uncertainty.category)}</p>
    <p>${response.explanation.warning}</p>
    <small>${provenanceText(response)}</small>`;
  result.focus();
}


async function submit(event) {
  event.preventDefault();
  document.querySelectorAll(".field-error").forEach((node) => { node.textContent = ""; });
  const errors = validateFormValues(bundle.inputSchema, mode.value, values());
  if (Object.keys(errors).length) {
    for (const [fieldId, message] of Object.entries(errors)) {
      document.querySelector(`#error-${CSS.escape(fieldId)}`).textContent = message;
    }
    document.querySelector(`#field-${CSS.escape(Object.keys(errors)[0])}`).focus();
    return;
  }
  const response = await fetch("/api/assess", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(serializeAssessment(bundle.inputSchema, mode.value, values())),
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || "Assessment failed");
  renderResult(payload);
}


function clearAssessment() {
  form.reset();
  mode.value = "PRE_LAB";
  renderFields();
  result.replaceChildren();
  mode.focus();
}


async function init() {
  bundle = await loadWebBundle();
  renderFields();
  mode.addEventListener("change", renderFields);
  form.addEventListener("submit", (event) => submit(event).catch((error) => {
    result.innerHTML = `<div class="callout callout-risk"><strong>Assessment unavailable.</strong><p>${error.message}</p></div>`;
  }));
  document.querySelector("#clear-assessment").addEventListener("click", clearAssessment);
  document.querySelector("#case-select").innerHTML = `<option value="">Load a synthetic case</option>${bundle.cases.map((item) => `<option value="${item.case_id}">${item.label}</option>`).join("")}`;
  document.querySelector("#case-select").addEventListener("change", (event) => {
    const selected = bundle.cases.find((item) => item.case_id === event.target.value);
    if (!selected) return;
    mode.value = selected.mode;
    renderFields();
    for (const [key, value] of Object.entries(selected.values)) {
      const control = form.elements.namedItem(key);
      if (control && value !== null) control.value = value;
    }
  });
}


init();

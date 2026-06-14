import { loadBundle } from "./data-client.js";
import { listLabels, titleCase } from "./formatters.js";
import { probabilityBars } from "./components.js";

const steps = [
  "Select scenario",
  "Review pre-lab signals",
  "See model output",
  "Understand uncertainty",
  "Take action",
];

let bundle;
let step = 1;
let selectedCase;

const descriptions = {
  "Clear single-label case": "A comparatively direct recommendation with a smaller ambiguity burden.",
  "Ambiguous multi-label case": "Several disease labels remain plausible and need confirmation.",
  "High-risk rare-label case": "An escalation case where rare-label evidence must be read cautiously.",
  "Center-shift stress case": "A scenario that foregrounds the model's limited transfer between facilities.",
};

function groupedCases() {
  const groups = new Map();
  for (const caseItem of bundle.cases) {
    if (!groups.has(caseItem.scenario)) groups.set(caseItem.scenario, caseItem);
  }
  for (const scenario of Object.keys(descriptions)) {
    if (!groups.has(scenario)) groups.set(scenario, bundle.cases[groups.size % bundle.cases.length]);
  }
  return groups;
}

function syncUrl() {
  const params = new URLSearchParams();
  if (selectedCase) params.set("case", selectedCase.case_id);
  params.set("step", String(step));
  history.replaceState(null, "", `?${params}`);
}

function renderProgress() {
  document.querySelector("#demo-step-list").innerHTML = steps.map((label, index) => {
    const number = index + 1;
    const state = number === step ? "active" : number < step ? "complete" : "";
    return `<li class="${state}">${number}. ${label}</li>`;
  }).join("");
  document.querySelector("#demo-counter").textContent = `Step ${step} of 5`;
  document.querySelector("#demo-case").textContent = selectedCase?.case_id || "Choose a scenario";
  document.querySelector("#demo-back").disabled = step === 1;
  document.querySelector("#demo-next").textContent = step === 5 ? "Open full evidence" : "Continue";
}

function callout(text) {
  return `<aside class="callout callout-warn"><strong>Why this matters</strong><br>${text}</aside>`;
}

function renderStep() {
  const content = document.querySelector("#demo-content");
  if (step === 1) {
    const groups = groupedCases();
    content.innerHTML = `<p class="section-kicker">Choose a simulated presentation scenario</p><h1>Which decision pattern should we inspect?</h1><p class="view-lede">These are curated anonymized examples, not identifiable patients and not live inference.</p><div class="scenario-grid">${[...groups].map(([scenario, caseItem]) => `<button class="scenario-option ${selectedCase?.case_id === caseItem.case_id ? "selected" : ""}" data-case="${caseItem.case_id}" type="button"><strong>${scenario}</strong><span>${descriptions[scenario]}</span></button>`).join("")}</div>${callout("Scenario labels help a first-time reviewer recognize an informative case without searching through hundreds of opaque identifiers.")}`;
    content.querySelectorAll("[data-case]").forEach((button) => button.addEventListener("click", () => {
      selectedCase = bundle.cases.find((item) => item.case_id === button.dataset.case);
      render();
    }));
  } else if (step === 2) {
    content.innerHTML = `<p class="section-kicker">Pre-lab evidence only</p><h1>Review the signal groups available before confirmation.</h1><p class="view-lede">The public prototype groups anonymized features instead of exposing 82 raw columns.</p><div class="grid grid-3"><article class="panel panel-border"><h3>Demographics</h3><p>Age band, sex, and facility context.</p></article><article class="panel panel-border"><h3>Symptoms</h3><p>Fever pattern, pain, bleeding, gastrointestinal and neurological signals.</p></article><article class="panel panel-border"><h3>Vitals and availability</h3><p>Observed vital signs plus explicit missingness indicators.</p></article></div>${callout("Stage gating prevents laboratory or disease-restatement fields from making the deployable model look unrealistically strong.")}`;
  } else if (step === 3) {
    content.innerHTML = `<p class="section-kicker">${selectedCase.case_id} · calibrated output</p><h1>Each label has its own decision threshold.</h1><p class="view-lede">Coral bars are above the operational threshold. The amber marker shows the threshold used for that disease.</p><div class="panel">${probabilityBars(selectedCase, bundle.dashboard.summary.active_labels, bundle.dashboard.thresholds)}</div>${callout("False-negative costs differ by disease. A global 0.50 threshold would silently contradict the published operational policy.")}`;
  } else if (step === 4) {
    const conformal = listLabels(selectedCase.conformal_set);
    content.innerHTML = `<p class="section-kicker">${selectedCase.uncertainty_category} uncertainty</p><h1>The model keeps ${conformal.length} plausible labels in view.</h1><div class="panel"><h2>Conformal set</h2><p>${conformal.map((label) => `<span class="tag">${titleCase(label)}</span>`).join(" ")}</p><p>This set is an uncertainty boundary, not a list of confirmed diagnoses. Larger sets indicate ambiguity and increase the need for review or confirmatory testing.</p></div>${callout("Conformal prediction gives the system a structured way to abstain instead of forcing false certainty.")}`;
  } else {
    content.innerHTML = `<p class="section-kicker">${selectedCase.case_id} · decision support</p><h1>${selectedCase.triage_category}</h1><div class="grid grid-2"><article class="panel"><h2>Recommended next step</h2><p>${selectedCase.triage_category.includes("Urgent") ? "Escalate for prompt clinician assessment and confirm capacity for urgent review." : "Route for clinician review and confirmatory testing according to local protocol."}</p></article><article class="panel"><h2>Resource implication</h2><p>This case contributes to both confirmatory-test demand and the human-review queue. Capacity projections are scenarios, not staffing prescriptions.</p></article></div>${callout("Orange and red priorities require human review. VECTRA-X supports allocation decisions but does not diagnose or prescribe treatment.")}`;
  }
  renderProgress();
  syncUrl();
}

function render() {
  if (!selectedCase) selectedCase = bundle.cases[0];
  renderStep();
}

async function init() {
  bundle = await loadBundle();
  const params = new URLSearchParams(location.search);
  selectedCase = bundle.cases.find((item) => item.case_id === params.get("case")) || bundle.cases[0];
  step = Math.min(5, Math.max(1, Number(params.get("step")) || 1));
  document.querySelector("#demo-back").addEventListener("click", () => { step = Math.max(1, step - 1); render(); });
  document.querySelector("#demo-next").addEventListener("click", () => {
    if (step === 5) location.href = "dashboard.html#overview";
    else { step += 1; render(); }
  });
  document.querySelector("#restart-demo").addEventListener("click", () => { step = 1; selectedCase = bundle.cases[0]; render(); });
  render();
}

init().catch((error) => {
  document.querySelector("#demo-content").innerHTML = `<div class="callout callout-risk"><strong>Demo data unavailable.</strong><br>${error.message}</div>`;
});

import { loadWebBundle } from "./data-client.js";


const steps = [
  "Choose a synthetic case",
  "Review anonymous inputs",
  "Run the locked assessment",
  "Inspect uncertainty and abstention",
  "Return to scientific evidence",
];
let index = 0;
let bundle;
let selectedCaseIndex = 0;


const caseSummary = (caseItem) => {
  const populated = Object.values(caseItem.values || {}).filter((value) => value !== null && value !== "").length;
  const total = Object.keys(caseItem.values || {}).length;
  if (caseItem.case_id === "SYNTH-MISSING") return `${populated} of ${total} fields populated / missing-input review`;
  if (caseItem.case_id === "SYNTH-OOD") return `${populated} of ${total} fields populated / out-of-range guardrail`;
  return `${populated} of ${total} fields populated / complete pre-lab example`;
};


function renderScenarioPicker() {
  return `<h1>Choose an anonymous synthetic scenario.</h1>
    <p>${bundle.evidence.safe_scope}</p>
    <div class="scenario-grid">${bundle.cases.map((caseItem, caseIndex) => `
      <button class="scenario-option ${caseIndex === selectedCaseIndex ? "selected" : ""}" type="button" data-case-index="${caseIndex}" aria-pressed="${caseIndex === selectedCaseIndex}">
        <strong>${caseItem.label}</strong>
        <span>${caseSummary(caseItem)}</span>
      </button>`).join("")}</div>`;
}


function bindScenarioPicker() {
  document.querySelectorAll("[data-case-index]").forEach((button) => {
    button.addEventListener("click", () => {
      selectedCaseIndex = Number(button.dataset.caseIndex);
      render();
    });
  });
}


function render() {
  document.querySelector("#demo-step-list").innerHTML = steps.map((step, stepIndex) =>
    `<li class="${stepIndex === index ? "active" : ""}">${step}</li>`
  ).join("");
  document.querySelector("#demo-counter").textContent = `Step ${index + 1} of ${steps.length}`;
  const caseItem = bundle.cases[selectedCaseIndex] || bundle.cases[0];
  const content = [
    renderScenarioPicker(),
    `<h1>${caseItem.label}</h1><p>This case is marked <strong>${caseItem.provenance}</strong> and does not reproduce a patient row.</p>`,
    `<h1>Use the same endpoint as manual entry.</h1><p>No expected output is embedded in this page.</p><a class="button button-primary" href="assessment.html">Open live assessment</a>`,
    `<h1>Mandatory review is a first-class result.</h1><p>Missingness, out-of-distribution values, uncertainty, and uninformative prediction sets can force abstention.</p>`,
    `<h1>Scenario outputs remain assumption-bound.</h1><p>They are projected review and testing demand, not observed outcomes or savings.</p><a class="button button-secondary" href="dashboard.html#limitations">Review deployment gates</a>`,
  ];
  document.querySelector("#demo-content").innerHTML = content[index];
  if (index === 0) bindScenarioPicker();
  document.querySelector("#demo-case").textContent = index === 0 ? "Choose a scenario" : caseItem.label;
  document.querySelector("#demo-back").disabled = index === 0;
  document.querySelector("#demo-next").textContent = index === steps.length - 1 ? "Restart" : "Continue";
}


loadWebBundle().then((loaded) => {
  bundle = loaded;
  document.querySelector("#demo-next").addEventListener("click", () => {
    index = index === steps.length - 1 ? 0 : index + 1;
    render();
  });
  document.querySelector("#demo-back").addEventListener("click", () => {
    index = Math.max(0, index - 1);
    render();
  });
  document.querySelector("#restart-demo").addEventListener("click", () => {
    index = 0;
    render();
  });
  render();
});

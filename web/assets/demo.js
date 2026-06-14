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


function render() {
  document.querySelector("#demo-step-list").innerHTML = steps.map((step, stepIndex) =>
    `<li class="${stepIndex === index ? "active" : ""}">${step}</li>`
  ).join("");
  document.querySelector("#demo-counter").textContent = `Step ${index + 1} of ${steps.length}`;
  const caseItem = bundle.cases[index % bundle.cases.length];
  const content = [
    `<h1>Choose an anonymous synthetic scenario.</h1><p>${bundle.evidence.safe_scope}</p>`,
    `<h1>${caseItem.label}</h1><p>This case is marked <strong>${caseItem.provenance}</strong> and does not reproduce a patient row.</p>`,
    `<h1>Use the same endpoint as manual entry.</h1><p>No expected output is embedded in this page.</p><a class="button button-primary" href="assessment.html">Open live assessment</a>`,
    `<h1>Mandatory review is a first-class result.</h1><p>Missingness, out-of-distribution values, uncertainty, and uninformative prediction sets can force abstention.</p>`,
    `<h1>Scenario outputs remain assumption-bound.</h1><p>They are projected review and testing demand, not observed outcomes or savings.</p><a class="button button-secondary" href="dashboard.html#limitations">Review deployment gates</a>`,
  ];
  document.querySelector("#demo-content").innerHTML = content[index];
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

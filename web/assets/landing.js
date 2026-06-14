import { loadJson } from "./data-client.js";
import { percent } from "./formatters.js";

async function init() {
  const [dashboard, manifest] = await Promise.all([
    loadJson("data/dashboard.json"),
    loadJson("data/manifest.json"),
  ]);
  const metrics = dashboard.summary.test_metrics.PRE_LAB;
  const conformal = dashboard.summary.conformal;
  const coinfection = dashboard.summary.coinfection;
  const values = [
    ["Macro-F1", metrics.macro_f1.toFixed(2), "Held-out test · balanced across labels"],
    ["Macro-recall", metrics.macro_recall.toFixed(2), "Held-out test · sensitivity focus"],
    ["Conformal coverage", percent(conformal.overall_coverage), "Target 90% · rare-label caveat"],
    ["Co-infection AUC", coinfection.roc_auc.toFixed(2), "Cohort-level detector"],
  ];
  document.querySelector("#landing-metrics").innerHTML = values.map(([label, value, source]) =>
    `<article class="metric"><span>${label}</span><strong>${value}</strong><small>${source}</small></article>`,
  ).join("");
  document.querySelector("#landing-source").textContent =
    `${manifest.evaluation_split} · cohort n=${manifest.cohort_size} · ${manifest.model_track} ${manifest.model_name} · generated ${manifest.generated_at.slice(0, 10)}`;
}

init().catch(() => {
  document.querySelector("#landing-metrics").innerHTML =
    `<p class="callout">Canonical metrics are temporarily unavailable. The guided explanation remains accessible.</p>`;
});

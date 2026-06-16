import { loadWebBundle } from "./data-client.js";


loadWebBundle().then(({ evidence, manifest }) => {
  const summary = evidence.primary_track_summary;
  document.querySelector("#landing-metrics").innerHTML = `
    <article><strong>${summary.macro_f1.toFixed(3)}</strong><span>PRE_LAB macro-F1</span></article>
    <article><strong>${summary.micro_f1.toFixed(3)}</strong><span>PRE_LAB micro-F1</span></article>
    <article><strong>${summary.macro_pr_auc.toFixed(3)}</strong><span>PRE_LAB macro PR-AUC</span></article>`;
  document.querySelector("#landing-source").textContent =
    `Locked run ${manifest.notebook_run_id} · policy ${manifest.analysis_policy_id}. Every public result is generated from this release.`;
}).catch((error) => {
  document.querySelector("#landing-metrics").innerHTML =
    `<p class="callout callout-risk">${error.message}</p>`;
});

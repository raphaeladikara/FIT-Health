import { loadWebBundle } from "./data-client.js";


loadWebBundle().then(({ evidence, manifest }) => {
  const summary = evidence.primary_track_summary;
  document.querySelector("#landing-metrics").innerHTML = `
    <article class="metric"><span>PRE_LAB macro-F1</span><strong>${summary.macro_f1.toFixed(3)}</strong><small>Balances all five scored labels, including rare labels.</small></article>
    <article class="metric"><span>PRE_LAB micro-F1</span><strong>${summary.micro_f1.toFixed(3)}</strong><small>Reflects pooled label decisions on the frozen test.</small></article>
    <article class="metric"><span>PRE_LAB macro PR-AUC</span><strong>${summary.macro_pr_auc.toFixed(3)}</strong><small>Ranking quality under class imbalance.</small></article>`;
  document.querySelector("#landing-source").textContent =
    `Locked run ${manifest.notebook_run_id} / policy ${manifest.analysis_policy_id}. Every public result is generated from this release.`;
}).catch((error) => {
  document.querySelector("#landing-metrics").innerHTML =
    `<p class="callout callout-risk">${error.message}</p>`;
});

import { loadWebBundle } from "./data-client.js";


loadWebBundle().then(({ evidence, manifest }) => {
  const counts = evidence.cohort_and_partitions.counts;
  document.querySelector("#landing-metrics").innerHTML = `
    <article><strong>${counts.n_supervised}</strong><span>verified supervised patients</span></article>
    <article><strong>${counts.training}</strong><span>training-pool patients</span></article>
    <article><strong>${counts.frozen_test}</strong><span>one locked frozen test</span></article>`;
  document.querySelector("#landing-source").textContent =
    `Locked run ${manifest.notebook_run_id}. Every public result is generated from this release.`;
}).catch((error) => {
  document.querySelector("#landing-metrics").innerHTML =
    `<p class="callout callout-risk">${error.message}</p>`;
});

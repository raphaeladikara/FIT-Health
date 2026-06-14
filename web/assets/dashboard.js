import { loadWebBundle } from "./data-client.js";
import { ProvenanceStrip } from "./components.js";
import {
  evaluationEvidence,
  executiveEvidence,
  fairnessEvidence,
  governanceEvidence,
  limitationsEvidence,
  uncertaintyEvidence,
} from "./evidence-views.js";
import { normalizeRoute, routeHref } from "./router.js";


const groups = [
  { label: "Scientific evidence", routes: [
    { key: "executive", label: "Executive Evidence" },
    { key: "governance", label: "Data and Leakage Governance" },
    { key: "evaluation", label: "Model Evaluation" },
    { key: "uncertainty", label: "Uncertainty and Safe Deferral" },
    { key: "fairness", label: "Fairness and Center Transfer" },
  ] },
  { label: "Decision support", routes: [
    { key: "assessment", label: "Live Assessment", href: "assessment.html" },
    { key: "scenario", label: "Scenario Prototype", href: "demo.html" },
    { key: "limitations", label: "Limitations and Deployment Gates" },
  ] },
];
const routes = groups.flatMap((group) =>
  group.routes.filter((route) => !route.href).map((route) => ({ ...route, group: group.label }))
);
let bundle;
let currentRoute = "executive";


function renderNav() {
  document.querySelector("#dashboard-nav").innerHTML = groups.map((group) =>
    `<section class="nav-group"><h2>${group.label}</h2>${group.routes.map((route) =>
      `<a href="${route.href || routeHref(route.key)}" ${route.href ? "" : `data-route="${route.key}"`}><span>${route.label}</span></a>`
    ).join("")}</section>`
  ).join("");
  document.querySelectorAll("[data-route]").forEach((link) =>
    link.addEventListener("click", (event) => {
      event.preventDefault();
      currentRoute = link.dataset.route;
      history.pushState({}, "", routeHref(currentRoute));
      renderRoute();
    })
  );
}


function renderRoute() {
  const track = document.querySelector("#model-mode").value;
  const route = routes.find((item) => item.key === currentRoute) || routes[0];
  const renderers = {
    executive: () => executiveEvidence(bundle),
    governance: () => governanceEvidence(bundle),
    evaluation: () => evaluationEvidence(bundle, track),
    uncertainty: () => uncertaintyEvidence(bundle),
    fairness: () => fairnessEvidence(bundle),
    limitations: () => limitationsEvidence(bundle),
  };
  document.querySelector("#section-group").textContent = route.group;
  document.querySelector("#section-title").textContent = route.label;
  document.querySelector("#dashboard-view").innerHTML =
    ProvenanceStrip(bundle.manifest) + renderers[route.key]();
  document.querySelectorAll("[data-route]").forEach((link) =>
    link.setAttribute("aria-current", link.dataset.route === route.key ? "page" : "false")
  );
}


async function init() {
  bundle = await loadWebBundle();
  renderNav();
  currentRoute = normalizeRoute(location.hash, routes.map((route) => route.key), "executive");
  document.querySelector("#run-status").textContent = "Locked scientific run";
  document.querySelector("#run-meta").textContent =
    `${bundle.manifest.notebook_run_id} · ${bundle.manifest.source_commit.slice(0, 12)}`;
  document.querySelector("#model-mode").addEventListener("change", () => {
    currentRoute = "evaluation";
    history.replaceState({}, "", "#evaluation");
    renderRoute();
  });
  const sidebar = document.querySelector("#sidebar");
  const backdrop = document.querySelector("#drawer-backdrop");
  const setMenu = (open) => {
    sidebar.classList.toggle("open", open);
    backdrop.classList.toggle("open", open);
    document.querySelector("#open-menu").setAttribute("aria-expanded", String(open));
  };
  document.querySelector("#open-menu").addEventListener("click", () => setMenu(true));
  document.querySelector("#close-menu").addEventListener("click", () => setMenu(false));
  backdrop.addEventListener("click", () => setMenu(false));
  window.addEventListener("hashchange", () => {
    currentRoute = normalizeRoute(location.hash, routes.map((route) => route.key), "executive");
    renderRoute();
  });
  renderRoute();
}


init().catch((error) => {
  document.querySelector("#dashboard-view").innerHTML =
    `<div class="callout callout-risk"><strong>Evidence unavailable.</strong><p>${error.message}</p></div>`;
});

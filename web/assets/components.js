import { isPositive } from "./thresholds.js";
import { number, percent, titleCase } from "./formatters.js";

export function metric(label, value, source) {
  return `<article class="metric-block"><span>${label}</span><strong>${value}</strong><small>${source}</small></article>`;
}

export function table(rows, columns) {
  if (!rows.length) return `<div class="callout">No rows match the current filters. Clear one or more filters to recover.</div>`;
  return `<div class="table-wrap"><table><thead><tr>${columns.map((column) => `<th>${column.label}</th>`).join("")}</tr></thead><tbody>${rows.map((row) => `<tr>${columns.map((column) => `<td>${column.render ? column.render(row[column.key], row) : row[column.key] ?? "N/A"}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
}

export function probabilityBars(caseItem, labels, thresholds) {
  return labels.map((label) => {
    const probability = Number(caseItem[`calprob_${label}`] || 0);
    const threshold = thresholds.values[label];
    const positive = isPositive(probability, label, thresholds);
    return `<div class="probability-row"><span>${titleCase(label)}</span><div class="probability-track" aria-label="${titleCase(label)} probability ${percent(probability)}, operational threshold ${percent(threshold)}"><div class="probability-fill ${positive ? "positive" : ""}" style="width:${probability * 100}%"></div><span class="threshold-marker" style="left:${threshold * 100}%"></span></div><span class="probability-value">${number(probability, 2)} · ${positive ? "above" : "below"}</span></div>`;
  }).join("");
}

export function dataBars(rows, valueKey, labelKey, { risk = false, max = 1 } = {}) {
  return `<div class="data-bars">${rows.map((row) => {
    const value = Number(row[valueKey] || 0);
    return `<div class="data-bar"><span>${titleCase(row[labelKey])}</span><div class="data-bar-track"><div class="data-bar-fill ${risk ? "risk" : ""}" style="width:${Math.min(100, value / max * 100)}%"></div></div><strong>${number(value, 2)}</strong></div>`;
  }).join("")}</div>`;
}

export function figure(file, alt, takeaway) {
  return `<figure class="figure"><img loading="lazy" src="figures/${file}" alt="${alt}"><figcaption>${takeaway}</figcaption></figure>`;
}

export function EvidenceScopeBadge(scope) {
  return `<span class="tag evidence-scope">${scope}</span>`;
}

export function ProvenanceStrip(manifest) {
  return `<div class="provenance-strip"><strong>Locked run ${manifest.notebook_run_id}</strong><span>Scientific schema ${manifest.scientific_schema_version}</span><span>Source ${manifest.source_commit.slice(0, 12)}</span></div>`;
}

export function SupportStatus(support, minimum = 5) {
  return `<span class="tag ${support < minimum ? "tag-risk" : ""}">${support < minimum ? "Insufficient evidence" : `${support} positives`}</span>`;
}

export function IntervalMetric(row) {
  return `<article class="metric-block"><span>${row.metric}</span><strong>${number(row.estimate, 2)}</strong><small>${number(row.lower, 2)} to ${number(row.upper, 2)} · n=${row.n_patients} · positives=${row.positive_support}</small></article>`;
}

export function DeploymentGate(gate) {
  return `<li class="deployment-gate"><span aria-hidden="true">Pending</span><strong>${gate}</strong></li>`;
}

export function ScientificCaveat(text) {
  return `<aside class="callout callout-warn"><strong>Scientific caveat:</strong> ${text}</aside>`;
}

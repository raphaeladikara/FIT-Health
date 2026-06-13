"use client";

import { Printer } from "lucide-react";

import { parseLabelSet } from "@/lib/patient-selection";
import type { Manifest, Patient } from "@/lib/types";

export function CaseReport({
  patient,
  manifest,
}: {
  patient: Patient;
  manifest: Manifest;
}) {
  const decisions = Object.entries(patient.label_decisions).sort(
    (a, b) => b[1].probability - a[1].probability,
  );
  return (
    <>
      <button type="button" className="chip print-button" onClick={() => window.print()}>
        <Printer aria-hidden="true" size={15} />
        Print case report
      </button>

      <section className="case-report" aria-hidden="true">
        <h2>VECTRA-X decision-support report</h2>
        <p className="case-report-meta">
          Anonymous {patient.case_id} · {patient.model_track} track · {patient.threshold_policy}{" "}
          threshold policy · run {manifest.run_id}
        </p>
        <p className="case-report-warn">
          Decision support only — NOT a diagnosis. No patient identifiers are included.
        </p>
        <table className="case-report-table">
          <thead>
            <tr>
              <th>Disease</th>
              <th>Probability</th>
              <th>Threshold</th>
              <th>Flagged</th>
            </tr>
          </thead>
          <tbody>
            {decisions.map(([label, d]) => (
              <tr key={label}>
                <td>{label.replace(/_/g, " ")}</td>
                <td>{(d.probability * 100).toFixed(0)}%</td>
                <td>{(d.threshold * 100).toFixed(0)}%</td>
                <td>{d.predicted ? "Yes" : "No"}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <dl>
          <dt>Triage priority</dt>
          <dd>{patient.triage_category}</dd>
          <dt>Triage score</dt>
          <dd>{patient.triage_score.toFixed(3)}</dd>
          <dt>Uncertainty</dt>
          <dd>{patient.uncertainty_level}</dd>
          <dt>Conformal caution set</dt>
          <dd>{parseLabelSet(patient.conformal_set).join(", ") || "none"}</dd>
          <dt>Recommended action</dt>
          <dd>{patient.recommended_action}</dd>
        </dl>
      </section>
    </>
  );
}

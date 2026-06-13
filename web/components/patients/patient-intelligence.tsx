"use client";

import { AlertTriangle, Gauge, HelpCircle, Layers3, ShieldCheck } from "lucide-react";
import { useMemo, useState } from "react";

import { MetricStrip } from "@/components/ui/metric-strip";
import { Panel } from "@/components/ui/panel";
import { StatusBadge } from "@/components/ui/status-badge";
import {
  parseLabelSet,
  selectRepresentativePatient,
  type RepresentativeScenario,
} from "@/lib/patient-selection";
import { titleCase } from "@/lib/format";
import type { Patient } from "@/lib/types";

const scenarios: Array<{ value: RepresentativeScenario; label: string }> = [
  { value: "highest-priority", label: "Highest priority" },
  { value: "high-uncertainty", label: "High uncertainty" },
  { value: "co-infection", label: "Potential co-infection" },
  { value: "routine", label: "Routine monitoring" },
];

export function PatientIntelligence({
  patients,
  labels,
}: {
  patients: Patient[];
  labels: string[];
}) {
  const initial = selectRepresentativePatient(patients, "highest-priority") ?? patients[0];
  const [caseId, setCaseId] = useState(initial.case_id);
  const selected = patients.find((patient) => patient.case_id === caseId) ?? initial;
  const probabilities = useMemo(
    () =>
      labels.map((label) => ({
        label,
        value: Number(selected[`calprob_${label}`] ?? 0),
      })),
    [labels, selected],
  );

  function chooseScenario(value: RepresentativeScenario) {
    const patient = selectRepresentativePatient(patients, value);
    if (patient) setCaseId(patient.case_id);
  }

  return (
    <>
      <div className="controls-row">
        <label className="field">
          Representative scenario
          <select onChange={(event) => chooseScenario(event.target.value as RepresentativeScenario)}>
            {scenarios.map((scenario) => (
              <option value={scenario.value} key={scenario.value}>{scenario.label}</option>
            ))}
          </select>
        </label>
        <label className="field">
          Anonymous case
          <select value={caseId} onChange={(event) => setCaseId(event.target.value)}>
            {patients.map((patient) => (
              <option key={patient.case_id}>{patient.case_id}</option>
            ))}
          </select>
        </label>
      </div>
      <MetricStrip
        items={[
          { label: "Triage priority", value: selected.triage_category.replace(" Priority", ""), detail: selected.case_id, tone: "urgent", icon: AlertTriangle },
          { label: "Triage score", value: selected.triage_score.toFixed(3), detail: "Operational ranking", tone: "primary", icon: Gauge },
          { label: "Uncertainty", value: titleCase(selected.uncertainty_level), detail: "Entropy-derived review need", tone: "review", icon: HelpCircle },
          { label: "Co-infection risk", value: selected.coinfection_prob.toFixed(2), detail: "Separate detector", tone: "violet", icon: Layers3 },
          { label: "Caution set", value: parseLabelSet(selected.conformal_set).length, detail: "Plausible labels", tone: "primary", icon: ShieldCheck },
        ]}
      />
      <div className="workspace-grid">
        <div>
          <Panel title="Calibrated disease probabilities" description="Probability after calibration. These values are risk signals, not diagnoses.">
            <div className="probability-list">
              {probabilities.map(({ label, value }) => (
                <div className="probability-row" key={label}>
                  <span>{titleCase(label)}</span>
                  <div
                    className="probability-track"
                    role="img"
                    aria-label={`${titleCase(label)} probability ${(value * 100).toFixed(1)} percent`}
                  >
                    <div className="probability-fill" style={{ width: `${value * 100}%` }} />
                  </div>
                  <strong>{(value * 100).toFixed(0)}%</strong>
                </div>
              ))}
            </div>
          </Panel>
          <Panel title="Explanation boundary" description="The current public artifact contains cohort-level feature importance.">
            <p className="insight">
              Feature contributions describe model behavior, not medical causality.
              Patient-specific explanations are intentionally withheld when they cannot be
              linked to an out-of-fold decision record with sufficient provenance.
            </p>
          </Panel>
        </div>
        <Panel title="Decision-support record" description="Four separate outputs keep probability, uncertainty, priority, and action distinct.">
          <dl className="record-list">
            <div><dt>Priority</dt><dd><StatusBadge value={selected.triage_category} /></dd></div>
            <div><dt>Predicted signals</dt><dd>{selected.predicted_labels}</dd></div>
            <div><dt>Uncertainty-aware caution set</dt><dd>{selected.conformal_set}</dd></div>
            <div><dt>Recommended human action</dt><dd>{selected.recommended_action}</dd></div>
          </dl>
        </Panel>
      </div>
    </>
  );
}

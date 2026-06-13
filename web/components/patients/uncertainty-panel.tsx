import { parseLabelSet } from "@/lib/patient-selection";
import type { Patient } from "@/lib/types";

export function UncertaintyPanel({ patient }: { patient: Patient }) {
  const cautionSet = parseLabelSet(patient.conformal_set);
  return (
    <div className="uncertainty-panel">
      <div className="uncertainty-row">
        <span className="uncertainty-key">Uncertainty level</span>
        <span className="demo-uncertainty-pill" data-level={patient.uncertainty_level}>
          {patient.uncertainty_level}
        </span>
      </div>
      <div className="uncertainty-row">
        <span className="uncertainty-key">Co-infection detector</span>
        <span className="uncertainty-coinf">{(patient.coinfection_prob * 100).toFixed(0)}%</span>
      </div>
      <div className="uncertainty-block">
        <span className="uncertainty-key">Conformal caution set</span>
        <div className="chip-row">
          {cautionSet.length ? (
            cautionSet.map((label) => (
              <span className="chip demo-caution-chip" key={label}>
                {label.replace(/_/g, " ")}
              </span>
            ))
          ) : (
            <span className="demo-caution-empty">Confident — no labels retained.</span>
          )}
        </div>
      </div>
      <p className="uncertainty-note">
        A wider caution set is an explicit request for human review. Conformal coverage is
        not guaranteed equally across labels.
      </p>
    </div>
  );
}

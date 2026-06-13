import { Monogram } from "@/components/ui/monogram";
import { StatusBadge } from "@/components/ui/status-badge";
import { selectRepresentativePatient } from "@/lib/patient-selection";
import { thresholdMarkerPercent } from "@/lib/thresholds";
import type { DashboardData } from "@/lib/types";

export function PatientStep({ data }: { data: DashboardData }) {
  const patient = selectRepresentativePatient(data.patients, "highest-priority");
  if (!patient) {
    return <p className="demo-read">No patient records are available in this artifact.</p>;
  }
  const decisions = Object.entries(patient.label_decisions).sort(
    (a, b) => b[1].probability - a[1].probability,
  );

  return (
    <>
      <div className="demo-visual">
        <div className="demo-patient-head">
          <Monogram size="md" caseId={patient.case_id} category={patient.triage_category} />
          <div>
            <strong>{patient.case_id}</strong>
            <StatusBadge value={patient.triage_category} />
          </div>
        </div>
        <div className="probability-list">
          {decisions.map(([label, decision]) => (
            <div className="probability-row" key={label}>
              <span>{label.replace(/_/g, " ")}</span>
              <span
                className="probability-track"
                data-over={decision.predicted}
                title={`threshold ${decision.threshold.toFixed(2)}`}
              >
                <span
                  className="probability-fill"
                  style={{ width: `${Math.min(100, decision.probability * 100)}%` }}
                />
                <span
                  className="probability-threshold"
                  style={{ left: `${thresholdMarkerPercent(decision.threshold)}%` }}
                />
              </span>
              <strong>
                {(decision.probability * 100).toFixed(0)}
                <small className="prob-threshold-note">/ thr {decision.threshold.toFixed(2)}</small>
              </strong>
            </div>
          ))}
        </div>
      </div>
      <div className="demo-read">
        <h2>What this shows</h2>
        <p>
          Each disease is judged against <strong>its own tuned threshold</strong> (the
          thin marker), never a single fixed 0.50 cutoff. A label is flagged only when
          its calibrated probability clears that marker, so the prediction shown always
          agrees with the bar.
        </p>
      </div>
      <p className="demo-limit">
        These are calibrated operating points for triage support — not a diagnosis. A
        clinician confirms before any action.
      </p>
    </>
  );
}

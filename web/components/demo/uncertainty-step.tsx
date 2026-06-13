import { Monogram } from "@/components/ui/monogram";
import { parseLabelSet, selectRepresentativePatient } from "@/lib/patient-selection";
import type { DashboardData } from "@/lib/types";

export function UncertaintyStep({ data }: { data: DashboardData }) {
  const patient =
    selectRepresentativePatient(data.patients, "high-uncertainty") ??
    selectRepresentativePatient(data.patients, "highest-priority");
  if (!patient) {
    return <p className="demo-read">No patient records are available in this artifact.</p>;
  }
  const cautionSet = parseLabelSet(patient.conformal_set);

  return (
    <>
      <div className="demo-visual">
        <div className="demo-patient-head">
          <Monogram size="md" caseId={patient.case_id} category={patient.triage_category} />
          <div>
            <strong>{patient.case_id}</strong>
            <span className="demo-uncertainty-pill" data-level={patient.uncertainty_level}>
              {patient.uncertainty_level} uncertainty
            </span>
          </div>
        </div>
        <div className="demo-caution">
          <span className="demo-caution-label">Conformal caution set</span>
          <div className="chip-row">
            {cautionSet.length ? (
              cautionSet.map((label) => (
                <span className="chip demo-caution-chip" key={label}>
                  {label.replace(/_/g, " ")}
                </span>
              ))
            ) : (
              <span className="demo-caution-empty">No labels retained — confident.</span>
            )}
          </div>
        </div>
      </div>
      <div className="demo-read">
        <h2>What this shows</h2>
        <p>
          When the model is unsure, the conformal caution set keeps{" "}
          <strong>every plausible disease</strong> rather than guessing. A wider set is
          an explicit, visible request for a human to review — not a silent error.
        </p>
      </div>
      <p className="demo-limit">
        Conformal coverage is not guaranteed equally across labels — typhoid coverage in
        particular is below target, which the trust center states openly.
      </p>
    </>
  );
}

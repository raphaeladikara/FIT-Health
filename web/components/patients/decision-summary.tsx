import { Monogram } from "@/components/ui/monogram";
import { StatusBadge } from "@/components/ui/status-badge";
import { triageTone } from "@/lib/triage";
import type { Patient } from "@/lib/types";

/** Hero band toned by the patient's actual triage category (routine never reads urgent). */
export function DecisionSummary({ patient }: { patient: Patient }) {
  return (
    <section className="decision-summary" data-tone={triageTone(patient.triage_category)}>
      <Monogram size="md" caseId={patient.case_id} category={patient.triage_category} />
      <div className="decision-summary-main">
        <p className="decision-summary-eyebrow">Decision-support record · {patient.case_id}</p>
        <div className="decision-summary-badges">
          <StatusBadge value={patient.triage_category} />
          <span className="decision-summary-track">{patient.model_track} · {patient.threshold_policy} policy</span>
        </div>
        <p className="decision-summary-action">{patient.recommended_action}</p>
      </div>
      <div className="decision-summary-score">
        <span>Triage score</span>
        <strong>{patient.triage_score.toFixed(3)}</strong>
      </div>
    </section>
  );
}

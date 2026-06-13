import type { Patient } from "@/lib/types";

export function ActionRecord({ patient }: { patient: Patient }) {
  return (
    <dl className="record-list">
      <div>
        <dt>Recommended human action</dt>
        <dd>{patient.recommended_action}</dd>
      </div>
      <div>
        <dt>Flagged disease signals</dt>
        <dd>{patient.predicted_labels}</dd>
      </div>
      <div>
        <dt>Model track</dt>
        <dd>{patient.model_track} (deployable, pre-laboratory)</dd>
      </div>
      <div>
        <dt>Record source</dt>
        <dd>{patient.record_source.replace(/_/g, " ")}</dd>
      </div>
    </dl>
  );
}

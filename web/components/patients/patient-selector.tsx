import { Monogram } from "@/components/ui/monogram";
import type { RepresentativeScenario } from "@/lib/patient-selection";
import type { Patient } from "@/lib/types";

const SCENARIOS: Array<{ value: RepresentativeScenario; label: string }> = [
  { value: "highest-priority", label: "Highest priority" },
  { value: "high-uncertainty", label: "High uncertainty" },
  { value: "co-infection", label: "Potential co-infection" },
  { value: "routine", label: "Routine monitoring" },
];

export function PatientSelector({
  patients,
  selected,
  activeScenario,
  onScenario,
  onCase,
}: {
  patients: Patient[];
  selected: Patient;
  activeScenario: RepresentativeScenario | null;
  onScenario: (scenario: RepresentativeScenario) => void;
  onCase: (caseId: string) => void;
}) {
  return (
    <div className="patient-selector">
      <div className="chip-row" role="group" aria-label="Representative scenarios">
        {SCENARIOS.map((option) => (
          <button
            key={option.value}
            type="button"
            className="chip"
            aria-pressed={activeScenario === option.value}
            onClick={() => onScenario(option.value)}
          >
            {option.label}
          </button>
        ))}
      </div>
      <div className="patient-selector-pick">
        <Monogram caseId={selected.case_id} category={selected.triage_category} />
        <label className="field">
          Anonymous case
          <select value={selected.case_id} onChange={(event) => onCase(event.target.value)}>
            {patients.map((patient) => (
              <option key={patient.case_id}>{patient.case_id}</option>
            ))}
          </select>
        </label>
      </div>
    </div>
  );
}

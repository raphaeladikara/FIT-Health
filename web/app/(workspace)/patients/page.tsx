import { PatientIntelligence } from "@/components/patients/patient-intelligence";
import { PageHeader } from "@/components/ui/page-header";
import { SafetyNote } from "@/components/ui/safety-note";
import type { RepresentativeScenario } from "@/lib/patient-selection";
import { loadDashboardData } from "@/lib/data";

const SCENARIOS: RepresentativeScenario[] = [
  "highest-priority",
  "high-uncertainty",
  "co-infection",
  "routine",
];

export default async function PatientsPage({
  searchParams,
}: {
  searchParams: Promise<{ case?: string; scenario?: string }>;
}) {
  const [{ patients, summary, manifest }, params] = await Promise.all([
    loadDashboardData(),
    searchParams,
  ]);
  const initialScenario = SCENARIOS.includes(params.scenario as RepresentativeScenario)
    ? (params.scenario as RepresentativeScenario)
    : undefined;
  return (
    <>
      <PageHeader
        title="Patient Review"
        description="Inspect one anonymous decision-support record at a time: calibrated per-disease risk against tuned thresholds, ambiguity, co-infection risk, and the next human action."
        aside={<SafetyNote compact />}
      />
      <PatientIntelligence
        patients={patients}
        labels={summary.active_labels}
        manifest={manifest}
        initialCaseId={params.case}
        initialScenario={initialScenario}
      />
    </>
  );
}

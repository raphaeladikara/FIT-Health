import { PatientIntelligence } from "@/components/patients/patient-intelligence";
import { PageHeader } from "@/components/ui/page-header";
import { SafetyNote } from "@/components/ui/safety-note";
import { loadDashboardData } from "@/lib/data";

export default async function PatientsPage({
  searchParams,
}: {
  searchParams: Promise<{ case?: string }>;
}) {
  const [{ patients, summary }, { case: caseParam }] = await Promise.all([
    loadDashboardData(),
    searchParams,
  ]);
  return (
    <>
      <PageHeader
        title="Patient Intelligence"
        description="Inspect one anonymous decision-support record at a time, including calibrated probabilities, ambiguity, co-infection risk, and the next human action."
        aside={<SafetyNote compact />}
      />
      <PatientIntelligence
        patients={patients}
        labels={summary.active_labels}
        initialCaseId={caseParam}
      />
    </>
  );
}

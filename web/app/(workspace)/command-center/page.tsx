import { CommandCenter } from "@/components/command-center/command-center";
import { PageHeader } from "@/components/ui/page-header";
import { SafetyNote } from "@/components/ui/safety-note";
import { loadDashboardData } from "@/lib/data";

export default async function CommandCenterPage() {
  const { patients, manifest } = await loadDashboardData();
  return (
    <>
      <PageHeader
        title="Outbreak Triage Command Center"
        description="Turn calibrated multi-label risk, uncertainty, and limited capacity into a clear queue for human action."
        aside={<SafetyNote compact />}
      />
      <CommandCenter patients={patients} manifest={manifest} />
    </>
  );
}

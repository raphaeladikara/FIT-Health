import { ResourceWorkspace } from "@/components/resources/resource-workspace";
import { PageHeader } from "@/components/ui/page-header";
import { SafetyNote } from "@/components/ui/safety-note";
import { loadDashboardData } from "@/lib/data";

export default async function ResourcesPage({
  searchParams,
}: {
  searchParams: Promise<{ preset?: string }>;
}) {
  const [{ patients, evidence }, { preset }] = await Promise.all([
    loadDashboardData(),
    searchParams,
  ]);
  return (
    <>
      <PageHeader
        title="Resource Scenarios"
        description="A transparent simulator: change capacity and watch who receives scarce tests, who is waitlisted, and where shortfalls remain. Demand assumptions are clinically unvalidated."
        aside={<SafetyNote compact />}
      />
      <ResourceWorkspace
        patients={patients}
        policyTradeoff={evidence.threshold_policy_tradeoff}
        initialPreset={preset}
      />
    </>
  );
}

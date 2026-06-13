import { ResourceWorkspace } from "@/components/resources/resource-workspace";
import { PageHeader } from "@/components/ui/page-header";
import { loadDashboardData } from "@/lib/data";

export default async function ResourcesPage() {
  const { patients, evidence } = await loadDashboardData();
  return (
    <>
      <PageHeader
        title="Resource Allocation"
        description="See who receives scarce tests and review capacity first, and which operational gaps remain under each capacity scenario."
      />
      <ResourceWorkspace
        patients={patients}
        policyTradeoff={evidence.threshold_policy_tradeoff}
      />
    </>
  );
}

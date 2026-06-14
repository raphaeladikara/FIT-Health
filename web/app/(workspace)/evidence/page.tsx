import { EvidenceWorkspace } from "@/components/evidence/evidence-workspace";
import { PageHeader } from "@/components/ui/page-header";
import { SafetyNote } from "@/components/ui/safety-note";
import { resolveEvidenceSection } from "@/lib/evidence-sections";
import { loadDashboardData } from "@/lib/data";

export default async function EvidencePage({
  searchParams,
}: {
  searchParams: Promise<{ section?: string }>;
}) {
  const [{ summary, evidence, manifest }, { section }] = await Promise.all([
    loadDashboardData(),
    searchParams,
  ]);
  const current = resolveEvidenceSection(section);
  return (
    <>
      <PageHeader
        title="Trust Center"
        description="Six honest questions about the model — discrimination, missed cases, calibration, abstention, generalization, and leakage control — each with what it cannot claim."
        aside={<SafetyNote compact />}
      />
      <EvidenceWorkspace
        summary={summary}
        evidence={evidence}
        manifest={manifest}
        section={current.slug}
      />
    </>
  );
}

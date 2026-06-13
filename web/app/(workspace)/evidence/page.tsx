import { Activity, Crosshair, Gauge, ShieldCheck, Users } from "lucide-react";

import { EvidenceWorkspace } from "@/components/evidence/evidence-workspace";
import { MetricStrip } from "@/components/ui/metric-strip";
import { PageHeader } from "@/components/ui/page-header";
import { formatMetric } from "@/lib/format";
import { loadDashboardData } from "@/lib/data";

export default async function EvidencePage() {
  const { summary, evidence, manifest } = await loadDashboardData();
  const metrics = summary.test_metrics.PRE_LAB ?? {};
  return (
    <>
      <PageHeader
        title="Trust & Evidence"
        description="Separate discrimination, missed-case safety, probability trust, subgroup behavior, and generalization instead of compressing trust into one score."
      />
      <MetricStrip
        items={[
          { label: "Macro F1", value: formatMetric(metrics.macro_f1), detail: "Held-out PRE_LAB", tone: "primary", icon: Activity },
          { label: "Micro F1", value: formatMetric(metrics.micro_f1), detail: "Held-out PRE_LAB", tone: "primary", icon: Gauge },
          { label: "Macro recall", value: formatMetric(metrics.macro_recall), detail: "Missed-case sensitivity", tone: "review", icon: Crosshair },
          { label: "Macro PR-AUC", value: formatMetric(metrics.macro_pr_auc), detail: "Imbalance-aware ranking", tone: "confirm", icon: ShieldCheck },
          { label: "Patients scored", value: manifest.patient_count, detail: "Out-of-fold cohort records", tone: "primary", icon: Users },
        ]}
      />
      <EvidenceWorkspace summary={summary} evidence={evidence} />
    </>
  );
}

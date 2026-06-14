import { PerLabelBar, type LabelDatum } from "@/components/charts/per-label-bar";
import { TONE_HEX } from "@/components/charts/chart-kit";
import { EvidenceNavigation } from "@/components/evidence/evidence-navigation";
import { EvidenceSection } from "@/components/evidence/evidence-section";
import { MetricWithInterval } from "@/components/evidence/metric-with-interval";
import { SupportAwareTable } from "@/components/evidence/support-aware-table";
import { Panel } from "@/components/ui/panel";
import { ProvenancePanel } from "@/components/ui/provenance-panel";
import {
  centerTransferInsight,
  conformalInsight,
  leakageInsight,
  missedCaseInsight,
  performanceInsight,
} from "@/lib/evidence-insights";
import { intervalForMetric } from "@/lib/landing-content";
import type { EvidenceSectionSlug } from "@/lib/evidence-sections";
import { titleCase } from "@/lib/format";
import type { Evidence, EvidenceInsight, Manifest, Summary } from "@/lib/types";

const HEADLINE_METRICS = ["macro_f1", "micro_f1", "macro_recall", "macro_pr_auc"];

export function EvidenceWorkspace({
  summary,
  evidence,
  manifest,
  section,
}: {
  summary: Summary;
  evidence: Evidence;
  manifest: Manifest;
  section: EvidenceSectionSlug;
}) {
  return (
    <div className="evidence">
      <EvidenceNavigation current={section} />
      {section === "performance" ? <Performance evidence={evidence} /> : null}
      {section === "missed-cases" ? <MissedCases evidence={evidence} /> : null}
      {section === "calibration" ? <Calibration evidence={evidence} /> : null}
      {section === "abstention" ? <Abstention evidence={evidence} /> : null}
      {section === "generalization" ? <Generalization evidence={evidence} /> : null}
      {section === "leakage" ? <Leakage summary={summary} evidence={evidence} /> : null}

      <Panel title="Artifact provenance" description="Every metric on this page comes from this run.">
        <ProvenancePanel manifest={manifest} />
      </Panel>
    </div>
  );
}

function Performance({ evidence }: { evidence: Evidence }) {
  const macroF1 = intervalForMetric(evidence.confidence_intervals, "macro_f1");
  return (
    <EvidenceSection
      question="How well does it discriminate?"
      insight={performanceInsight(macroF1.value, macroF1.interval)}
    >
      <div className="metric-ci-grid">
        {HEADLINE_METRICS.map((metric) => {
          const m = intervalForMetric(evidence.confidence_intervals, metric);
          return (
            <MetricWithInterval
              key={metric}
              label={titleCase(metric)}
              value={m.value}
              interval={m.interval}
            />
          );
        })}
      </div>
      <SupportAwareTable
        rows={evidence.model_leaderboard}
        columns={["track", "model", "macro_f1", "micro_f1", "macro_pr_auc", "macro_recall"]}
      />
    </EvidenceSection>
  );
}

function MissedCases({ evidence }: { evidence: Evidence }) {
  const preLab = evidence.per_label_metrics.filter((row) => row.track === "PRE_LAB");
  const recall: LabelDatum[] = preLab
    .map((row) => ({ label: titleCase(String(row.label ?? "")), value: Number(row.recall) }))
    .filter((datum) => Number.isFinite(datum.value));
  return (
    <EvidenceSection
      question="Which cases does it miss?"
      insight={missedCaseInsight(evidence.per_label_metrics)}
    >
      {recall.length ? <PerLabelBar data={recall} unit="Recall" color={TONE_HEX.primary} /> : null}
      <SupportAwareTable
        rows={preLab}
        columns={["label", "support_pos", "recall", "precision", "false_negative_rate", "fn"]}
        supportColumn="support_pos"
      />
    </EvidenceSection>
  );
}

function Calibration({ evidence }: { evidence: Evidence }) {
  const insight: EvidenceInsight = {
    title: "Probabilities are calibrated, but only on a small split",
    summary:
      "Brier score and expected calibration error are reported per disease and variant.",
    implication:
      "Lower Brier and ECE mean the probabilities can be read as risk, not just rank order.",
    cannotClaim:
      "We cannot claim calibration holds on populations unlike this small held-out cohort.",
    severity: "neutral",
    source: "calibration_metrics",
  };
  return (
    <EvidenceSection question="Can I trust the probabilities?" insight={insight}>
      <SupportAwareTable
        rows={evidence.calibration_metrics}
        columns={["label", "base_rate", "brier", "ece", "variant"]}
        supportColumn="base_rate"
        lowSupport={0}
      />
    </EvidenceSection>
  );
}

function Abstention({ evidence }: { evidence: Evidence }) {
  const typhoid =
    evidence.conformal_metrics.find((row) => row.label === "typhoid") ??
    evidence.conformal_metrics[0];
  return (
    <EvidenceSection
      question="When does it ask for help?"
      insight={conformalInsight(typhoid, 0.9)}
    >
      <SupportAwareTable
        rows={evidence.conformal_metrics}
        columns={["label", "test_positives", "covered_positives", "empirical_coverage", "predicted_inclusions"]}
        supportColumn="test_positives"
      />
    </EvidenceSection>
  );
}

function Generalization({ evidence }: { evidence: Evidence }) {
  const insight = centerTransferInsight(evidence.center_transfer);
  return (
    <EvidenceSection question="Does it transfer to new centers?" insight={insight}>
      {insight.limitations?.length ? (
        <ul className="limit-list evidence-limit-list">
          {insight.limitations.map((limitation) => (
            <li className="limit-item" key={limitation}>
              {limitation}
            </li>
          ))}
        </ul>
      ) : null}
      <SupportAwareTable
        rows={evidence.center_transfer}
        columns={[
          "test_on",
          "macro_f1",
          "recall_malaria",
          "recall_dengue",
          "recall_typhoid",
          "recall_yellow_fever",
        ]}
        supportColumn="n_test"
        lowSupport={0}
      />
    </EvidenceSection>
  );
}

function Leakage({ summary, evidence }: { summary: Summary; evidence: Evidence }) {
  const preLab = Number(summary.test_metrics?.PRE_LAB?.macro_f1 ?? 0);
  const full = Number(summary.test_metrics?.FULL?.macro_f1 ?? 0);
  return (
    <EvidenceSection question="Is the score honest?" insight={leakageInsight(preLab, full)}>
      <div className="leakage-tracks">
        <div className="leakage-track">
          <span className="compare-tag" data-tone="primary">Deployable</span>
          <strong>PRE_LAB {preLab.toFixed(2)}</strong>
        </div>
        <div className="leakage-track">
          <span className="compare-tag" data-tone="urgent">Research only</span>
          <strong>FULL {full.toFixed(2)}</strong>
        </div>
      </div>
      <SupportAwareTable
        rows={evidence.leakage_candidates.slice(0, 12)}
        columns={["feature", "stage", "reason", "decision"]}
        supportColumn="__none__"
      />
    </EvidenceSection>
  );
}

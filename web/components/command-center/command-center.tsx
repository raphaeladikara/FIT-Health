import { BarChart3, HelpCircle, PieChart, TrendingUp } from "lucide-react";

import { DistributionDonut } from "@/components/charts/distribution-donut";
import { TriageBarChart } from "@/components/charts/triage-bar-chart";
import { TriageScoreProfile } from "@/components/charts/triage-score-profile";
import { DecisionChain } from "@/components/command-center/decision-chain";
import { SituationSummary } from "@/components/command-center/situation-summary";
import { TriageQueue } from "@/components/command-center/triage-queue";
import { TONE_HEX } from "@/components/charts/chart-kit";
import { Panel } from "@/components/ui/panel";
import { ProvenancePanel } from "@/components/ui/provenance-panel";
import { TRIAGE_ORDER, TRIAGE_SHORT, triageTone } from "@/lib/triage";
import type { Manifest, Patient, TriageCategory } from "@/lib/types";

const uncertaintyTone: Record<string, string> = {
  low: "primary",
  moderate: "review",
  high: "urgent",
};

export function CommandCenter({
  patients,
  manifest,
}: {
  patients: Patient[];
  manifest: Manifest;
}) {
  const total = patients.length;

  const tierCounts = {} as Record<TriageCategory, number>;
  for (const category of TRIAGE_ORDER) tierCounts[category] = 0;
  for (const patient of patients) tierCounts[patient.triage_category] += 1;

  const uncertaintyCounts = patients.reduce<Record<string, number>>((counts, patient) => {
    counts[patient.uncertainty_level] = (counts[patient.uncertainty_level] ?? 0) + 1;
    return counts;
  }, {});

  const tierData = TRIAGE_ORDER.map((category) => ({
    label: category,
    short: TRIAGE_SHORT[category],
    value: tierCounts[category],
    tone: triageTone(category),
  }));
  const scores = patients.map((patient) => patient.triage_score);
  const scoreMin = scores.length ? Math.min(...scores) : 0;
  const scoreMax = scores.length ? Math.max(...scores) : 0;

  return (
    <>
      <SituationSummary patients={patients} />
      <DecisionChain patients={patients} />
      <TriageQueue patients={patients} />

      <div className="chart-duo">
        <Panel title="Triage demand by tier" description="Cohort distribution across the four operational tiers." icon={BarChart3}>
          <TriageBarChart data={tierData} />
        </Panel>
        <Panel title="Triage score profile" description="Every case ranked high→low — a distribution, not a time series." icon={TrendingUp}>
          <TriageScoreProfile scores={scores} />
          <p className="chart-summary">
            Scores span <strong>{scoreMin.toFixed(2)}</strong>–<strong>{scoreMax.toFixed(2)}</strong>.
          </p>
        </Panel>
      </div>

      <div className="two-column">
        <Panel title="Cohort priority mix" description="Share of cases in each triage tier." icon={PieChart}>
          <DistributionDonut
            data={tierData.map(({ label, value, tone }) => ({ label, value, tone }))}
            centerValue={total}
            centerLabel="cases"
          />
          <div className="chart-legend">
            {tierData.map((datum) => (
              <span key={datum.label}>
                <i style={{ background: TONE_HEX[datum.tone] }} />
                {datum.label} · {datum.value}
              </span>
            ))}
          </div>
        </Panel>

        <Panel title="Human-review burden" description="Entropy-derived uncertainty across the cohort." icon={HelpCircle}>
          <div className="bar-list">
            {["high", "moderate", "low"].map((level) => {
              const count = uncertaintyCounts[level] ?? 0;
              return (
                <div className="bar-row" key={level}>
                  <span className="bar-label" style={{ textTransform: "capitalize" }}>{level} uncertainty</span>
                  <span className="bar-count">{count}</span>
                  <span className="bar-track">
                    <span
                      className="bar-fill"
                      data-tone={uncertaintyTone[level]}
                      style={{ width: `${total ? (count / total) * 100 : 0}%` }}
                    />
                  </span>
                </div>
              );
            })}
          </div>
        </Panel>
      </div>

      <Panel title="Artifact provenance" description="Which model run and evaluation these counts come from.">
        <ProvenancePanel manifest={manifest} />
      </Panel>
    </>
  );
}

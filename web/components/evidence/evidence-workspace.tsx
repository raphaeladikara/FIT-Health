"use client";

import { useState } from "react";

import { Panel } from "@/components/ui/panel";
import { formatMetric, titleCase } from "@/lib/format";
import type { Evidence, EvidenceRecord, Summary } from "@/lib/types";

const tabs = ["Performance", "Safety", "Calibration", "Fairness", "Explainability"] as const;

export function EvidenceWorkspace({
  summary,
  evidence,
}: {
  summary: Summary;
  evidence: Evidence;
}) {
  const [active, setActive] = useState<(typeof tabs)[number]>("Performance");
  return (
    <>
      <div className="evidence-tabs" role="tablist" aria-label="Evidence categories">
        {tabs.map((tab) => (
          <button
            className="tab-button"
            data-active={active === tab}
            role="tab"
            aria-selected={active === tab}
            key={tab}
            onClick={() => setActive(tab)}
          >
            {tab}
          </button>
        ))}
      </div>
      {active === "Performance" ? (
        <EvidenceTable
          title="Model comparison"
          description="Candidate models are compared before the held-out PRE_LAB result is reported."
          rows={evidence.model_leaderboard}
          columns={["track", "model", "macro_f1", "micro_f1", "macro_pr_auc", "macro_recall"]}
        />
      ) : null}
      {active === "Safety" ? (
        <>
          <EvidenceTable
            title="False-negative evidence by disease"
            description="Support counts and missed-case rates matter more than a single aggregate score."
            rows={evidence.per_label_metrics.filter((row) => row.track === "PRE_LAB")}
            columns={["label", "support_pos", "precision", "recall", "f1", "false_negative_rate", "fn"]}
          />
          <p className="insight warning">
            Rare-label estimates remain uncertain. VECTRA-X requires prospective,
            multi-center validation before operational use.
          </p>
        </>
      ) : null}
      {active === "Calibration" ? (
        <div className="two-column">
          <EvidenceTable title="Calibration metrics" rows={evidence.calibration_metrics} columns={["track", "label", "brier_score", "ece"]} />
          <EvidenceTable title="Conformal coverage" rows={evidence.conformal_metrics} columns={["label", "coverage", "avg_set_size"]} />
        </div>
      ) : null}
      {active === "Fairness" ? (
        <>
          <EvidenceTable title="Subgroup diagnostics" rows={evidence.fairness_metrics} columns={["axis", "group", "label", "support", "recall", "f1"]} />
          <EvidenceTable title="Health-center transfer stress test" rows={evidence.center_transfer} columns={["held_out_center", "macro_f1", "micro_f1", "macro_recall", "macro_pr_auc"]} />
          <p className="insight">
            Subgroup results are warning diagnostics, not proof of fairness. Center
            transfer degradation requires facility-specific validation.
          </p>
        </>
      ) : null}
      {active === "Explainability" ? (
        <div className="two-column">
          <EvidenceTable title="Global permutation importance" rows={evidence.feature_importance_global.slice(0, 20)} columns={["feature", "importance_mean", "importance_std"]} />
          <Panel title="Leakage controls" description="Features that can restate or reveal the diagnosis are kept outside the deployable pre-lab model.">
            <p className="insight warning">
              The FULL track is a research-only leakage demonstration. It must never be
              interpreted as deployable triage performance.
            </p>
            <EvidenceTable title="Flagged candidates" rows={evidence.leakage_candidates.slice(0, 12)} columns={["feature", "stage", "reason", "decision"]} />
          </Panel>
        </div>
      ) : null}
      <Panel title="Held-out operational headline">
        <dl className="record-list">
          {Object.entries(summary.test_metrics.PRE_LAB ?? {}).slice(0, 8).map(([key, value]) => (
            <div key={key}><dt>{titleCase(key)}</dt><dd>{formatMetric(value)}</dd></div>
          ))}
        </dl>
      </Panel>
    </>
  );
}

function EvidenceTable({
  title,
  description,
  rows,
  columns,
}: {
  title: string;
  description?: string;
  rows: EvidenceRecord[];
  columns: string[];
}) {
  return (
    <Panel title={title} description={description}>
      {rows.length ? (
        <div className="data-table-wrap">
          <table className="data-table">
            <thead><tr>{columns.map((column) => <th key={column}>{titleCase(column)}</th>)}</tr></thead>
            <tbody>
              {rows.slice(0, 30).map((row, index) => (
                <tr key={index}>
                  {columns.map((column) => (
                    <td className={typeof row[column] === "number" ? "numeric" : ""} key={column}>
                      {typeof row[column] === "number" ? formatMetric(row[column]) : String(row[column] ?? "Unavailable")}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="insight">This optional artifact was not available in the latest export.</p>
      )}
    </Panel>
  );
}

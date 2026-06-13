"use client";

import {
  AlertTriangle,
  FlaskConical,
  HelpCircle,
  Layers3,
  Users,
} from "lucide-react";
import { useMemo, useState } from "react";

import { MetricStrip } from "@/components/ui/metric-strip";
import { Panel } from "@/components/ui/panel";
import { StatusBadge } from "@/components/ui/status-badge";
import type { Patient } from "@/lib/types";

export function CommandCenter({ patients }: { patients: Patient[] }) {
  const [query, setQuery] = useState("");
  const [priority, setPriority] = useState("All priorities");
  const filtered = useMemo(
    () =>
      [...patients]
        .filter(
          (patient) =>
            (priority === "All priorities" || patient.triage_category === priority) &&
            `${patient.case_id} ${patient.predicted_labels}`
              .toLowerCase()
              .includes(query.toLowerCase()),
        )
        .sort((a, b) => b.triage_score - a.triage_score),
    [patients, priority, query],
  );

  const urgent = patients.filter(
    (patient) => patient.triage_category === "Urgent Response Priority",
  ).length;
  const confirmatory = patients.filter(
    (patient) => patient.triage_category === "Confirmatory Test Priority",
  ).length;
  const uncertain = patients.filter(
    (patient) => patient.uncertainty_level === "high",
  ).length;
  const coinfection = patients.filter(
    (patient) => patient.coinfection_prob >= 0.5,
  ).length;

  return (
    <>
      <MetricStrip
        items={[
          { label: "Cases reviewed", value: patients.length, detail: "Full anonymous cohort", tone: "primary", icon: Users },
          { label: "Urgent response", value: urgent, detail: "Escalate now", tone: "urgent", icon: AlertTriangle },
          { label: "Test priority", value: confirmatory, detail: "Confirmatory demand", tone: "confirm", icon: FlaskConical },
          { label: "High uncertainty", value: uncertain, detail: "Human review burden", tone: "review", icon: HelpCircle },
          { label: "Co-infection risk", value: coinfection, detail: "Probability at least 0.50", tone: "violet", icon: Layers3 },
        ]}
      />
      <div className="workspace-grid">
        <div>
          <Panel
            title="Live triage queue"
            description="Ranked by triage score. Search or isolate a priority tier without exposing patient identifiers."
          >
            <div className="controls-row">
              <label className="field">
                Search cases
                <input
                  type="search"
                  placeholder="Case ID or predicted disease"
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                />
              </label>
              <label className="field">
                Priority tier
                <select value={priority} onChange={(event) => setPriority(event.target.value)}>
                  <option>All priorities</option>
                  <option>Urgent Response Priority</option>
                  <option>Confirmatory Test Priority</option>
                  <option>Clinical Review</option>
                  <option>Routine Monitoring</option>
                </select>
              </label>
            </div>
            <div className="data-table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Case</th>
                    <th>Predicted signals</th>
                    <th>Uncertainty</th>
                    <th>Score</th>
                    <th>Priority</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.slice(0, 30).map((patient) => (
                    <tr key={patient.case_id}>
                      <td><strong>{patient.case_id}</strong></td>
                      <td>{patient.predicted_labels}</td>
                      <td>{patient.uncertainty_level}</td>
                      <td className="numeric">{patient.triage_score.toFixed(3)}</td>
                      <td><StatusBadge value={patient.triage_category} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Panel>
          <div className="two-column">
            <DemandPanel
              title="Triage demand"
              rows={Object.entries(
                patients.reduce<Record<string, number>>((counts, patient) => {
                  counts[patient.triage_category] = (counts[patient.triage_category] ?? 0) + 1;
                  return counts;
                }, {}),
              )}
              total={patients.length}
            />
            <DemandPanel
              title="Human-review burden"
              rows={Object.entries(
                patients.reduce<Record<string, number>>((counts, patient) => {
                  counts[patient.uncertainty_level] = (counts[patient.uncertainty_level] ?? 0) + 1;
                  return counts;
                }, {}),
              )}
              total={patients.length}
            />
          </div>
        </div>
        <div>
          <Panel title="Requires attention now" description="Highest-priority decisions for the current review cycle.">
            <div className="action-list">
              {[...patients]
                .sort((a, b) => b.triage_score - a.triage_score)
                .slice(0, 7)
                .map((patient) => (
                  <article className="action-item" key={patient.case_id}>
                    <header>
                      <strong>{patient.case_id}</strong>
                      <span className="score">{patient.triage_score.toFixed(2)}</span>
                    </header>
                    <StatusBadge value={patient.triage_category} />
                    <p>{patient.predicted_labels}</p>
                  </article>
                ))}
            </div>
          </Panel>
          <Panel title="Operational reading" description="What this cohort requires before the next review cycle.">
            <p className="insight">
              {urgent} cases currently meet urgent-response criteria. {confirmatory + urgent} cases
              compete for confirmatory testing, while {uncertain} cases add uncertainty-driven
              manual review demand.
            </p>
          </Panel>
        </div>
      </div>
    </>
  );
}

function DemandPanel({
  title,
  rows,
  total,
}: {
  title: string;
  rows: [string, number][];
  total: number;
}) {
  return (
    <Panel title={title}>
      <div className="probability-list">
        {rows.map(([label, count]) => (
          <div className="probability-row" key={label}>
            <span>{label}</span>
            <div className="probability-track">
              <div className="probability-fill" style={{ width: `${(count / total) * 100}%` }} />
            </div>
            <strong>{count}</strong>
          </div>
        ))}
      </div>
    </Panel>
  );
}

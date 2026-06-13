"use client";

import { Bed, ClipboardCheck, FlaskConical, TriangleAlert } from "lucide-react";
import { useMemo, useState } from "react";

import { MetricStrip } from "@/components/ui/metric-strip";
import { Panel } from "@/components/ui/panel";
import { StatusBadge } from "@/components/ui/status-badge";
import { allocateRapidTests, calculateCapacity } from "@/lib/resource-allocation";
import type { EvidenceRecord, Patient } from "@/lib/types";

export function ResourceWorkspace({
  patients,
  policyTradeoff,
}: {
  patients: Patient[];
  policyTradeoff: EvidenceRecord[];
}) {
  const [rapidTests, setRapidTests] = useState(Math.min(50, patients.length));
  const [beds, setBeds] = useState(Math.min(12, patients.length));
  const [monitoringSlots, setMonitoringSlots] = useState(Math.min(80, patients.length));
  const [staffReviews, setStaffReviews] = useState(
    Math.min(80, patients.length * 2),
  );
  const capacity = useMemo(
    () => calculateCapacity(patients, { rapidTests, beds, monitoringSlots, staffReviews }),
    [beds, monitoringSlots, patients, rapidTests, staffReviews],
  );
  const queue = useMemo(
    () => allocateRapidTests(patients, rapidTests),
    [patients, rapidTests],
  );
  const rapidDemand = capacity.find((row) => row.resource === "Rapid tests")!;
  const bedDemand = capacity.find((row) => row.resource === "Beds")!;
  const reviewDemand = capacity.find((row) => row.resource === "Staff review slots")!;
  const shortages = capacity.filter((row) => row.status === "Insufficient");
  const waitingForTests = queue.filter(
    (patient) =>
      patient.test_allocation === "Waiting" &&
      ["Confirmatory Test Priority", "Urgent Response Priority"].includes(
        patient.triage_category,
      ),
  ).length;

  return (
    <>
      <Panel title="Available capacity" description="Adjust real constraints. Patient probabilities stay fixed while allocation changes.">
        <div className="capacity-grid">
          <CapacityControl label="Rapid tests" value={rapidTests} max={patients.length} onChange={setRapidTests} />
          <CapacityControl label="Beds" value={beds} max={patients.length} onChange={setBeds} />
          <CapacityControl label="Monitoring slots" value={monitoringSlots} max={patients.length} onChange={setMonitoringSlots} />
          <CapacityControl label="Staff review slots" value={staffReviews} max={patients.length * 2} onChange={setStaffReviews} />
        </div>
      </Panel>
      <MetricStrip
        items={[
          { label: "Rapid-test demand", value: rapidDemand.demand, detail: `${rapidTests} available`, tone: "confirm", icon: FlaskConical },
          { label: "Bed demand", value: bedDemand.demand, detail: `${beds} available`, tone: "urgent", icon: Bed },
          { label: "Review demand", value: reviewDemand.demand, detail: `${staffReviews} slots`, tone: "review", icon: ClipboardCheck },
          { label: "Unmet categories", value: shortages.length, detail: shortages.length ? "Capacity action needed" : "All categories covered", tone: shortages.length ? "urgent" : "primary", icon: TriangleAlert },
        ]}
      />
      <div className="two-column">
        <Panel title="Capacity ledger" description="Demand, available supply, and the resulting gap.">
          <div className="data-table-wrap">
            <table className="data-table">
              <thead><tr><th>Resource</th><th>Demand</th><th>Capacity</th><th>Gap</th><th>Status</th></tr></thead>
              <tbody>
                {capacity.map((row) => (
                  <tr key={row.resource}>
                    <td><strong>{row.resource}</strong></td>
                    <td className="numeric">{row.demand}</td>
                    <td className="numeric">{row.capacity}</td>
                    <td className="numeric">{row.gap}</td>
                    <td><StatusBadge value={row.status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
        <Panel title="Operational consequence" description="The simulator converts capacity into a visible service decision.">
          <p className={shortages.length ? "insight warning" : "insight"}>
            {shortages.length
              ? `${waitingForTests} eligible cases remain outside the current rapid-test allocation. Shortfalls affect ${shortages.map((row) => row.resource.toLowerCase()).join(", ")}.`
              : "Current capacity covers every simulated resource category."}
          </p>
          {policyTradeoff.length ? (
            <dl className="record-list">
              {policyTradeoff.slice(0, 4).map((row, index) => (
                <div key={String(row.policy ?? index)}>
                  <dt>{String(row.policy ?? `Policy ${index + 1}`)}</dt>
                  <dd>{String(row.total_flags ?? "Unavailable")} disease flags</dd>
                </div>
              ))}
            </dl>
          ) : null}
        </Panel>
      </div>
      <Panel title="Prioritized confirmatory-test queue" description="Allocation follows triage score, co-infection risk, then stable anonymous case ID.">
        <div className="data-table-wrap">
          <table className="data-table">
            <thead><tr><th>Case</th><th>Priority</th><th>Uncertainty</th><th>Signals</th><th>Score</th><th>Allocation</th></tr></thead>
            <tbody>
              {queue.slice(0, 100).map((patient) => (
                <tr key={patient.case_id}>
                  <td><strong>{patient.case_id}</strong></td>
                  <td><StatusBadge value={patient.triage_category} /></td>
                  <td>{patient.uncertainty_level}</td>
                  <td>{patient.predicted_labels}</td>
                  <td className="numeric">{patient.triage_score.toFixed(3)}</td>
                  <td><StatusBadge value={patient.test_allocation} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
    </>
  );
}

function CapacityControl({
  label,
  value,
  max,
  onChange,
}: {
  label: string;
  value: number;
  max: number;
  onChange: (value: number) => void;
}) {
  const id = `capacity-${label.toLowerCase().replaceAll(" ", "-")}`;
  return (
    <div className="capacity-control">
      <label htmlFor={id}>{label}</label><output htmlFor={id}>{value}</output>
      <input
        id={id}
        type="range"
        min="0"
        max={max}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
      />
    </div>
  );
}

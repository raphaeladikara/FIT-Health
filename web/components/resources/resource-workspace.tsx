"use client";

import { GitCompareArrows, Info, ListChecks, Scale, SlidersHorizontal } from "lucide-react";
import { useMemo, useState } from "react";

import { AllocationQueue } from "@/components/resources/allocation-queue";
import { AssumptionsPanel } from "@/components/resources/assumptions-panel";
import { CapacityControl } from "@/components/resources/capacity-control";
import { ScenarioComparison } from "@/components/resources/scenario-comparison";
import { ScenarioPresets } from "@/components/resources/scenario-presets";
import { Panel } from "@/components/ui/panel";
import { StatusBadge } from "@/components/ui/status-badge";
import {
  allocateRapidTests,
  calculateCapacity,
  scenarioImpact,
} from "@/lib/resource-allocation";
import {
  RESOURCE_PRESETS,
  resolveResourcePreset,
  type ResourcePresetKey,
} from "@/lib/resource-presets";
import type { CapacityInput, EvidenceRecord, Patient } from "@/lib/types";

const FIELDS: Array<{ key: keyof CapacityInput; label: string; unit: string; factor: number }> = [
  { key: "rapidTests", label: "Rapid tests", unit: "tests", factor: 1 },
  { key: "beds", label: "Beds", unit: "beds", factor: 1 },
  { key: "monitoringSlots", label: "Monitoring slots", unit: "slots", factor: 1 },
  { key: "staffReviews", label: "Staff review slots", unit: "slots", factor: 2 },
];

const POLICY_TRADEOFFS: Record<string, string> = {
  performance: "Fewest flags — efficient, but the highest risk of a missed disease.",
  operational: "Balanced default — moderate confirmatory and review demand.",
  safety: "Most flags — safest for missed cases, heaviest confirmatory demand.",
};

export function ResourceWorkspace({
  patients,
  policyTradeoff,
  initialPreset,
}: {
  patients: Patient[];
  policyTradeoff: EvidenceRecord[];
  initialPreset?: string;
}) {
  const start = resolveResourcePreset(initialPreset);
  const [presetKey, setPresetKey] = useState<ResourcePresetKey>(start.key);
  const [capacity, setCapacity] = useState<CapacityInput>(start.capacity);

  const rows = useMemo(() => calculateCapacity(patients, capacity), [patients, capacity]);
  const queue = useMemo(
    () => allocateRapidTests(patients, capacity.rapidTests),
    [patients, capacity.rapidTests],
  );
  const baselineImpact = useMemo(
    () => scenarioImpact(patients, RESOURCE_PRESETS.current.capacity),
    [patients],
  );
  const currentImpact = useMemo(() => scenarioImpact(patients, capacity), [patients, capacity]);

  function selectPreset(key: ResourcePresetKey) {
    setPresetKey(key);
    setCapacity(RESOURCE_PRESETS[key].capacity);
  }
  function reset() {
    setCapacity(RESOURCE_PRESETS[presetKey].capacity);
  }
  function setField(key: keyof CapacityInput, value: number) {
    setCapacity((current) => ({ ...current, [key]: value }));
  }

  return (
    <>
      <Panel
        title="Capacity scenario"
        description="Load a preset or set exact values. Patient probabilities stay fixed; only allocation changes."
        icon={SlidersHorizontal}
      >
        <ScenarioPresets active={presetKey} onSelect={selectPreset} onReset={reset} />
        <div className="capacity-grid">
          {FIELDS.map((field) => (
            <CapacityControl
              key={field.key}
              label={field.label}
              unit={field.unit}
              value={capacity[field.key]}
              max={patients.length * field.factor}
              onChange={(value) => setField(field.key, value)}
            />
          ))}
        </div>
      </Panel>

      <div className="two-column">
        <Panel title="Capacity ledger" description="Demand, supply, and the resulting non-negative shortfall." icon={Scale}>
          <div className="data-table-wrap">
            <table className="data-table">
              <thead>
                <tr><th>Resource</th><th className="numeric">Demand</th><th className="numeric">Capacity</th><th className="numeric">Shortfall</th><th>Status</th></tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={row.resource}>
                    <td><strong>{row.resource}</strong></td>
                    <td className="numeric">{row.demand}</td>
                    <td className="numeric">{row.capacity}</td>
                    <td className="numeric">{row.shortfall}</td>
                    <td><StatusBadge value={row.status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>

        <Panel title="Scenario vs current capacity" description="How this scenario changes outcomes against today's baseline." icon={GitCompareArrows}>
          <ScenarioComparison baseline={baselineImpact} current={currentImpact} />
        </Panel>
      </div>

      <Panel title="Demand assumptions" description="Every demand figure is a clinically unvalidated heuristic, shown in full." icon={Info}>
        <AssumptionsPanel />
      </Panel>

      <Panel title="Rapid-test allocation queue" description="Allocation follows triage score, then co-infection risk, then stable anonymous case ID." icon={ListChecks}>
        <AllocationQueue queue={queue} />
      </Panel>

      {policyTradeoff.length ? (
        <Panel title="Threshold-policy trade-off" description="How the flagging policy changes downstream demand. More flags catch more disease but cost more tests.">
          <div className="data-table-wrap">
            <table className="data-table">
              <thead>
                <tr><th>Policy</th><th className="numeric">Avg flags / patient</th><th className="numeric">Total flags</th><th>Trade-off</th></tr>
              </thead>
              <tbody>
                {policyTradeoff.map((row, index) => {
                  const policy = String(row.policy ?? `Policy ${index + 1}`);
                  return (
                    <tr key={policy}>
                      <td style={{ textTransform: "capitalize" }}><strong>{policy}</strong></td>
                      <td className="numeric">{String(row.avg_flags_per_patient ?? "—")}</td>
                      <td className="numeric">{String(row.total_flags ?? "—")}</td>
                      <td>{POLICY_TRADEOFFS[policy] ?? "—"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Panel>
      ) : null}
    </>
  );
}

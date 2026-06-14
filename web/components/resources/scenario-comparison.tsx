import type { ScenarioImpact } from "@/lib/types";

const ROWS: Array<{ key: keyof ScenarioImpact; label: string; goodIsLow: boolean }> = [
  { key: "allocatedTests", label: "Tests allocated", goodIsLow: false },
  { key: "waitlistedTests", label: "Eligible waitlisted", goodIsLow: true },
  { key: "urgentBedShortfall", label: "Bed shortfall", goodIsLow: true },
  { key: "monitoringShortfall", label: "Monitoring shortfall", goodIsLow: true },
  { key: "reviewShortfall", label: "Review shortfall", goodIsLow: true },
];

function Delta({ value, goodIsLow }: { value: number; goodIsLow: boolean }) {
  if (value === 0) return <span className="delta" data-dir="flat">±0</span>;
  const improved = goodIsLow ? value < 0 : value > 0;
  return (
    <span className="delta" data-dir={improved ? "good" : "bad"}>
      {value > 0 ? "+" : ""}
      {value}
    </span>
  );
}

export function ScenarioComparison({
  baseline,
  current,
}: {
  baseline: ScenarioImpact;
  current: ScenarioImpact;
}) {
  return (
    <div className="data-table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            <th>Outcome</th>
            <th className="numeric">Current capacity</th>
            <th className="numeric">This scenario</th>
            <th className="numeric">Change</th>
          </tr>
        </thead>
        <tbody>
          {ROWS.map(({ key, label, goodIsLow }) => (
            <tr key={key}>
              <td>{label}</td>
              <td className="numeric">{baseline[key]}</td>
              <td className="numeric">{current[key]}</td>
              <td className="numeric">
                <Delta value={current[key] - baseline[key]} goodIsLow={goodIsLow} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function MetricWithInterval({
  label,
  value,
  interval,
}: {
  label: string;
  value: number;
  interval: [number, number];
}) {
  return (
    <div className="metric-ci">
      <span className="metric-ci-label">{label}</span>
      <strong className="metric-ci-value">{value.toFixed(2)}</strong>
      <span className="metric-ci-band">
        95% CI {interval[0].toFixed(2)}–{interval[1].toFixed(2)}
      </span>
    </div>
  );
}

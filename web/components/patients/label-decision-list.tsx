import { thresholdMarkerPercent, type LabelDecision } from "@/lib/thresholds";

function LabelDecisionRow({
  label,
  probability,
  threshold,
  predicted,
}: { label: string } & LabelDecision) {
  const name = label.replace(/_/g, " ");
  return (
    <div className="label-decision" data-predicted={predicted}>
      <span className="label-decision-name">{name}</span>
      <span
        className="probability-track"
        data-over={predicted}
        role="img"
        aria-label={`${name}: probability ${(probability * 100).toFixed(0)} percent against threshold ${(
          threshold * 100
        ).toFixed(0)} percent — ${predicted ? "flagged" : "below threshold"}`}
      >
        <span className="probability-fill" style={{ width: `${Math.min(100, probability * 100)}%` }} />
        <span
          className="probability-threshold"
          style={{ left: `${thresholdMarkerPercent(threshold)}%` }}
        />
      </span>
      <span className="label-decision-value">
        <strong>{(probability * 100).toFixed(0)}%</strong>
        <small>thr {threshold.toFixed(2)}</small>
      </span>
      <span className="label-decision-flag" data-predicted={predicted}>
        {predicted ? "Flagged" : "Below"}
      </span>
    </div>
  );
}

export function LabelDecisionList({
  decisions,
}: {
  decisions: Record<string, LabelDecision>;
}) {
  const entries = Object.entries(decisions).sort(
    (a, b) => b[1].probability - a[1].probability,
  );
  return (
    <div className="label-decision-list">
      {entries.map(([label, decision]) => (
        <LabelDecisionRow key={label} label={label} {...decision} />
      ))}
    </div>
  );
}

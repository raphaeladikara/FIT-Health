import { clampCapacity } from "@/lib/resource-presets";

/** A single capacity dial: a number field and a slider sharing one label and value. */
export function CapacityControl({
  label,
  value,
  max,
  unit,
  onChange,
}: {
  label: string;
  value: number;
  max: number;
  unit?: string;
  onChange: (value: number) => void;
}) {
  const id = `capacity-${label.toLowerCase().replace(/\s+/g, "-")}`;
  const set = (raw: number) => onChange(clampCapacity(raw, max));

  return (
    <div className="capacity-control">
      <div className="capacity-control-head">
        <label htmlFor={id}>{label}</label>
        <input
          id={id}
          type="number"
          min={0}
          max={max}
          value={value}
          aria-label={`${label}${unit ? ` (${unit})` : ""}`}
          onChange={(event) => set(Number(event.target.value))}
        />
      </div>
      <input
        type="range"
        min={0}
        max={max}
        value={value}
        aria-label={`${label} slider`}
        onChange={(event) => set(Number(event.target.value))}
      />
      <span className="capacity-control-max">{unit ?? "available"} · max {max}</span>
    </div>
  );
}

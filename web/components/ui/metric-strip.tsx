import type { LucideIcon } from "lucide-react";

export type MetricItem = {
  label: string;
  value: string | number;
  detail: string;
  tone: string;
  icon: LucideIcon;
};

export function MetricStrip({ items }: { items: MetricItem[] }) {
  return (
    <section className="metric-strip" aria-label="Operational summary">
      {items.map(({ label, value, detail, tone, icon: Icon }) => (
        <article className="metric-item" data-tone={tone} key={label}>
          <div className="metric-label">
            <Icon aria-hidden="true" size={18} />
            {label}
          </div>
          <strong>{value}</strong>
          <small>{detail}</small>
        </article>
      ))}
    </section>
  );
}

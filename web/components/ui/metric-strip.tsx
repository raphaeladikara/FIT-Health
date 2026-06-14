import type { LucideIcon } from "lucide-react";

export type MetricItem = {
  label: string;
  value: string | number;
  detail: string;
  tone: string;
  icon: LucideIcon;
  /** Optional share of cohort (0–1) rendered as an honest proportion chip. */
  share?: number;
};

export function MetricStrip({ items }: { items: MetricItem[] }) {
  return (
    <section className="kpi-grid" aria-label="Operational summary">
      {items.map(({ label, value, detail, tone, icon: Icon, share }) => (
        <article className="kpi-card" data-tone={tone} key={label}>
          <div className="kpi-head">
            <span className="kpi-id">
              <span className="kpi-icon">
                <Icon aria-hidden="true" size={19} strokeWidth={2} />
              </span>
              <span className="kpi-label">{label}</span>
            </span>
            {typeof share === "number" ? (
              <span className="kpi-share">{Math.round(share * 100)}%</span>
            ) : null}
          </div>
          <strong className="kpi-value">{value}</strong>
          <small className="kpi-detail">{detail}</small>
        </article>
      ))}
    </section>
  );
}

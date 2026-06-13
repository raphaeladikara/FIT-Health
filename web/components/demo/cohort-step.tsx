import { TRIAGE_ORDER, triageTone } from "@/lib/triage";
import type { DashboardData, TriageCategory } from "@/lib/types";

export function CohortStep({ data }: { data: DashboardData }) {
  const total = data.manifest.patient_count;
  const multi = Number(data.summary.n_multilabel_patients ?? 0);
  const distribution = (data.summary.triage_distribution ?? {}) as Record<string, number>;
  const max = Math.max(1, ...Object.values(distribution));

  return (
    <>
      <div className="demo-visual">
        <div className="demo-bigstat">
          <strong>{multi}</strong>
          <span>
            of {total} patients ({Math.round((multi / total) * 100)}%) carry more than
            one disease signal
          </span>
        </div>
        <div className="bar-list demo-bars">
          {TRIAGE_ORDER.map((category: TriageCategory) => {
            const count = distribution[category] ?? 0;
            return (
              <div className="bar-row" key={category}>
                <span className="bar-label">{category}</span>
                <span className="bar-count">{count}</span>
                <span className="bar-track">
                  <span
                    className="bar-fill"
                    data-tone={triageTone(category)}
                    style={{ width: `${(count / max) * 100}%` }}
                  />
                </span>
              </div>
            );
          })}
        </div>
      </div>
      <div className="demo-read">
        <h2>What this shows</h2>
        <p>
          Real febrile patients are imbalanced and frequently multi-label: only a
          minority are urgent, yet a large share carry more than one disease at once. A
          classifier that forces every patient into a single class would misrepresent
          this cohort before any modelling even begins.
        </p>
      </div>
      <p className="demo-limit">
        The cohort is small ({total} patients), so these proportions are indicative of
        the modelling challenge, not a population estimate.
      </p>
    </>
  );
}

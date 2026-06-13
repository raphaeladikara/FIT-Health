import { formatMetric } from "@/lib/format";
import type { DashboardData } from "@/lib/types";

export function LeakageStep({ data }: { data: DashboardData }) {
  const preLab = Number(data.summary.test_metrics?.PRE_LAB?.macro_f1 ?? 0);
  const full = Number(data.summary.test_metrics?.FULL?.macro_f1 ?? 0);
  const max = Math.max(preLab, full, 0.0001);
  const inflation = full - preLab;

  return (
    <>
      <div className="demo-visual demo-compare">
        <div className="compare-row">
          <div className="compare-head">
            <strong>PRE_LAB</strong>
            <span className="compare-tag" data-tone="primary">
              Deployable
            </span>
          </div>
          <div className="compare-track">
            <span
              className="compare-fill"
              data-tone="primary"
              style={{ width: `${(preLab / max) * 100}%` }}
            />
          </div>
          <span className="compare-value">{formatMetric(preLab)}</span>
        </div>
        <div className="compare-row">
          <div className="compare-head">
            <strong>FULL</strong>
            <span className="compare-tag" data-tone="urgent">
              Research only
            </span>
          </div>
          <div className="compare-track">
            <span
              className="compare-fill"
              data-tone="urgent"
              style={{ width: `${(full / max) * 100}%` }}
            />
          </div>
          <span className="compare-value">{formatMetric(full)}</span>
        </div>
        <p className="compare-caption">
          Macro F1, held-out. FULL looks <strong>+{formatMetric(inflation)}</strong>{" "}
          better — purely from features that leak the outcome.
        </p>
      </div>
      <div className="demo-read">
        <h2>What this shows</h2>
        <p>
          The FULL track is allowed to see laboratory-confirmation features that would
          not exist at the moment a triage decision is made. It scores higher, but the
          gain is an artefact of leakage, not real predictive skill. VECTRA-X deploys
          only the leakage-controlled PRE_LAB model.
        </p>
      </div>
      <p className="demo-limit">
        FULL is retained <strong>only</strong> to quantify how much leakage inflates
        results. It is never offered for inference or real decisions.
      </p>
    </>
  );
}

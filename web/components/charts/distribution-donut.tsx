"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { TONE_HEX, TooltipCard } from "@/components/charts/chart-kit";

export type DonutDatum = { label: string; value: number; tone: string };

function DonutTooltip({
  active,
  payload,
  total,
}: {
  active?: boolean;
  payload?: Array<{ payload: DonutDatum }>;
  total: number;
}) {
  if (!active || !payload?.length) return null;
  const datum = payload[0].payload;
  const pct = total ? Math.round((datum.value / total) * 100) : 0;
  return <TooltipCard label={datum.label} value={`${datum.value} cases · ${pct}%`} />;
}

export function DistributionDonut({
  data,
  centerValue,
  centerLabel,
}: {
  data: DonutDatum[];
  centerValue: string | number;
  centerLabel: string;
}) {
  const total = data.reduce((sum, datum) => sum + datum.value, 0);
  return (
    <div className="chart-canvas" aria-hidden="true" style={{ position: "relative" }}>
      <ResponsiveContainer width="100%" height={224}>
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="label"
            innerRadius={64}
            outerRadius={92}
            paddingAngle={2}
            stroke="none"
            startAngle={90}
            endAngle={-270}
          >
            {data.map((datum) => (
              <Cell key={datum.label} fill={TONE_HEX[datum.tone] ?? TONE_HEX.neutral} />
            ))}
          </Pie>
          <Tooltip content={<DonutTooltip total={total} />} />
        </PieChart>
      </ResponsiveContainer>
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "grid",
          placeItems: "center",
          pointerEvents: "none",
        }}
      >
        <div style={{ textAlign: "center" }}>
          <div
            style={{
              fontFamily: "var(--font-jakarta)",
              fontSize: 28,
              fontWeight: 750,
              letterSpacing: "-0.02em",
              lineHeight: 1,
              color: "var(--ink)",
              fontVariantNumeric: "tabular-nums",
            }}
          >
            {centerValue}
          </div>
          <div style={{ marginTop: 4, fontSize: 12, color: "var(--ink-faint)" }}>{centerLabel}</div>
        </div>
      </div>
    </div>
  );
}

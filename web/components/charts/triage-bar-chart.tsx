"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { CHART, TONE_HEX, TooltipCard } from "@/components/charts/chart-kit";

export type TierDatum = { label: string; short: string; value: number; tone: string };

function TierTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: TierDatum }> }) {
  if (!active || !payload?.length) return null;
  const datum = payload[0].payload;
  return <TooltipCard label={datum.label} value={`${datum.value} cases`} />;
}

export function TriageBarChart({ data }: { data: TierDatum[] }) {
  return (
    <div className="chart-canvas" aria-hidden="true">
      <ResponsiveContainer width="100%" height={236}>
        <BarChart data={data} margin={{ top: 20, right: 6, left: 6, bottom: 0 }}>
          <CartesianGrid vertical={false} stroke={CHART.grid} />
          <XAxis dataKey="short" tickLine={false} axisLine={false} dy={4} />
          <YAxis hide domain={[0, "dataMax + 12"]} />
          <Tooltip cursor={{ fill: "rgba(59,110,246,0.06)" }} content={<TierTooltip />} />
          <Bar dataKey="value" radius={[8, 8, 0, 0]} maxBarSize={66}>
            <LabelList
              dataKey="value"
              position="top"
              fill={CHART.ink}
              fontSize={13}
              fontWeight={700}
            />
            {data.map((datum) => (
              <Cell key={datum.label} fill={TONE_HEX[datum.tone] ?? TONE_HEX.neutral} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

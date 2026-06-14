"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { CHART, TONE_HEX, TooltipCard } from "@/components/charts/chart-kit";

export type LabelDatum = { label: string; value: number };

function LabelTooltip({
  active,
  payload,
  unit,
}: {
  active?: boolean;
  payload?: Array<{ payload: LabelDatum }>;
  unit: string;
}) {
  if (!active || !payload?.length) return null;
  const datum = payload[0].payload;
  return <TooltipCard label={datum.label} value={`${unit}: ${datum.value.toFixed(2)}`} />;
}

/** Horizontal comparison bars for per-label metrics (e.g. recall by disease). */
export function PerLabelBar({
  data,
  unit = "Value",
  color = TONE_HEX.primary,
}: {
  data: LabelDatum[];
  unit?: string;
  color?: string;
}) {
  return (
    <div className="chart-canvas" aria-hidden="true">
      <ResponsiveContainer width="100%" height={data.length * 46 + 24}>
        <BarChart layout="vertical" data={data} margin={{ top: 4, right: 36, left: 6, bottom: 4 }}>
          <CartesianGrid horizontal={false} stroke={CHART.grid} />
          <XAxis type="number" domain={[0, 1]} hide />
          <YAxis
            type="category"
            dataKey="label"
            width={118}
            tickLine={false}
            axisLine={false}
            tick={{ fontSize: 12.5 }}
          />
          <Tooltip cursor={{ fill: "rgba(59,110,246,0.06)" }} content={<LabelTooltip unit={unit} />} />
          <Bar dataKey="value" fill={color} radius={[0, 6, 6, 0]} barSize={15}>
            <LabelList
              dataKey="value"
              position="right"
              formatter={(value) => (typeof value === "number" ? value.toFixed(2) : String(value ?? ""))}
              fill={CHART.ink}
              fontSize={12}
              fontWeight={700}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

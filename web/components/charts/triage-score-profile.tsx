"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { CHART, TONE_HEX, TooltipCard } from "@/components/charts/chart-kit";

type ScorePoint = { rank: number; score: number };

function ScoreTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: ScorePoint }> }) {
  if (!active || !payload?.length) return null;
  const point = payload[0].payload;
  return <TooltipCard label={`Rank #${point.rank}`} value={`Triage score ${point.score.toFixed(3)}`} />;
}

/**
 * Honest analog of the reference "income" line chart: real triage scores sorted
 * high→low across the cohort. This is a distribution profile, NOT a time series.
 */
export function TriageScoreProfile({ scores }: { scores: number[] }) {
  const points: ScorePoint[] = [...scores]
    .sort((a, b) => b - a)
    .map((score, index) => ({ rank: index + 1, score }));
  const max = points.length ? Math.max(...points.map((point) => point.score)) : 1;

  return (
    <div className="chart-canvas" aria-hidden="true">
      <ResponsiveContainer width="100%" height={224}>
        <AreaChart data={points} margin={{ top: 10, right: 8, left: 6, bottom: 0 }}>
          <defs>
            <linearGradient id="vx-score-fill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={TONE_HEX.primary} stopOpacity={0.32} />
              <stop offset="100%" stopColor={TONE_HEX.primary} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid vertical={false} stroke={CHART.grid} />
          <XAxis
            dataKey="rank"
            tickLine={false}
            axisLine={false}
            ticks={[1, Math.ceil(points.length / 2), points.length].filter(Boolean)}
            tickFormatter={(value: number) => `#${value}`}
            dy={4}
          />
          <YAxis hide domain={[0, Math.max(max, 0.1)]} />
          <Tooltip content={<ScoreTooltip />} />
          <Area
            type="monotone"
            dataKey="score"
            stroke={TONE_HEX.primaryStrong}
            strokeWidth={2.4}
            fill="url(#vx-score-fill)"
            activeDot={{ r: 4, strokeWidth: 0, fill: TONE_HEX.primaryStrong }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

"use client";

import type { ReactNode } from "react";

/** Literal hexes mirroring the CSS severity ramp (Recharts can't read CSS vars). */
export const TONE_HEX: Record<string, string> = {
  primary: "#3b6ef6",
  primaryStrong: "#2f59d6",
  routine: "#1f9d6b",
  review: "#e0a32e",
  confirm: "#ef7d3a",
  urgent: "#e5484d",
  violet: "#7c5cfc",
  neutral: "#8aa0b6",
};

export const CHART = {
  grid: "#eceff5",
  axis: "#67798d",
  ink: "#16202e",
};

export function TooltipCard({ label, value }: { label: ReactNode; value: ReactNode }) {
  return (
    <div className="recharts-tooltip-card">
      <div className="t-label">{label}</div>
      <div className="t-value">{value}</div>
    </div>
  );
}

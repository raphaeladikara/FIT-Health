import {
  AlertCircle,
  Ban,
  CheckCircle2,
  CircleDot,
  Clock,
  FlaskConical,
  type LucideIcon,
} from "lucide-react";

const categoryMap: Record<string, { tone: string; icon: LucideIcon }> = {
  "Routine Monitoring": { tone: "routine", icon: CheckCircle2 },
  "Clinical Review": { tone: "review", icon: CircleDot },
  "Confirmatory Test Priority": { tone: "confirm", icon: FlaskConical },
  "Urgent Response Priority": { tone: "urgent", icon: AlertCircle },
  // resource-allocation statuses
  Sufficient: { tone: "routine", icon: CheckCircle2 },
  Insufficient: { tone: "urgent", icon: AlertCircle },
  Allocated: { tone: "primary", icon: CheckCircle2 },
  Waitlisted: { tone: "review", icon: Clock },
  "Not eligible": { tone: "neutral", icon: Ban },
};

export function StatusBadge({ value }: { value: string }) {
  const setting = categoryMap[value] ?? { tone: "neutral", icon: CircleDot };
  const Icon = setting.icon;
  return (
    <span className="status-badge" data-tone={setting.tone}>
      <Icon aria-hidden="true" size={13} />
      {value}
    </span>
  );
}

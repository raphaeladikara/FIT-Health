import { AlertCircle, CheckCircle2, CircleDot, FlaskConical } from "lucide-react";

const categoryMap = {
  "Routine Monitoring": { tone: "routine", icon: CheckCircle2 },
  "Clinical Review": { tone: "review", icon: CircleDot },
  "Confirmatory Test Priority": { tone: "confirm", icon: FlaskConical },
  "Urgent Response Priority": { tone: "urgent", icon: AlertCircle },
};

export function StatusBadge({ value }: { value: string }) {
  const setting = categoryMap[value as keyof typeof categoryMap] ?? {
    tone: "neutral",
    icon: CircleDot,
  };
  const Icon = setting.icon;
  return (
    <span className="status-badge" data-tone={setting.tone}>
      <Icon aria-hidden="true" size={14} />
      {value}
    </span>
  );
}

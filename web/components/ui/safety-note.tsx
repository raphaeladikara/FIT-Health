import { ShieldAlert } from "lucide-react";

export function SafetyNote({ compact = false }: { compact?: boolean }) {
  return (
    <div className={compact ? "safety-note compact" : "safety-note"} role="note">
      <ShieldAlert aria-hidden="true" size={18} />
      <span>
        VECTRA-X supports triage decisions. It does not provide a confirmed diagnosis
        or replace qualified medical review.
      </span>
    </div>
  );
}

import { Inbox } from "lucide-react";
import Link from "next/link";
import type { ReactNode } from "react";

export function EmptyState({
  title,
  description,
  actionHref,
  actionLabel,
  onAction,
  icon,
}: {
  title: string;
  description?: string;
  actionHref?: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: ReactNode;
}) {
  return (
    <div className="empty-state" role="status">
      <span className="empty-state-icon" aria-hidden="true">
        {icon ?? <Inbox size={22} />}
      </span>
      <strong>{title}</strong>
      {description ? <p>{description}</p> : null}
      {actionLabel && actionHref ? (
        <Link href={actionHref} className="empty-state-action">
          {actionLabel}
        </Link>
      ) : actionLabel && onAction ? (
        <button type="button" className="empty-state-action" onClick={onAction}>
          {actionLabel}
        </button>
      ) : null}
    </div>
  );
}

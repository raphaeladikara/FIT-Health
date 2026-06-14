import { TriangleAlert } from "lucide-react";

export function ErrorState({
  title,
  description,
}: {
  title: string;
  description?: string;
}) {
  return (
    <div className="empty-state error-state" role="alert">
      <span className="empty-state-icon" aria-hidden="true">
        <TriangleAlert size={22} />
      </span>
      <strong>{title}</strong>
      {description ? <p>{description}</p> : null}
    </div>
  );
}

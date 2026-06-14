import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

export function Panel({
  title,
  description,
  icon: Icon,
  aside,
  children,
  className = "",
}: {
  title: string;
  description?: string;
  icon?: LucideIcon;
  aside?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`panel ${className}`.trim()}>
      <div className="panel-heading">
        <div className="panel-title-group">
          <h2>
            {Icon ? (
              <span className="panel-icon" aria-hidden="true">
                <Icon size={16} strokeWidth={2} />
              </span>
            ) : null}
            {title}
          </h2>
          {description ? <p>{description}</p> : null}
        </div>
        {aside ? <div className="panel-aside">{aside}</div> : null}
      </div>
      {children}
    </section>
  );
}

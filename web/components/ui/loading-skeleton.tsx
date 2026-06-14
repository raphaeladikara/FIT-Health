export function LoadingSkeleton({ rows = 3 }: { rows?: number }) {
  return (
    <div className="skeleton" aria-hidden="true">
      {Array.from({ length: rows }).map((_, index) => (
        <span className="skeleton-row" key={index} />
      ))}
    </div>
  );
}

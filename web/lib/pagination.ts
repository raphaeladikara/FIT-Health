export type Page<T> = {
  items: T[];
  currentPage: number;
  totalPages: number;
  total: number;
};

/**
 * Pure, clamped pagination. The requested page is bounded to [1, totalPages] so an
 * out-of-range page (e.g. after filtering shrinks the list) never yields an empty view.
 */
export function paginate<T>(items: T[], page: number, pageSize: number): Page<T> {
  const total = items.length;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const currentPage = Math.min(Math.max(Math.trunc(page) || 1, 1), totalPages);
  const start = (currentPage - 1) * pageSize;
  return {
    items: items.slice(start, start + pageSize),
    currentPage,
    totalPages,
    total,
  };
}

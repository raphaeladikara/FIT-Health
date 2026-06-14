import { formatMetric, titleCase } from "@/lib/format";
import type { EvidenceRecord } from "@/lib/types";

/**
 * A table that keeps the support column visible and flags low-support rows, so a
 * strong-looking metric on a handful of cases is never read as settled.
 */
export function SupportAwareTable({
  rows,
  columns,
  supportColumn = "support_pos",
  lowSupport = 10,
  caption,
}: {
  rows: EvidenceRecord[];
  columns: string[];
  supportColumn?: string;
  lowSupport?: number;
  caption?: string;
}) {
  if (!rows.length) {
    return <p className="insight">This optional artifact was not available in the latest export.</p>;
  }
  return (
    <div className="data-table-wrap">
      <table className="data-table">
        {caption ? <caption className="sr-only">{caption}</caption> : null}
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column} className={column === supportColumn ? "support-col" : ""}>
                {titleCase(column)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => {
            const support = Number(row[supportColumn]);
            const low = Number.isFinite(support) && support <= lowSupport;
            return (
              <tr key={index} data-low-support={low || undefined}>
                {columns.map((column) => {
                  const value = row[column];
                  const isSupport = column === supportColumn;
                  return (
                    <td
                      key={column}
                      className={`${typeof value === "number" ? "numeric" : ""} ${
                        isSupport ? "support-col" : ""
                      }`.trim()}
                    >
                      {isSupport && low ? (
                        <span className="low-support-flag" title="Low support — estimate unstable">
                          {String(value)}
                        </span>
                      ) : typeof value === "number" ? (
                        formatMetric(value)
                      ) : (
                        String(value ?? "—")
                      )}
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

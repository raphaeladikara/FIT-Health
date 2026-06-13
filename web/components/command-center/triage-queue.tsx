"use client";

import { ArrowUpRight, ListChecks } from "lucide-react";
import Link from "next/link";
import { useMemo, useState } from "react";

import { EmptyState } from "@/components/ui/empty-state";
import { Monogram } from "@/components/ui/monogram";
import { Pagination } from "@/components/ui/pagination";
import { Panel } from "@/components/ui/panel";
import { StatusBadge } from "@/components/ui/status-badge";
import { paginate } from "@/lib/pagination";
import { TRIAGE_ORDER } from "@/lib/triage";
import type { Patient } from "@/lib/types";

const PAGE_SIZE = 25;
const ALL = "All priorities";

export function TriageQueue({ patients }: { patients: Patient[] }) {
  const [query, setQuery] = useState("");
  const [priority, setPriority] = useState(ALL);
  const [page, setPage] = useState(1);

  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return [...patients]
      .filter(
        (patient) =>
          (priority === ALL || patient.triage_category === priority) &&
          (needle === "" ||
            `${patient.case_id} ${patient.predicted_labels}`
              .toLowerCase()
              .includes(needle)),
      )
      .sort((a, b) => b.triage_score - a.triage_score);
  }, [patients, priority, query]);

  const pageData = paginate(filtered, page, PAGE_SIZE);
  const hasFilters = query.trim() !== "" || priority !== ALL;

  function update<T>(setter: (value: T) => void) {
    return (value: T) => {
      setter(value);
      setPage(1);
    };
  }

  function clearFilters() {
    setQuery("");
    setPriority(ALL);
    setPage(1);
  }

  return (
    <Panel
      title="Live triage queue"
      description="Ranked by triage score. Filter by tier or search without exposing patient identifiers."
      icon={ListChecks}
    >
      <div className="controls-row">
        <label className="field">
          Search cases
          <input
            type="search"
            placeholder="Case ID or predicted disease"
            value={query}
            onChange={(event) => update(setQuery)(event.target.value)}
          />
        </label>
        <label className="field">
          Priority tier
          <select
            value={priority}
            onChange={(event) => update(setPriority)(event.target.value)}
          >
            <option>{ALL}</option>
            {TRIAGE_ORDER.map((tier) => (
              <option key={tier}>{tier}</option>
            ))}
          </select>
        </label>
        {hasFilters ? (
          <button type="button" className="chip clear-filters" onClick={clearFilters}>
            Clear filters
          </button>
        ) : null}
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          title="No matching cases"
          description="No anonymous case matches the current search and tier filter."
          actionLabel="Clear filters"
          onAction={clearFilters}
        />
      ) : (
        <>
          <div className="data-table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Case</th>
                  <th>Predicted signals</th>
                  <th>Uncertainty</th>
                  <th>Score</th>
                  <th>Priority</th>
                  <th aria-label="Open" />
                </tr>
              </thead>
              <tbody>
                {pageData.items.map((patient) => (
                  <tr key={patient.case_id}>
                    <td>
                      <span className="case-cell">
                        <Monogram size="sm" caseId={patient.case_id} category={patient.triage_category} />
                        <strong>{patient.case_id}</strong>
                      </span>
                    </td>
                    <td>{patient.predicted_labels}</td>
                    <td style={{ textTransform: "capitalize" }}>{patient.uncertainty_level}</td>
                    <td className="numeric">{patient.triage_score.toFixed(3)}</td>
                    <td><StatusBadge value={patient.triage_category} /></td>
                    <td>
                      <Link
                        className="queue-open"
                        href={`/patients?case=${encodeURIComponent(patient.case_id)}`}
                      >
                        Open <ArrowUpRight size={13} aria-hidden="true" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Pagination
            currentPage={pageData.currentPage}
            totalPages={pageData.totalPages}
            total={pageData.total}
            pageSize={PAGE_SIZE}
            onPageChange={setPage}
            noun="cases"
          />
        </>
      )}
    </Panel>
  );
}

"use client";

import { useState } from "react";

import { Monogram } from "@/components/ui/monogram";
import { Pagination } from "@/components/ui/pagination";
import { StatusBadge } from "@/components/ui/status-badge";
import { paginate } from "@/lib/pagination";
import type { AllocatedPatient, TestAllocation } from "@/lib/types";

const PAGE_SIZE = 25;

export function AllocationQueue({ queue }: { queue: AllocatedPatient[] }) {
  const [page, setPage] = useState(1);
  const counts: Record<TestAllocation, number> = {
    Allocated: 0,
    Waitlisted: 0,
    "Not eligible": 0,
  };
  for (const patient of queue) counts[patient.test_allocation] += 1;
  const pageData = paginate(queue, page, PAGE_SIZE);

  return (
    <>
      <div className="allocation-counts">
        {(Object.keys(counts) as TestAllocation[]).map((status) => (
          <div className="allocation-count" key={status}>
            <StatusBadge value={status} />
            <strong>{counts[status]}</strong>
          </div>
        ))}
      </div>
      <div className="data-table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>Case</th>
              <th>Priority</th>
              <th>Signals</th>
              <th>Score</th>
              <th>Allocation</th>
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
                <td><StatusBadge value={patient.triage_category} /></td>
                <td>{patient.predicted_labels}</td>
                <td className="numeric">{patient.triage_score.toFixed(3)}</td>
                <td><StatusBadge value={patient.test_allocation} /></td>
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
  );
}

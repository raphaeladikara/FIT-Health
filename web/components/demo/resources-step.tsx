import { allocateRapidTests } from "@/lib/resource-allocation";
import { RESOURCE_PRESETS } from "@/lib/resource-presets";
import type { DashboardData, TestAllocation } from "@/lib/types";

const CARDS: Array<{ status: TestAllocation; tone: string; note: string }> = [
  { status: "Allocated", tone: "routine", note: "Receive a rapid test now." },
  { status: "Waitlisted", tone: "review", note: "Eligible, but capacity is exhausted." },
  { status: "Not eligible", tone: "neutral", note: "Routine tier — no test under the rule." },
];

export function ResourcesStep({ data }: { data: DashboardData }) {
  const tests = RESOURCE_PRESETS.current.capacity.rapidTests;
  const queue = allocateRapidTests(data.patients, tests);
  const counts: Record<TestAllocation, number> = {
    Allocated: 0,
    Waitlisted: 0,
    "Not eligible": 0,
  };
  for (const patient of queue) counts[patient.test_allocation] += 1;

  return (
    <>
      <div className="demo-visual">
        <p className="demo-allocation-lead">
          With the current capacity of <strong>{tests}</strong> rapid tests across{" "}
          {data.manifest.patient_count} patients:
        </p>
        <div className="demo-allocation-grid">
          {CARDS.map((card) => (
            <div className="demo-alloc-card" data-tone={card.tone} key={card.status}>
              <span className="demo-alloc-count">{counts[card.status]}</span>
              <strong>{card.status}</strong>
              <p>{card.note}</p>
            </div>
          ))}
        </div>
      </div>
      <div className="demo-read">
        <h2>What this shows</h2>
        <p>
          A calibrated risk score only becomes a decision when it meets scarce capacity.
          Even with a sensible priority order, real constraints leave a clear{" "}
          <strong>waitlist</strong> — and that consequence is made explicit, not hidden.
        </p>
      </div>
      <p className="demo-limit">
        Allocation here is a transparent simulator built on clinically unvalidated
        heuristics, for exploring trade-offs — not an operational scheduling system.
      </p>
    </>
  );
}

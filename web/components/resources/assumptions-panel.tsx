import { DEMAND_ASSUMPTIONS } from "@/lib/resource-allocation";
import type { ResourceName } from "@/lib/types";

export function AssumptionsPanel() {
  const entries = Object.entries(DEMAND_ASSUMPTIONS) as Array<[ResourceName, string]>;
  return (
    <dl className="assumptions-list">
      {entries.map(([resource, assumption]) => (
        <div key={resource} className="assumption-item">
          <dt>{resource}</dt>
          <dd>{assumption}</dd>
        </div>
      ))}
    </dl>
  );
}

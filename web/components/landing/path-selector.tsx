import { ArrowRight, MonitorCheck, PlayCircle } from "lucide-react";
import Link from "next/link";

export function PathSelector() {
  return (
    <section className="landing-section landing-paths" aria-labelledby="paths-heading">
      <h2 id="paths-heading" className="landing-section-title">
        Choose how you want to look
      </h2>
      <div className="path-grid">
        <Link href="/demo" className="path-card" data-variant="demo">
          <span className="path-icon" aria-hidden="true">
            <PlayCircle size={22} />
          </span>
          <strong>Guided demo</strong>
          <p>
            A five-step walkthrough for judges: cohort reality, the leakage trap, a
            patient decision, an ambiguous case, and the resource consequence.
          </p>
          <span className="path-go">
            Start the walkthrough <ArrowRight aria-hidden="true" size={15} />
          </span>
        </Link>
        <Link href="/command-center" className="path-card" data-variant="ops">
          <span className="path-icon" aria-hidden="true">
            <MonitorCheck size={22} />
          </span>
          <strong>Command center</strong>
          <p>
            The operational view: a live triage queue, per-patient decisions, resource
            scenarios, and the full evidence trust center.
          </p>
          <span className="path-go">
            Open the workspace <ArrowRight aria-hidden="true" size={15} />
          </span>
        </Link>
      </div>
    </section>
  );
}

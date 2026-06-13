import { ArrowRight, ShieldCheck } from "lucide-react";
import Link from "next/link";

import { evaluationModeLabel, provenanceStatus } from "@/lib/provenance";
import type { Manifest } from "@/lib/types";

export function LandingHero({ manifest }: { manifest: Manifest }) {
  const status = provenanceStatus(manifest);
  return (
    <section className="landing-hero">
      <p className="landing-eyebrow">Outbreak triage decision support</p>
      <h1>
        Calibrated, honest triage <br />
        when every test is scarce.
      </h1>
      <p className="landing-lead">
        VECTRA-X turns pre-laboratory patient signals into calibrated, multi-label
        disease risk, flags the cases a clinician should review, and shows how scarce
        tests and beds get allocated — without ever calling its output a diagnosis.
      </p>
      <div className="landing-cta-row">
        <Link href="/demo" className="public-cta">
          Start guided demo
          <ArrowRight aria-hidden="true" size={16} />
        </Link>
        <Link href="/command-center" className="landing-cta-secondary">
          Open command center
        </Link>
      </div>
      <div className="landing-runstatus" data-testid="landing-run-status" data-severity={status.severity}>
        <ShieldCheck aria-hidden="true" size={16} />
        <span>
          {status.canonical
            ? "Canonical pipeline run"
            : `Development artifact — ${manifest.execution_profile}`}{" "}
          · headline metrics evaluated on {evaluationModeLabel(status.evaluationMode)} data ·{" "}
          <span className="landing-runid">run {manifest.run_id}</span>
        </span>
      </div>
    </section>
  );
}

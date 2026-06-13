import { Differentiators } from "@/components/landing/differentiators";
import { EvidenceSnapshot } from "@/components/landing/evidence-snapshot";
import { LandingHero } from "@/components/landing/landing-hero";
import { LimitationsBand } from "@/components/landing/limitations-band";
import { OperationalFlow } from "@/components/landing/operational-flow";
import { PathSelector } from "@/components/landing/path-selector";
import { buildLandingSnapshot } from "@/lib/landing-content";
import { loadDashboardData } from "@/lib/data";

export default async function LandingPage() {
  const data = await loadDashboardData();
  const snapshot = buildLandingSnapshot(data);
  return (
    <div className="landing">
      <LandingHero manifest={data.manifest} />
      <OperationalFlow />
      <Differentiators />
      <EvidenceSnapshot snapshot={snapshot} />
      <PathSelector />
      <LimitationsBand />
    </div>
  );
}

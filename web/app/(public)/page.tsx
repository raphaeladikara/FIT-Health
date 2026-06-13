import Link from "next/link";

// Placeholder landing — replaced by the full product briefing in Phase 3 (Task 6).
export default function LandingPage() {
  return (
    <section className="landing-placeholder">
      <h1>VECTRA-X Outbreak Triage</h1>
      <p>
        Calibrated, uncertainty-aware multi-label triage decision support for
        vector-borne disease response.
      </p>
      <div className="landing-placeholder-actions">
        <Link href="/demo" className="public-cta">
          Start guided demo
        </Link>
        <Link href="/command-center" className="public-nav-link">
          Open command center
        </Link>
      </div>
    </section>
  );
}

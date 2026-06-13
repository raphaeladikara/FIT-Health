import type { ReactNode } from "react";

import { PublicHeader } from "@/components/shell/public-header";

export default function PublicLayout({ children }: { children: ReactNode }) {
  return (
    <div className="public-shell">
      <a className="skip-link" href="#main-content">
        Skip to main content
      </a>
      <PublicHeader />
      <main id="main-content" className="public-main">
        {children}
      </main>
      <footer className="public-footer">
        <p>
          <strong>VECTRA-X</strong> is calibrated triage decision support for
          vector-borne disease response — <strong>not a diagnosis</strong> and not a
          substitute for clinical judgement or laboratory confirmation.
        </p>
        <p className="public-footer-meta">
          Research prototype · privacy-safe anonymized artifacts · no prospective
          clinical validation.
        </p>
      </footer>
    </div>
  );
}

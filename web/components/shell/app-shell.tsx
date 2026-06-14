import type { ReactNode } from "react";

import { MobileNavigation } from "@/components/shell/mobile-navigation";
import { SideNavigation } from "@/components/shell/side-navigation";
import { TopBar } from "@/components/shell/top-bar";
import { loadManifest } from "@/lib/data";

export async function AppShell({ children }: { children: ReactNode }) {
  const manifest = await loadManifest();
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">
        Skip to main content
      </a>
      <aside className="sidebar">
        <div className="brand-lockup">
          <span className="brand-mark" aria-hidden="true">VX</span>
          <span>
            <strong>VECTRA-X</strong>
            <small>Outbreak Triage</small>
          </span>
        </div>
        <SideNavigation />
        <div className="sidebar-note">
          <strong>
            <span className="status-dot" />
            PRE_LAB operational model
          </strong>
          <small>Calibrated triage decision support — never a diagnosis.</small>
        </div>
      </aside>
      <div className="app-main">
        <TopBar manifest={manifest} />
        <header className="mobile-header">
          <div className="brand-lockup compact">
            <span className="brand-mark" aria-hidden="true">VX</span>
            <strong>VECTRA-X</strong>
          </div>
          <MobileNavigation />
        </header>
        <main id="main-content" className="main-content">
          {children}
        </main>
      </div>
    </div>
  );
}

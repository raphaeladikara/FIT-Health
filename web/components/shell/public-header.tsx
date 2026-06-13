"use client";

import { ArrowRight } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS: Array<{ href: string; label: string }> = [
  { href: "/", label: "Overview" },
  { href: "/demo", label: "Guided demo" },
  { href: "/methodology", label: "Methodology" },
];

export function PublicHeader() {
  const pathname = usePathname();
  return (
    <header className="public-header">
      <Link href="/" className="public-brand" aria-label="VECTRA-X overview">
        <span className="brand-mark" aria-hidden="true">
          VX
        </span>
        <span className="public-brand-text">
          <strong>VECTRA-X</strong>
          <small>Outbreak Triage</small>
        </span>
      </Link>
      <nav className="public-nav" aria-label="Public navigation">
        {LINKS.map(({ href, label }) => {
          const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className="public-nav-link"
              data-active={active}
              aria-current={active ? "page" : undefined}
            >
              {label}
            </Link>
          );
        })}
      </nav>
      <Link href="/command-center" className="public-cta">
        Open command center
        <ArrowRight aria-hidden="true" size={16} />
      </Link>
    </header>
  );
}

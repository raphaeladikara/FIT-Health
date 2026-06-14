import Link from "next/link";

import {
  EVIDENCE_SECTIONS,
  evidenceSectionHref,
  type EvidenceSectionSlug,
} from "@/lib/evidence-sections";

export function EvidenceNavigation({ current }: { current: EvidenceSectionSlug }) {
  return (
    <nav className="evidence-nav" aria-label="Trust center questions">
      {EVIDENCE_SECTIONS.map((section) => (
        <Link
          key={section.slug}
          href={evidenceSectionHref(section.slug)}
          className="evidence-nav-link"
          data-active={section.slug === current}
          aria-current={section.slug === current ? "page" : undefined}
        >
          {section.label}
        </Link>
      ))}
    </nav>
  );
}

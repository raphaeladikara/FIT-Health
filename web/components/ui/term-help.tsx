import { HelpCircle } from "lucide-react";
import Link from "next/link";

import { glossaryAnchor, glossaryEntry } from "@/lib/glossary";

/** An accessible inline link to a glossary definition (not a hover-only tooltip). */
export function TermHelp({ slug, children }: { slug: string; children?: React.ReactNode }) {
  const entry = glossaryEntry(slug);
  const label = children ?? entry?.term ?? slug;
  return (
    <Link
      href={glossaryAnchor(slug)}
      className="term-help"
      aria-label={`${entry?.term ?? slug} — see definition`}
    >
      {label}
      <HelpCircle aria-hidden="true" size={13} />
    </Link>
  );
}

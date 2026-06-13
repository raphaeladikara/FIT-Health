"use client";

import {
  Activity,
  BookOpenCheck,
  FlaskConical,
  Gauge,
  ShieldCheck,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const items = [
  { href: "/", label: "Command Center", icon: Activity },
  { href: "/patients", label: "Patient Intelligence", icon: Gauge },
  { href: "/resources", label: "Resource Allocation", icon: FlaskConical },
  { href: "/evidence", label: "Trust & Evidence", icon: ShieldCheck },
  { href: "/methodology", label: "Methodology", icon: BookOpenCheck },
];

export function SideNavigation() {
  const pathname = usePathname();
  return (
    <nav className="side-nav" aria-label="Primary navigation">
      {items.map(({ href, label, icon: Icon }) => {
        const active = href === "/" ? pathname === href : pathname.startsWith(href);
        return (
          <Link
            className="nav-item"
            data-active={active}
            href={href}
            key={href}
            aria-current={active ? "page" : undefined}
          >
            <Icon aria-hidden="true" size={19} strokeWidth={1.8} />
            <span>{label}</span>
          </Link>
        );
      })}
    </nav>
  );
}

"use client";

import {
  Activity,
  BookOpenCheck,
  Inbox,
  ShieldCheck,
  SlidersHorizontal,
  Users,
  type LucideIcon,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

type NavItem = { href: string; label: string; icon: LucideIcon };

const groups: Array<{ label: string; items: NavItem[] }> = [
  {
    label: "Operations",
    items: [
      { href: "/command-center", label: "Command Center", icon: Activity },
      { href: "/patients", label: "Patient Review", icon: Users },
      { href: "/intake", label: "Batch Intake", icon: Inbox },
      { href: "/resources", label: "Resource Scenarios", icon: SlidersHorizontal },
      { href: "/evidence", label: "Trust Center", icon: ShieldCheck },
    ],
  },
  {
    label: "Reference",
    items: [{ href: "/methodology", label: "Methodology", icon: BookOpenCheck }],
  },
];

export function SideNavigation() {
  const pathname = usePathname();
  return (
    <nav aria-label="Primary navigation">
      {groups.map((group) => (
        <div className="nav-group" key={group.label}>
          <p className="nav-group-label">{group.label}</p>
          <div className="side-nav">
            {group.items.map(({ href, label, icon: Icon }) => {
              const active = pathname.startsWith(href);
              return (
                <Link
                  className="nav-item"
                  data-active={active}
                  href={href}
                  key={href}
                  aria-current={active ? "page" : undefined}
                >
                  <Icon aria-hidden="true" size={19} strokeWidth={1.9} />
                  <span>{label}</span>
                </Link>
              );
            })}
          </div>
        </div>
      ))}
    </nav>
  );
}

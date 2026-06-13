"use client";

import { Menu, X } from "lucide-react";
import { useState } from "react";

import { SideNavigation } from "@/components/shell/side-navigation";

export function MobileNavigation() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button
        className="mobile-menu-button"
        type="button"
        aria-label={open ? "Close navigation" : "Open navigation"}
        aria-expanded={open}
        onClick={() => setOpen((value) => !value)}
      >
        {open ? <X aria-hidden="true" /> : <Menu aria-hidden="true" />}
      </button>
      {open ? (
        <div className="mobile-nav-panel" onClick={() => setOpen(false)}>
          <SideNavigation />
        </div>
      ) : null}
    </>
  );
}

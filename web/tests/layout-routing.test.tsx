import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { PublicHeader } from "@/components/shell/public-header";
import { SideNavigation } from "@/components/shell/side-navigation";

vi.mock("next/navigation", () => ({
  usePathname: () => "/command-center",
}));

describe("public header", () => {
  it("exposes the public entry points and the command-center CTA", () => {
    render(<PublicHeader />);

    for (const label of ["Overview", "Guided demo", "Methodology"]) {
      expect(screen.getByRole("link", { name: label })).toBeVisible();
    }
    expect(
      screen.getByRole("link", { name: /Open command center/i }),
    ).toHaveAttribute("href", "/command-center");
  });

  it("does not render the operational sidebar", () => {
    render(<PublicHeader />);
    expect(
      screen.queryByRole("navigation", { name: "Primary navigation" }),
    ).toBeNull();
  });
});

describe("workspace sidebar", () => {
  it("treats /command-center as the active operational route", () => {
    render(<SideNavigation />);
    expect(
      screen.getByRole("link", { name: /Command Center/i }),
    ).toHaveAttribute("aria-current", "page");
  });
});

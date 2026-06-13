import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { SideNavigation } from "@/components/shell/side-navigation";

vi.mock("next/navigation", () => ({
  usePathname: () => "/resources",
}));

describe("side navigation", () => {
  it("marks the current workspace and exposes meaningful labels", () => {
    render(<SideNavigation />);

    expect(screen.getByRole("navigation", { name: "Primary navigation" })).toBeVisible();
    expect(screen.getByRole("link", { name: /Resource Allocation/i })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getByRole("link", { name: /Patient Intelligence/i })).not.toHaveAttribute(
      "aria-current",
    );
  });
});
